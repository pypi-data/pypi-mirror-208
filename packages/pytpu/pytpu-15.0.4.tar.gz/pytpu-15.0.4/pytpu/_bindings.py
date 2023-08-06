from __future__ import annotations

__all__ = [
    'Device',
    'Program',
    'Inference',
    'InferenceError',
]

import collections.abc
import contextlib
import zipfile
import json
import os
import re
from ctypes import (CDLL, c_char, c_char_p, c_int, c_void_p, c_uint8, c_size_t, c_bool, cast,
                    POINTER, CFUNCTYPE, Structure)
from enum import Enum
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Mapping
from typing import Optional

import numpy as np

_LIB_TPU_SO_PATH = '/usr/lib/libtpu.2.so'


# libtpu = CDLL('libtpu-experimental/build/libtpu.so')
# libtpu = CDLL('/home/d.baburin/iva_tpu_sdk/libtpu.2/build/libtpu.2.so')


class _LibTPUBinder:
    """This class lazy binds to libtpu *.so file thus allowing module to be imported without *.so file"""

    def __init__(self):
        self._libtpu: Optional[CDLL] = None

    @property
    def libtpu(self) -> CDLL:
        if self._libtpu is None:
            self._bind()

        assert self._libtpu is not None

        return self._libtpu

    def _bind(self) -> None:
        libtpu = CDLL(_LIB_TPU_SO_PATH)

        _cb_pointer = CFUNCTYPE(None, POINTER(Inference), c_int, c_void_p)

        # Device
        libtpu.tpu_create_device.restype = POINTER(Device)
        # libtpu.tpu_create_device.argtypes = [c_int]
        libtpu.tpu_create_device.argtypes = [c_char_p]

        libtpu.tpu_destroy_device.restype = c_void_p
        libtpu.tpu_destroy_device.argtypes = [POINTER(Device)]

        libtpu.tpu_is_device_valid.restype = c_int
        libtpu.tpu_is_device_valid.argtypes = [POINTER(Device)]

        libtpu.tpu_init_device.restype = c_int
        libtpu.tpu_init_device.argtypes = [POINTER(Device)]

        libtpu.tpu_get_device_error_message.restype = c_char_p
        libtpu.tpu_get_device_error_message.argtypes = [POINTER(Device)]

        libtpu.tpu_get_device_info.restype = c_char_p
        libtpu.tpu_get_device_info.argtypes = [POINTER(Device)]

        libtpu.tpu_load_program.restype = c_int
        libtpu.tpu_load_program.argtypes = [POINTER(Device), POINTER(Program)]

        libtpu.tpu_run_inference.restype = c_int
        libtpu.tpu_run_inference.argtypes = [POINTER(Device), POINTER(Inference), c_int]

        libtpu.tpu_submit_inference.restype = c_int
        libtpu.tpu_submit_inference.argtypes = [POINTER(Device), POINTER(Inference), c_int, _cb_pointer, c_void_p]

        # Program
        libtpu.tpu_create_program.restype = POINTER(Program)
        libtpu.tpu_create_program.argtypes = [POINTER(c_char), c_int]

        libtpu.tpu_destroy_program.restype = c_void_p
        libtpu.tpu_destroy_program.argtypes = [POINTER(Program)]

        libtpu.tpu_is_program_valid.restype = c_int
        libtpu.tpu_is_program_valid.argtypes = [POINTER(Program)]

        libtpu.tpu_get_program_info.restype = c_char_p
        libtpu.tpu_get_program_info.argtypes = [POINTER(Program)]

        libtpu.tpu_get_program_error_message.restype = c_char_p
        libtpu.tpu_get_program_error_message.argtypes = [POINTER(Program)]

        libtpu.tpu_get_batch_size.restype = c_size_t
        libtpu.tpu_get_batch_size.argtypes = [POINTER(Program)]

        libtpu.tpu_get_input_count.restype = c_size_t
        libtpu.tpu_get_input_count.argtypes = [POINTER(Program)]

        libtpu.tpu_get_input_size.restype = c_size_t
        libtpu.tpu_get_input_size.argtypes = [POINTER(Program), c_size_t, c_bool]

        libtpu.tpu_get_output_count.restype = c_size_t
        libtpu.tpu_get_output_count.argtypes = [POINTER(Program)]

        libtpu.tpu_get_output_size.restype = c_size_t
        libtpu.tpu_get_output_size.argtypes = [POINTER(Program), c_size_t, c_bool]

        # _TensorBufferObject
        libtpu.tpu_create_tensor_buffer_object.restype = POINTER(_TensorBufferObject)
        libtpu.tpu_create_tensor_buffer_object.argtypes = [POINTER(Program), c_int]

        libtpu.tpu_destroy_tensor_buffer_object.restype = c_void_p
        libtpu.tpu_destroy_tensor_buffer_object.argtypes = [POINTER(_TensorBufferObject)]

        libtpu.tpu_process_tensor_buffers.restype = c_void_p
        libtpu.tpu_process_tensor_buffers.argtypes = [POINTER(_TensorBufferObject)]

        libtpu.tpu_get_tensor_buffer_ptr.restype = POINTER(c_uint8)
        libtpu.tpu_get_tensor_buffer_ptr.argtypes = [POINTER(_TensorBufferObject), c_size_t, c_bool]

        libtpu.tpu_set_user_tensor_buffer_ptr.restype = POINTER(c_uint8)
        libtpu.tpu_set_user_tensor_buffer_ptr.argtypes = [POINTER(_TensorBufferObject), c_size_t, POINTER(c_uint8)]

        # Inference
        libtpu.tpu_create_inference.restype = POINTER(Inference)
        libtpu.tpu_create_inference.argtypes = [POINTER(Program)]

        libtpu.tpu_destroy_inference.restype = c_void_p
        libtpu.tpu_destroy_inference.argtypes = [POINTER(Inference)]

        libtpu.tpu_get_inference_program.restype = POINTER(Program)
        libtpu.tpu_get_inference_program.argtypes = [POINTER(Inference)]

        libtpu.tpu_get_inference_inputs.restype = POINTER(_TensorBufferObject)
        libtpu.tpu_get_inference_inputs.argtypes = [POINTER(Inference)]

        libtpu.tpu_set_inference_inputs.restype = POINTER(_TensorBufferObject)
        libtpu.tpu_set_inference_inputs.argtypes = [POINTER(Inference), POINTER(_TensorBufferObject)]

        libtpu.tpu_get_inference_outputs.restype = POINTER(_TensorBufferObject)
        libtpu.tpu_get_inference_outputs.argtypes = [POINTER(Inference)]

        libtpu.tpu_set_inference_outputs.restype = POINTER(_TensorBufferObject)
        libtpu.tpu_set_inference_outputs.argtypes = [POINTER(Inference), POINTER(_TensorBufferObject)]

        libtpu.tpu_get_inference_status.restype = c_int
        libtpu.tpu_get_inference_status.argtypes = [POINTER(Inference)]

        libtpu.tpu_get_inference_error_message.restype = c_char_p
        libtpu.tpu_get_inference_error_message.argtypes = [POINTER(Inference)]

        self._libtpu = libtpu


