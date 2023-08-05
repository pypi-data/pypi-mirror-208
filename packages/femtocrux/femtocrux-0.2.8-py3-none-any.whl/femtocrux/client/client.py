from collections.abc import Iterable
from dataclasses import dataclass
import docker
from enum import Enum
from getpass import getpass
import google.protobuf
import grpc
import logging
import numpy as np
import os
import platform
import pickle
import queue
import socket
import sys
import time
from typing import Any, List, Tuple, Union

from fmot.fqir import GraphProto

from femtocrux.util.utils import numpy_to_ndarray, ndarray_to_numpy, get_channel_options

# GRPC artifacts
import femtocrux.grpc.compiler_service_pb2 as cs_pb2
import femtocrux.grpc.compiler_service_pb2_grpc as cs_pb2_grpc

# Docker info
__docker_registry__ = "ghcr.io"

def __get_docker_image_name__() -> str:
    """
    Returns the docker image name. For testing, override with the
    FEMTOCRUX_SERVER_IMAGE_NAME environment variable.
    """
    try:
        return os.environ["FEMTOCRUX_SERVER_IMAGE_NAME"]
    except KeyError:
        from femtocrux.version import __version__
        ORG = "femtosense"
        IMAGE = "femtocrux"
        remote_image_name = "%s/%s/%s:%s" % (
            __docker_registry__, 
            ORG, 
            IMAGE, 
            __version__
        )
        return remote_image_name

__docker_image_name__ = __get_docker_image_name__()

# Set up logging
def __init_logger__():
    """ Init a basic logger to stderr. """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = __init_logger__()

def __env_var_to_bool__(varname: str, default: bool = False) -> bool:
    """ Parse an environment varaible as a boolean. """
    try:
        value = os.environ[varname]
    except KeyError:
        return default

    value_lower = value.lower()
    if value_lower in {'yes', '1', 'true'}:
        return True
    elif value_lower in {'no', '0', 'false'}:
        return False
    else:
        raise OSError("Failed to parse value of environment variable %s: '%s'" % (
            varname, value
            )
        )

class Model:
    """ 
    Base class wrapping any model to be compiled by femtocrux. Should not be instantiated directly. Instead, use one of its child classes like :class:`~femtocrux.client.client.FQIRModel` or :class:`~femtocrux.client.client.TFLiteModel`.
    """
    def __get_message__(self, options: dict = {}) -> cs_pb2.model:
        # Format the options
        options_struct = google.protobuf.struct_pb2.Struct()
        options_struct.update(options)

        # Construct the model with IR
        return cs_pb2.model(
            **{self.__ir_name__: self.__get_ir__()},
            options = options_struct
        )

    @property
    def __ir_name__(self) -> str:
        """
            Subclass overrides this to tell which 'ir' field is being returned.
        """
        return NotImplementedError("Subclass must override with IR type.")


    def __get_ir__(self) -> Tuple[str, Any]:
        """
            Subclass overrides this to implement the 'ir' field of the model's 
            grpc message.
        """
        raise NotImplementedError("Must be defined by subclass")

@dataclass
class FQIRModel(Model):
    """
        Wraps an FQIR model to be compiled by femtocrux.

        :type graph_proto: fmot.fqir.GraphProto, required
        :param graph_proto: The traced FQIR model.

        :type batch_dim: int, optional
        :param batch_dim: The batch dimension to be squeezed from all inputs.

        :type sequence_dim: int, optional
        :param sequence_dim: The sequence dimension to squeezed from all inputs.
    """

    graph_proto: GraphProto = None
    batch_dim: int = None
    sequence_dim: int = None

    @property
    def __ir_name__(self) -> str:
        return 'fqir'

    def __get_ir__(self) -> Any:
        # Serialize FQIR via pickle
        model = pickle.dumps(self.graph_proto)

        # Send the serialized model
        return cs_pb2.fqir(
            model = model,
            batch_dim = self.batch_dim,
            sequence_dim = self.sequence_dim,
        )

@dataclass
class TFLiteModel(Model):
    """
        Wraps a TFLite model to be compiled by femtocrux.

        :type flatbuffer: bytes, required
        :param flatbuffer: The TFLite flatbuffer to be compiled.

        :type signature_name: str, optional
        :param signature_name: The name of the TFLite IO signature to be used for input / output metadata. Must be provided if the model contains multiple signatures.
    """

    flatbuffer: bytes = None
    signature_name: str = None

    @property
    def __ir_name__(self) -> str:
        return 'tflite'

    def __get_ir__(self) -> Any:
        return cs_pb2.tflite(
            model = self.flatbuffer,
            signature_name = self.signature_name
        )

