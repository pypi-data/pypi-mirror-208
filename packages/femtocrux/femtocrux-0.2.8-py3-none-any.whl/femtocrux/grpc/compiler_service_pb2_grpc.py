# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import compiler_service_pb2 as compiler__service__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class CompileStub(object):
    """Compiler service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.compile = channel.unary_unary(
                '/fscompiler.Compile/compile',
                request_serializer=compiler__service__pb2.model.SerializeToString,
                response_deserializer=compiler__service__pb2.compiled_artifacts.FromString,
                )
        self.ping = channel.unary_unary(
                '/fscompiler.Compile/ping',
                request_serializer=compiler__service__pb2.data.SerializeToString,
                response_deserializer=compiler__service__pb2.data.FromString,
                )
        self.simulate = channel.stream_stream(
                '/fscompiler.Compile/simulate',
                request_serializer=compiler__service__pb2.simulation_input.SerializeToString,
                response_deserializer=compiler__service__pb2.simulation_output.FromString,
                )
        self.version = channel.unary_unary(
                '/fscompiler.Compile/version',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=compiler__service__pb2.version_info.FromString,
                )


class CompileServicer(object):
    """Compiler service
    """

    def compile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def simulate(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def version(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CompileServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'compile': grpc.unary_unary_rpc_method_handler(
                    servicer.compile,
                    request_deserializer=compiler__service__pb2.model.FromString,
                    response_serializer=compiler__service__pb2.compiled_artifacts.SerializeToString,
            ),
            'ping': grpc.unary_unary_rpc_method_handler(
                    servicer.ping,
                    request_deserializer=compiler__service__pb2.data.FromString,
                    response_serializer=compiler__service__pb2.data.SerializeToString,
            ),
            'simulate': grpc.stream_stream_rpc_method_handler(
                    servicer.simulate,
                    request_deserializer=compiler__service__pb2.simulation_input.FromString,
                    response_serializer=compiler__service__pb2.simulation_output.SerializeToString,
            ),
            'version': grpc.unary_unary_rpc_method_handler(
                    servicer.version,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=compiler__service__pb2.version_info.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'fscompiler.Compile', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Compile(object):
    """Compiler service
    """

    @staticmethod
    def compile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fscompiler.Compile/compile',
            compiler__service__pb2.model.SerializeToString,
            compiler__service__pb2.compiled_artifacts.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fscompiler.Compile/ping',
            compiler__service__pb2.data.SerializeToString,
            compiler__service__pb2.data.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def simulate(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/fscompiler.Compile/simulate',
            compiler__service__pb2.simulation_input.SerializeToString,
            compiler__service__pb2.simulation_output.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def version(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fscompiler.Compile/version',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            compiler__service__pb2.version_info.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
