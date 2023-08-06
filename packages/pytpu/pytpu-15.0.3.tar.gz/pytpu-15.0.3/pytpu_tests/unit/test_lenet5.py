import concurrent.futures
import contextlib
import os.path
import tempfile
import threading
from collections import deque
from itertools import cycle
from math import ceil

import pytest

import pytpu as tpu
from ._helpres import get_data_path, get_programs_path
from ._lenet5 import post as lenet5_post
from ._lenet5 import pre as lenet5_pre

testdata = [
    (os.path.join(get_data_path(), "lenet5/images/0.jpg"), 0),
    (os.path.join(get_data_path(), "lenet5/images/1.jpg"), 1),
    (os.path.join(get_data_path(), "lenet5/images/2.jpg"), 2),
    (os.path.join(get_data_path(), "lenet5/images/3.jpg"), 3),
    (os.path.join(get_data_path(), "lenet5/images/4.jpg"), 4),
    (os.path.join(get_data_path(), "lenet5/images/5.jpg"), 5),
    (os.path.join(get_data_path(), "lenet5/images/6.jpg"), 6),
    (os.path.join(get_data_path(), "lenet5/images/7.jpg"), 7),
    (os.path.join(get_data_path(), "lenet5/images/8.jpg"), 8),
    (os.path.join(get_data_path(), "lenet5/images/9.jpg"), 9),
]


@pytest.mark.parametrize("image_path, expected", testdata)
def test_lenet5_inference_sync(image_path: str, expected: int):
    num_images = 1000

    def pre(image_path):
        tensor_dct, sizes = lenet5_pre(image_path)
        return tensor_dct, sizes

    def post(out, sizes):
        return lenet5_post(sizes, out)

    inputs = [image_path for _ in range(num_images)]

    with contextlib.ExitStack() as tpu_device_stack:
        tpu_devices = [tpu_device_stack.enter_context(tpu.Device.open(i)) for i in tpu.Device.list_devices()]
        program_path = "{}/lenet5.tpu".format(get_programs_path(tpu_devices[0]))

        with contextlib.ExitStack() as tpu_program_stack:
            tpu_programs = [tpu_program_stack.enter_context(tpu.load(program_path)) for tpu in tpu_devices]
            with contextlib.ExitStack() as tpu_inference_stack:
                programs_merged_inputs = zip(cycle(tpu_programs), range(len(inputs)))

                for tpu_program, input_index in programs_merged_inputs:
                    inference = tpu_inference_stack.enter_context(tpu_program.inference())
                    input_, sizes = pre(inputs[input_index])
                    out = inference.sync(input_)

                    result = post(out, sizes)[0]
                    assert result == expected


@pytest.mark.skip('Work only on ASIC')  # TODO: add jira issue?
@pytest.mark.parametrize("image_path, expected", testdata)
def test_lenet5_inference_thread(image_path: str, expected: int):
    _thread_to_inference = dict()

    max_workers = 4
    num_images = 10000

    def pre(image_path):
        tensor_dct, sizes = lenet5_pre(image_path)
        return tensor_dct, sizes

    def post(out, sizes):
        return lenet5_post(sizes, out)

    def worker_init():
        tpu_program = tpu_program_queque.pop()
        thread = threading.current_thread()
        _thread_to_inference[thread] = tpu.Inference(tpu_program)

    def target(path):
        input_, sizes = pre(path)
        thread = threading.current_thread()
        inference = _thread_to_inference[thread]
        out = inference.sync(input_)
        result = post(out, sizes)
        return result

    with contextlib.ExitStack() as tpu_device_stack:
        tpu_devices = [tpu_device_stack.enter_context(tpu.Device.open(i)) for i in tpu.Device.list_devices()]

        with contextlib.ExitStack() as tpu_program_stack:
            program_path = "{}/lenet5.tpu".format(get_programs_path(tpu_devices[0]))
            tpu_programs = [tpu_program_stack.enter_context(tpu.load(program_path)) for tpu in tpu_devices]

            tpu_program_queque = deque(tuple(tpu_programs) * ceil(max_workers / len(tpu_devices)))
            inputs = [image_path for _ in range(num_images)]
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, initializer=worker_init,
                                                           initargs=()) as executor:
                    futures = []

                    for path in inputs:
                        futures.append(executor.submit(target, path))

                    for future in concurrent.futures.as_completed(futures):
                        out = future.result()
                        assert out[0] == expected
            finally:
                for inference in _thread_to_inference.values():
                    inference.close()


@pytest.mark.parametrize("image_path, expected", testdata)
def test_lenet5_inference_sync_raw(image_path: str, expected: int):
    def pre(image_path):
        tensor_dct, sizes = lenet5_pre(image_path)
        return tensor_dct, sizes

    def post(out, sizes):
        return lenet5_post(sizes, out)

    input_dict, sizes = pre(image_path)

    dev_name = tpu.Device.list_devices()[0]

    with tpu.Device.open(dev_name) as device:
        program_path = "{}/lenet5.tpu".format(get_programs_path(device))

        with tempfile.TemporaryDirectory() as temporary_directory:

            raw_program_file_name = os.path.join(temporary_directory, 'program_raw.tpu')
            codec = tpu.convert_to_raw(program_path, raw_program_file_name)

            with device.load(raw_program_file_name) as program:
                with program.inference() as inference:
                    encoded_dict = codec.encode(input_dict)

                    output_raw_dict = inference.sync(encoded_dict)

                    output_dict = codec.decode(output_raw_dict)

                    result = post(output_dict, sizes)
                    assert result[0] == expected