_LIB_TPU_BINDER = _LibTPUBinder()


class ProcessingMode(Enum):
    RAW = 0
    PRE_PROCESS = 1
    POST_PROCESS = 2
    FULL = 3


class _TensorBufferType(Enum):
    INPUTS = 0
    OUTPUTS = 1


_Pointer = Any


class Device(Structure):
    _fields_ = []

    @staticmethod
    @contextlib.contextmanager
    def open(dev_name: str) -> Generator[Device, None, None]:
        if not isinstance(dev_name, str):
            raise ValueError(f'Device name must be a string: {type(dev_name)}')

        pointer = _LIB_TPU_BINDER.libtpu.tpu_create_device(c_char_p(dev_name.encode('utf-8')))
        device = Device(pointer)

        yield device
        _LIB_TPU_BINDER.libtpu.tpu_destroy_device(pointer)

    @staticmethod
    def list_devices() -> List[str]:
        # TODO: check why len(f) == 4?
        return [os.path.join('/dev', f) for f in os.listdir('/dev') if re.match(r'tpu.', f) and len(f) == 4]

    def __init__(self, pointer: _Pointer) -> None:

        super().__init__()

        self._pointer = pointer

        init_code = _LIB_TPU_BINDER.libtpu.tpu_init_device(pointer)
        if init_code != 0:
            raise ValueError(f'Invalid init code {init_code}: {self._get_error_message()}')

        if not _LIB_TPU_BINDER.libtpu.tpu_is_device_valid(self._pointer):
            raise ValueError(f'Invalid device: {self._get_error_message()}')

    def _get_error_message(self) -> str:
        msg = _LIB_TPU_BINDER.libtpu.tpu_get_device_error_message(self._pointer)
        return msg.decode('utf-8')

    # TODO: user https://mypy.readthedocs.io/en/latest/more_types.html#typeddict ?
    def info(self) -> Dict:
        return json.loads(_LIB_TPU_BINDER.libtpu.tpu_get_device_info(self._pointer).decode('utf-8'))

    def close(self) -> None:
        _LIB_TPU_BINDER.libtpu.tpu_destroy_device(self._pointer)

    @contextlib.contextmanager
    def load(self, program_path: str) -> Generator[Program, None, None]:
        is_raw = _is_raw_program(program_path)

        if not isinstance(program_path, str):
            raise ValueError(f'Program path must be a string: {type(program_path)}')

        program_pointer = _LIB_TPU_BINDER.libtpu.tpu_create_program(c_char_p(program_path.encode('utf-8')), is_raw)
        program = Program(self, program_pointer, is_raw)
        _LIB_TPU_BINDER.libtpu.tpu_load_program(self._pointer, program_pointer)

        yield program
        _LIB_TPU_BINDER.libtpu.tpu_destroy_program(program_pointer)


