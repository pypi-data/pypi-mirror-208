import argparse
from collections.abc import Iterable
import concurrent 
import google.protobuf
import grpc
import logging
import pickle
import sys
from typing import Dict

from femtostack.common import CompilerFrontend, SimIOWrapper, IOConfig
from femtostack.tflite_api.tflite_frontend import TFLiteCompiler
from femtostack.torch_api.frontend import TorchCompiler
from fmot.fqir import GraphProto

from femtocrux.server.exceptions import format_exception, format_exception_from_exc
from femtocrux.util.utils import numpy_to_ndarray, ndarray_to_numpy, field_or_none, get_channel_options

# Import GRPC artifacts
import femtocrux.grpc.compiler_service_pb2 as cs_pb2
import femtocrux.grpc.compiler_service_pb2_grpc as cs_pb2_grpc

# Network parameters
default_port = "50051"

class CompileServicer(cs_pb2_grpc.CompileServicer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize the log
        self.logger = logging.getLogger("CompileServicer")
        self.logger.setLevel(logging.DEBUG)
        self.logger.info('Starting compile server.')

    def __get_fqir_compiler__(self, model: cs_pb2.model) -> CompilerFrontend:
        """ Get a Torch compiler from an FQIR a model message """
        # Deserialize FQIR
        fqir = model.fqir
        graph_proto = pickle.loads(fqir.model)


        # Compile the FQIR
        return TorchCompiler(
            graph_proto, 
            batch_dim=field_or_none(fqir, 'batch_dim'),
            seq_dim=field_or_none(fqir, 'sequence_dim')
        )

    def __get_tflite_compiler__(self, model: cs_pb2.model) -> CompilerFrontend:
        """ Get a TFLite compiler from a model message """
        tflite = model.tflite
        return TFLiteCompiler(
            tflite.model, 
            signature=field_or_none(tflite, 'signature_name') 
        )

    def __compile_model__(self, model: cs_pb2.model, context) -> CompilerFrontend:
        """ Compile a model, for simulation or bitfile generation. """
        # Get a compiler for the model
        model_type_map = {
            'fqir': self.__get_fqir_compiler__,
            'tflite': self.__get_tflite_compiler__
        }
        model_type = model.WhichOneof('ir')
        compiler = model_type_map[model_type](model)

        # Get the compiler options
        options_struct = field_or_none(model, 'options')
        if options_struct is None:
            options = {}
        else: 
            options = google.protobuf.json_format.MessageToDict(options_struct)

        # Compile the model
        compiler.compile(options = options) 
        assert compiler.is_compiled, "Expected compilation completed"
        return compiler

    def compile(self, model, context):
        """ Compile a model into a bitfile. """

        self.logger.debug('Received \'compile\' request.')

        # Compile the model
        try:
            compiler = self.__compile_model__(model, context)
            bitfile = compiler.dump_bitfile(encrypt=True)
        except Exception as exc:
            msg = "Compiler raised exception:\n%s" % (
                format_exception_from_exc(exc)
            )
            self.logger.error(msg)
            return cs_pb2.compiled_artifacts( 
                status = cs_pb2.status(
                    success=False, 
                    msg=msg
                )
            )

        # Return the bitfile
        return cs_pb2.compiled_artifacts( 
            bitfile = bitfile,
            status = cs_pb2.status(
                success=True
            )
        )

    def ping(self, data: cs_pb2.data, context) -> cs_pb2.data:
        """ Round-trip a message. """
        return data

    def simulate(self, 
        request_iterator: Iterable[cs_pb2.simulation_input], 
        context
        ) -> Iterable[cs_pb2.simulation_output]:
        """ Simulate the SPU's behavior on a given model. """
        self.logger.debug('Received \'simulate\' request.')

        # The first request compiles the model
        for model_request in request_iterator:
            # Check that this is a model request
            if not model_request.WhichOneof('model_or_data') == 'model':
                yield cs_pb2.simulation_output(
                    status = cs_pb2.status(
                        success = False,
                        msg = "Expected model message."
                    )
                )
                continue

            # Attempt compilation
            try:
                compiler = self.__compile_model__(model_request.model, context)
            except Exception as exc:
                msg = "Compiler raised exception:\n%s" % (
                    format_exception_from_exc(exc)
                )
                self.logger.error(msg)
                yield cs_pb2.simulation_output( 
                    status = cs_pb2.status(
                        success=False, 
                        msg=msg
                    )
                )
                continue

            # If successful, move on to data requests
            yield cs_pb2.simulation_output(
                status=cs_pb2.status(
                    success = True
                )
            )
            break

        # Subsequent requests must be data
        for data_request in request_iterator:

            # Check that this is a data message
            if not data_request.WhichOneof('model_or_data') == 'data':
                yield cs_pb2.simulation_output(
                    status = cs_pb2.status(
                        success = False,
                        msg = "Expected data message."
                    )
                )
                continue

            # Convert input data
            sim_data = data_request.data
            data = [ndarray_to_numpy(x) for x in sim_data.data]
            assert len(data) == 1, "Behavioral sim currently only supports 1 input" #FIXME
            data = data[0]
    
            sim_duration = None if sim_data.sim_duration == -1 else sim_data.sim_duration

            # Simulate the model
            try:
                outputs, metrics = compiler.run_behavioral_simulator(
                    data,
                    quantize_inputs = sim_data.quantize_inputs,
                    dequantize_outputs = sim_data.dequantize_outputs,
                    input_period = field_or_none(sim_data, 'sim_duration')
                )
            except Exception as exc:
                msg = "Simulator raised exception:\n%s" % (
                    format_exception_from_exc(exc)
                )
                self.logger.error(msg)
                yield cs_pb2.simulation_output(
                    status = cs_pb2.status(
                        success = False,
                        msg = msg
                    )
                )
                continue

            # Respond with output data
            yield cs_pb2.simulation_output(
                data = [numpy_to_ndarray(x) for x in outputs],
                report = metrics.performance_report(),
                status = cs_pb2.status(success=True)
            )

    def version(self, empty, context) -> cs_pb2.version_info:
        """ Return the version of femtocrux running in this server. """
        from femtocrux.version import __version__
        return cs_pb2.version_info(version = __version__)

def handle_exception(type, value, tb):
    """Log an uncaught exception before terminating."""
    logger.error("Server raised uncaught exception:\n")
    logger.error(format_exception(type, value, tb))

    # Call the default excepthook to terminate the progarm
    sys.__excepthook__(type, value, tb)

def serve():
    """ 
    Starts the server and blocks the thread, waiting for connections. 
    """
    # Set up logs
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    sys.excepthook = handle_exception

    # Parse arguments
    parser = argparse.ArgumentParser(description='Configures the gRPC server.')
    parser.add_argument(
        '--port', 
        dest="port", 
        default=default_port,
        help="the port used for RPCs (default: %s)" % default_port
    )
    args = parser.parse_args()

    # Start the server
    server = grpc.server(
        concurrent.futures.ThreadPoolExecutor(max_workers=10),
        options = get_channel_options()
    )

    cs_pb2_grpc.add_CompileServicer_to_server(CompileServicer(), server)
    server.add_insecure_port("[::]:%s" % args.port)
    server.start()
    logging.info("Server listening on port %s" % args.port)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