class Simulator():
    """
        Simulates a compiled model's behavior on the SPU.
    """
    def __init__(self, client: "CompilerClient", model: Model, 
        options: dict = {}):
        self.client = client
        self.model = model

        # Create an event stream fed by a queue
        self.request_queue = queue.SimpleQueue()
        request_iterator = iter(
            self.request_queue.get, 
            self.__request_sentinel__
        ) 
        self.response_iterator = client.__simulate__(request_iterator)

        # Compile the model with the first message
        model_msg = model.__get_message__(options)
        simulation_start_msg = cs_pb2.simulation_input(
            model = model_msg
        )
        self.__send_request__(simulation_start_msg)

        # Check compilation status
        self.__get_response__()

    def __del__(self):
        """ Close any open streams. """
        self.__send_request__(self.__request_sentinel__)

    def __send_request__(self, msg):
        self.request_queue.put(msg)

    def __get_response__(self):
        response = next(self.response_iterator)
        self.client.__check_status__(response.status)
        return response

    @property
    def __request_sentinel__(self) -> Any:
        """ Sentinel value to close the request queue. """
        return None

    def simulate(self, inputs: Union[np.array, Iterable[np.array]], quantize_inputs: bool = False, dequantize_outputs: bool = False, sim_duration: float = None) -> List[np.array]:
        """ 
        Simulates the model on the given inputs. 

        :type inputs: array or iterable of arrays, required
        :param inputs: The input tensors.

        :type quantize_inputs: bool, optional
        :param quantize_inputs: If true, quantizes each input from float to integer using its scale :math:`a` and zero point :math:`z`, according to the formula
        .. math::
            f(x) = a (x - z)

        :type dequantize_outputs: bool, optional
        :param dequantize_outputs: If true, dequantizes each output from integer to float using its scale :math:`a` and zero point :math:`z`, according to the formula
        .. math::
            g(x) = \\frac{x}{a} + z.

        :param sim_duration: The total simulation time, in seconds. Used to estimate static power consumption. For example, in a streaming model, this should be the time elapsed between model invocations. By default, this is just the estimated latency of the model.
        :type sim_duration: float, optional
        
        :rtype: list
        :return: The output tensors.

        """
        #TODO how to handle multiple inputs? What's the proper form for FASMIR? Map inputs to FASMIR indices as in CompilerFrontend?        
        # Convert a single ndarray to a list containing that input.
        # Otherwise, this will be interpreted as an iterable of (n-1)-d arrays 
        if isinstance(inputs, np.ndarray):
            inputs = [inputs]

        simulation_request = cs_pb2.simulation_input(
            data = cs_pb2.simulation_data(
                data = [numpy_to_ndarray(x) for x in inputs],
                quantize_inputs = quantize_inputs,
                dequantize_outputs = dequantize_outputs,
                sim_duration = sim_duration
            )
        )
        self.__send_request__(simulation_request)
        response = self.__get_response__()

        return [ndarray_to_numpy(x) for x in response.data], response.report

class CompilerClientImpl:
    """ 
    Internal implementation of CompilerClient, with extra testing options. 

    Allows substituting your own gRPC channel and stub.
    """
    def __init__(self, channel, stub):
        self.channel = channel
        self.stub = stub
        self.__check_version__()

    def __check_status__(self, status):
        """ Check a status response, raising an exception if unsuccessful. """
        if not status.success:
            raise RuntimeError("Client received error from compiler server:\n%s" % status.msg)

    def __check_version__(self):
        """ Verify the server's version matches the client. """
        from femtocrux.version import __version__ as client_version
        server_version = self.__server_version__()
        assert client_version == server_version, """
        Client-server version mismatch:
            client: %s
            server: %s
        """ % (client_version, server_version)

    def compile(self, model: Model, options: dict = {}) -> bytes: 
        """ 
        Compile the model to a bitstream. 

        :type model: Model, required
        :param model: The model to be compiled.

        :type options: dict, optional 
        :param options: Complier options.

        :rtype: bytes
        :return: A zip archive of compiler artifacts.
        """
        response = self.stub.compile(model.__get_message__(options))
        self.__check_status__(response.status)
        return response.bitfile

    def __ping__(self, message: bytes) -> None:
        """ Pings the server with a message. """
        response = self.stub.ping(cs_pb2.data(data=message))
        if response.data != message:
            raise RuntimeError("Server response does not match request data!")

    def __simulate__(self, in_stream: Iterable) -> Iterable:
        """ Calls the 'simulator' bidirectional streaming RPC. """
        return self.stub.simulate(in_stream)

    def simulate(self, model: Model, options: dict = {}) -> Simulator:
        """ 
        Get a simulator for the model. 

        :type model: Model, required
        :param model: The model to be simulated.

        :type options: dict, optional
        :param options: Compiler options.

        :rtype: Simulator
        :return: A simulator for the model.
        """
        return Simulator(client=self, model=model, options=options)

    def __server_version__(self) -> str:
        """ Queries the femtocrux version running on the server. """
        response = self.stub.version(google.protobuf.empty_pb2.Empty())
        return response.version