class _TensorBufferObject(Structure):
    _fields_ = []

    def __init__(self, pointer: _Pointer) -> None:
        super().__init__()
        self._pointer = pointer

    def set_user_tensor_buffer_ptr(self, n: int, ptr: _Pointer) -> _Pointer:
        return _LIB_TPU_BINDER.libtpu.tpu_set_user_tensor_buffer_ptr(self._pointer, c_size_t(n), ptr)


class Program(Structure):
    _fields_ = []

    def __init__(self, device: Device, pointer: _Pointer, is_raw: bool = False) -> None:
        super().__init__()

        self._device = device
        self._pointer = pointer
        self._is_raw = is_raw

        # Check status
        if not _LIB_TPU_BINDER.libtpu.tpu_is_program_valid(self._pointer):
            msg = _LIB_TPU_BINDER.libtpu.tpu_get_program_error_message(self._pointer)
            raise ValueError('Invalid program: ' + str(msg.decode('utf-8')))

        # Preload metadata
        metadata = self.info()
        self._input_metadata = metadata['inputs']['1']
        self._output_metadata = metadata['outputs']['2']
        self._hardware_parameters_metadata = metadata['hardware_parameters']

    # TODO: Use https://mypy.readthedocs.io/en/latest/more_types.html#typeddict here?
    def info(self) -> Dict:
        return json.loads(_LIB_TPU_BINDER.libtpu.tpu_get_program_info(self._pointer).decode('utf-8'))

    def get_input_size(self, n: int, is_raw: bool) -> int:
        return _LIB_TPU_BINDER.libtpu.tpu_get_input_size(self._pointer, c_size_t(n), c_bool(is_raw))

    def get_output_size(self, n: int, is_raw: bool) -> int:
        return _LIB_TPU_BINDER.libtpu.tpu_get_output_size(self._pointer, c_size_t(n), c_bool(is_raw))

    def close(self) -> None:
        _LIB_TPU_BINDER.libtpu.tpu_destroy_program(self._pointer)

    @contextlib.contextmanager
    def inference(self) -> Generator[Inference, None, None]:
        inference = Inference(self)
        yield inference
        inference.close()

    @contextlib.contextmanager
    def buffer(self, type_: _TensorBufferType) -> Generator[_TensorBufferObject, None, None]:
        buffer_pointer = _LIB_TPU_BINDER.libtpu.tpu_create_tensor_buffer_object(self._pointer,
                                                                                type_.value)  # make pointer
        yield _TensorBufferObject(buffer_pointer)
        _LIB_TPU_BINDER.libtpu.tpu_destroy_tensor_buffer_object(buffer_pointer)  # destroy pointer


