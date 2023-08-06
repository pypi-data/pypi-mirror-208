import concurrent.futures
import contextlib
import os.path
import threading
from collections import deque
from itertools import cycle
from math import ceil

import pytest

import pytpu as tpu
from ._helpres import get_data_path, get_programs_path


from ._resnet50 import pre as resnet50_pre
from ._resnet50 import post as resnet50_post

testdata = [
    (os.path.join(get_data_path(), "resnet50/images/0.jpg"), 227),
]


@pytest.mark.parametrize("image_path, expected", testdata)
def test_resnet50_inference_sync(image_path: str, expected: int):
    num_images = 100

    def pre(image_path):
        tensor_dct, sizes = resnet50_pre(image_path)
        return tensor_dct, sizes

    def post(out, sizes):
        return resnet50_post(sizes, out)

    inputs = [image_path for _ in range(num_images)]

    with contextlib.ExitStack() as tpu_device_stack:
        tpu_devices = [tpu_device_stack.enter_context(tpu.Device.open(i)) for i in tpu.Device.list_devices()]
        program_path = "{}/resnet50.tpu".format(get_programs_path(tpu_devices[0]))

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


@pytest.mark.skip()  # TODO: add appropriate JIRA issue?
@pytest.mark.parametrize("image_path, expected", testdata)
def test_resnet50_inference_thread(image_path: str, expected: int):
    _thread_to_inference = dict()

    max_workers = 4
    num_images = 100

    def pre(image_path):
        tensor_dct, sizes = resnet50_pre(image_path)
        return tensor_dct, sizes

    def post(out, sizes):
        return resnet50_post(sizes, out)

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
            program_path = "{}/resnet50.tpu".format(get_programs_path(tpu_devices[0]))
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
