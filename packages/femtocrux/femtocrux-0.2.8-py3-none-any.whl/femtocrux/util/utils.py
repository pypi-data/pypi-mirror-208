""" Utils for client-server communication. """

import numpy as np
from typing import Any

import femtocrux.grpc.compiler_service_pb2 as cs_pb2
import femtocrux.grpc.compiler_service_pb2_grpc as cs_pb2_grpc

def numpy_to_ndarray(data: np.array) -> cs_pb2.ndarray:
    """ Convert a numpy array to an ndarray message. """
    return cs_pb2.ndarray(
        data = [float(x) for x in data.ravel()],
        shape = data.shape
    )

def ndarray_to_numpy(data: cs_pb2.ndarray) -> np.array:
    """ Convert an ndarray message to a numpy array. """
    return np.array(data.data).reshape(data.shape)

def field_or_none(message: Any, field_name: str) -> Any:
    """ Convert empty message fields to None. """
    return getattr(message, field_name) if message.HasField(field_name) else None

def get_channel_options(max_message_mb: int = 32):
    # Set the maximum message size
    megabyte_size = 2 ** 20
    max_message_size = max_message_mb * megabyte_size
    return [('grpc.max_send_message_length', max_message_size),
            ('grpc.max_receive_message_length', max_message_size)]