CTX = Any


class InferenceError(ValueError):
    """Exception raised if libtpu reports inference as invalid"""


class Inference(Structure):
    _fields_ = []

    def __init__(self, program: Program):
        super().__init__()
        self._program = program
        self._pointer = _LIB_TPU_BINDER.libtpu.tpu_create_inference(program._pointer)

        # Explicitly order inputs and outputs:
        _input_tensor_name_to_input_tensor_index = {
            tensor_name: i
            for i, tensor_name in enumerate(program._input_metadata)
        }

        _output_tensor_name_to_output_tensor_index = {
            tensor_name: i
            for i, tensor_name in enumerate(program._output_metadata)
        }

        self._tensor_name_to_tensor_index: Dict[str, int] = dict()
        self._tensor_name_to_tensor_index.update(_input_tensor_name_to_input_tensor_index)
        self._tensor_name_to_tensor_index.update(_output_tensor_name_to_output_tensor_index)

        # Precalculate sizes:
        _input_sizes = {
            tensor_name: program.get_input_size(self._tensor_name_to_tensor_index[tensor_name], self._program._is_raw)
            for tensor_name in program._input_metadata
        }

        _output_sizes = {
            tensor_name: program.get_output_size(self._tensor_name_to_tensor_index[tensor_name], self._program._is_raw)
            for tensor_name in program._output_metadata
        }

        self._tensor_name_to_tensor_size: Dict[str, int] = dict()
        self._tensor_name_to_tensor_size.update(_input_sizes)
        self._tensor_name_to_tensor_size.update(_output_sizes)

    def _run(self, mode: ProcessingMode) -> None:
        status_code = _LIB_TPU_BINDER.libtpu.tpu_run_inference(
            self._program._device._pointer,  # device pointer
            self._pointer,  # inference pointer
            mode.value,  # pass numerical value of processing mode
        )

        if status_code != 0:
            msg = self._get_error_message()
            raise InferenceError(f'Invalid tpu_run_inference return code {status_code}: {msg}')

    def _get_error_message(self) -> str:
        return _LIB_TPU_BINDER.libtpu.tpu_get_inference_error_message(self._pointer).decode('utf-8')

    def sync(self, inputs, mode: ProcessingMode = ProcessingMode.FULL) -> Dict[str, np.ndarray]:

        with contextlib.ExitStack() as buffer_exit_stack:
            # Reserve pointers for input and output buffers:
            tpu_input_buf = buffer_exit_stack.enter_context(self._program.buffer(_TensorBufferType.INPUTS))
            tpu_output_buf = buffer_exit_stack.enter_context(self._program.buffer(_TensorBufferType.OUTPUTS))

            # Load
            ctx = self._load_inference(tpu_input_buf, tpu_output_buf, inputs)

            # Run
            self._run(mode)

            # Get results:
            result = self._get_inference(ctx)

            # NOTE: only after we have a copy of results in memory as numpy arrays -
            #       we can exit from buffer_exit_stack thus releasing IO pointers!

        self._check_status()

        return result

    def _check_status(self) -> None:
        status_code = _LIB_TPU_BINDER.libtpu.tpu_get_inference_status(self._pointer)
        if status_code != 0:
            msg = self._get_error_message()
            raise InferenceError(f'Invalid inference status code {status_code}: {msg}')

    def close(self):
        _LIB_TPU_BINDER.libtpu.tpu_destroy_inference(self._pointer)

    def _load_inference(self, tpu_input: _TensorBufferObject, tpu_output: _TensorBufferObject,
                        input_data: Mapping[str, np.ndarray]) -> Dict[str, CTX]:

        if not isinstance(input_data, collections.abc.Mapping):
            raise ValueError('Input data must be a mapping, got:' + str(type(input_data)))

        # Inputs:
        for tensor_name, tensor_data in input_data.items():
            tensor_idx = self._tensor_name_to_tensor_index[tensor_name]
            tensor_size = self._tensor_name_to_tensor_size[tensor_name]

            in_tensor = bytearray(tensor_data)
            p_in_tensor = (c_uint8 * tensor_size).from_buffer(in_tensor)
            tpu_input.set_user_tensor_buffer_ptr(tensor_idx, cast(p_in_tensor, POINTER(c_uint8)))

        _LIB_TPU_BINDER.libtpu.tpu_set_inference_inputs(self._pointer, tpu_input._pointer)

        # Outputs:
        out_ctx = dict()

        for tensor_name in self._program._output_metadata:
            tensor_idx = self._tensor_name_to_tensor_index[tensor_name]
            tensor_size = self._tensor_name_to_tensor_size[tensor_name]

            out_tensor = bytearray(np.empty((tensor_size,), dtype=np.uint8))
            p_out_tensor = (c_uint8 * tensor_size).from_buffer(out_tensor)
            c_out_ptr = cast(p_out_tensor, POINTER(c_uint8))
            tpu_output.set_user_tensor_buffer_ptr(tensor_idx, c_out_ptr)

            out_ctx[tensor_name] = c_out_ptr

        _LIB_TPU_BINDER.libtpu.tpu_set_inference_outputs(self._pointer, tpu_output._pointer)

        return out_ctx

    def _get_inference(self, ctx: Dict[str, CTX]) -> Dict[str, np.ndarray]:
        out_meta = self._program._output_metadata
        hw_par_meta = self._program._hardware_parameters_metadata

        collected_data = dict()

        for tensor_name, out_ctx in ctx.items():
            tensor_size = self._tensor_name_to_tensor_size[tensor_name]
            data = np.ctypeslib.as_array(out_ctx, shape=(tensor_size,))

            if self._program._is_raw:
                data = data.reshape(-1, hw_par_meta["ddr_word_len"])
            else:
                data = _convert_from_uint8_to_user_dtype(data, out_meta[tensor_name]['user_dtype'])
                data = data.reshape(out_meta[tensor_name]['user_shape'])

            collected_data[tensor_name] = data

        return collected_data