class CompilerClient(CompilerClientImpl):
    """
    Client which spawns and interacts with the compiler server. This is the main entrypoint for femtocrux.
    """
    def __init__(self):
        self.container = None

        # Start a new docker server
        self.container = self.__create_docker_server__()
        self.__wait_for_server_ready__()
        self.__init_channel_info__(self.container)

        # Establish a connection to the server
        self.channel = self.__connect__()

        # Initialize the client on this channel
        self.stub = cs_pb2_grpc.CompileStub(self.channel)
        super().__init__(self.channel, self.stub)

    def __del__(self):
        """ Reclaim system resources. """
        if self.container is not None:
            self.container.kill()
            self.container = None

    def __get_docker_api_client__(self):
        """ Get a client to the Docker daemon. """
        try:
            return docker.from_env()
        except Exception as exc:
            raise RuntimeError("""Failed to connect to the Docker daemon. 
                    Please ensure it is installed and running.""") from exc

    def __init_channel_info__(self, container):
        """
        For local connections only.

        Gets the IP address and port of the container.
        """
        self.__channel_port__ = self.__container_port__

        # Platform network defaults
        sys_name = platform.system()
        try:
            network_name = {
                'Linux': 'bridge',
                'Darwin': 'bridge',
                'Windows': 'nat'
            }[sys_name]
        except KeyError:
            raise NotImplementedError("Unsupported platform: %s" % sys_name)

        # Get the network info
        client = self.__get_docker_api_client__()
        network = client.networks.get(network_name)

        # Search for this container in the network
        network_containers = network.attrs['Containers']
        try:
            container_info = network_containers[container.id]
        except KeyError:
            raise OSError(
                """Failed to find container '%s' on network '%s'.
                Found options:
                    %s""" % (
                container.id, network_name, container_info
                )
            )

        # Extract the IP address of this container
        container_ip = container_info['IPv4Address'].split('/')[0]
        self.__channel_addr__ = container_ip

    def __connect__(self) -> Any:
        """ Establishes a gRPC connection to the server. """

        # Open a gRPC channel to the server 
        sock_name = '%s:%s' % (self.channel_addr, self.channel_port)
        channel = grpc.insecure_channel(
            sock_name,
            options = get_channel_options(),
        )
        logger.info("Created gRPC channel at %s" % sock_name)

        # Wait for the channel to be ready
        channel_timeout_seconds = 30
        channel_ready = grpc.channel_ready_future(channel)
        logger.info("Waiting to establish a connection...")
        try:
            channel_ready.result(timeout=channel_timeout_seconds)
        except grpc.FutureTimeoutError as exc:
            raise OSError("Channel timed out after %s seconds. Check that the server is running." % channel_timeout_seconds) from exc
        logger.info("Connection successful.")

        return channel

    @property
    def channel_addr(self) -> str:
        """ IP address used for the gRPC channel. """
        return self.__channel_addr__

    @property
    def channel_port(self) -> int:
        """
        Port used for the gRPC channel.
        """
        return self.__channel_port__

    @property
    def __container_port__(self) -> int:
        """ Port used inside the container. """
        return 50051

    @property
    def __container_label__(self) -> str:
        """ Label attached to identify containers started by this client. """
        return 'femtocrux_server'

    def __get_unused_container_name__(self) -> str:
        """ Get an unused container name. """
        basename = 'femtocrux_server_'

        # Search for an unused name
        client = self.__get_docker_api_client__()
        container_idx = 0
        while True:
            name = 'femtocrux_server_%d' % container_idx
            try:
                client.containers.get(name)
            except docker.errors.NotFound:
                # If no collision, use this name
                return name

            container_idx += 1

    def __pull_docker_image__(self):
        """ Pull the Docker image from remote. """

        logger.info(
            """
            Attempting to pull docker image from remote.

            Alternatively, you can pull the image yourself with the command:
                docker pull %s
            """, 
            __docker_image_name__
        )
  
        # Log in to Github
        client = self.__get_docker_api_client__()
        while True:
            # Get the password
            manual_pass = True
            if "GH_PACKAGE_KEY" in os.environ:
                password = os.environ["GH_PACKAGE_KEY"]
                manual_pass = False
            else:
                # Prompt the user for password entry
                password = getpass("Please enter your Femtosense-provided key:")

            # Log in to the client
            try:
                resp = client.login("femtodaemon", password, registry="https://" + get_docker_registry())
            except docker.errors.APIError as exc:
                if 'denied' in exc.explanation:
                    logger.error("Docker authetication failed.")
                    # Retry password entry
                    if manual_pass:
                        continue

                raise RuntimeError("Docker authentication failed") from exc

            # Login successful
            logger.info(resp['Status'])
            break

        def image_not_found_error() -> RuntimeError:
            """ Return an exception saying the image wasn't found. """
            return RuntimeError(
            """Docker image not found:
                %s
            Please notify your Femtosense representative.""" % (
                __docker_image_name__
                )
            )

        # Download the image
        logger.info("Downloading image. This could take a few minutes...")
        try:
            image = client.images.pull(__docker_image_name__)
        except docker.errors.ImageNotFound as exc:
            raise image_not_found_error() from exc
        except docker.errors.APIError as exc:
            if exc.explanation == "manifest unknown":
                logger.error(
                    "Docker image %s not found on the remote. Check if it is published.", 
                    __docker_image_name__
                )
            raise image_not_found_error() from exc

        logger.info("Download completed.")

    def __create_docker_server__(self) -> docker.models.containers.Container:
        """
        Starts the server in a new Docker container.
        """
        # Get a client for the Docker daemon
        client = self.__get_docker_api_client__()

        # Pull the image, if not available
        existing_image_names = [tag for image in client.images.list() for tag in image.tags]
        if __docker_image_name__ not in existing_image_names:
            # Check if we are allowed to pull the image.
            # This is disabled for CI builds.
            image_not_found_msg = 'Failed to find the docker image %s locally.' % __docker_image_name__
            if not __env_var_to_bool__("FS_ALLOW_DOCKER_PULL", default=True):
                raise RuntimeError(
                    """
                    %s 
                    Docker pull is disabled by the environment.
                    """ %
                    image_not_found_msg
                )

            # Pull the image from remote
            logger.info(image_not_found_msg)    
            self.__pull_docker_image__()

        # Start a container running the server
        command = "--port %s" % self.__container_port__
        container = client.containers.run(
            __docker_image_name__,
            command=command, # Appends entrypoint with args 
            detach=True,
            labels=[self.__container_label__],
            stderr=True,
            stdout=True,
            name=self.__get_unused_container_name__(),
            auto_remove=True,
        )

        return container

    def __wait_for_server_ready__(self):
        """
        Block until the Docker container is ready to handle requests.
        """

        container = self.container

        # Block until the container starts
        num_attempts = 5
        wait_interval = 1.0 # Seconds
        print('Checking container status...')
        for attempt in range(num_attempts):
            container.reload()
            status = container.status
            if status == 'created':
                # Sleep and try again
                print('Container starting up. Retrying in %fs...' % wait_interval)
                time.sleep(wait_interval)
                continue
            elif status == 'running':
                print('Container started successfully.')
                break
            elif status == 'exited':
                raise RuntimeError("Container exited! See logs:\n%d" % container.logs())
            else:
                raise RuntimeError("Unrecognized docker container status: %d" % status)

        # Check the final status
        container.reload()
        if container.status != 'running':
            raise RuntimeError("Container failed to start after %d attempts" % num_attempts)

        # Check the container's health
        for attempt in range(num_attempts):
            exit_code, output = container.exec_run('python3 /femtocrux/femtocrux/server/healthcheck.py')

            if exit_code == 0:
                print('Container passed health check.')
                break

            time.sleep(wait_interval)

        # Check the last return code
        if exit_code != 0:
            raise RuntimeError(
                "Docker container failed %d health check(s)!\nLast output:\n%s" % (
                    num_attempts, output.decode('utf-8')
                )
            )

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    client = CompilerClient()
    logger.info('Client started successfully.')