def _convert_from_uint8_to_user_dtype(data, user_dtype):
    if 'int' in user_dtype:
        return data.view(user_dtype)
    elif 'float16' == user_dtype:
        return data.view(np.uint16).view(user_dtype)
    elif 'float32' == user_dtype:
        return data.view(np.uint32).view(user_dtype)
    else:
        raise AssertionError(f'{user_dtype} as user_dtype does not support!')


def _is_raw_metadata(metadata: Dict[str, Any]) -> bool:
    """Heuristic to determine if the metadata dictionary corresponds to the RAW program."""

    # Metadata for outputs (first argv region in the outputs)
    out_meta = next(iter(metadata['outputs'].values()))  # type: ignore

    # Metadata for the first output tensor (no mixed raw/non-raw tensor metadata is possible so any output tensor metadata will suffice):
    output_tensor_metadata = next(iter(out_meta.values()))

    # RAW programs only contain 'address' and 'size' fields, user_* fields are only present in non-raw programs:
    return 'user_dtype' not in output_tensor_metadata


def _is_raw_program(program_path: str) -> bool:
    """Inspect ZIP file (open with zipfile) and determine determine whether program is in RAW format or not."""

    with zipfile.ZipFile(program_path, 'r') as tpu_program:
        data = tpu_program.read('metadata.json')

    metadata = json.loads(data)
    return _is_raw_metadata(metadata)
