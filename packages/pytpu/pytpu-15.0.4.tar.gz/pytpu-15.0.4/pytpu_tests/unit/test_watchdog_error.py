import pytest

import pytpu as tpu


@pytest.mark.skip(reason="watchdog program has mem collision and breaks the device and other pytpu_tests")
def test_watchdog_error(tpu_device, watchdog_program):
    with pytest.raises(tpu.InferenceError):
        # infer failed program
        ...

    # @pytest.fixture(scope='module')
    # def watchdog_program(tpu_device: tpu.Device):
    #     program_path = "{}/watchdog.tpu".format(get_programs_path(tpu_device))
    #     with tpu_device.load(program_path) as tpu_program:
    #         yield tpu_program

    # # TODO: watchdog breaks the device?...
    # input_path = os.path.join(get_data_path(), "watchdog/input.bin")
    # inp = np.fromfile(input_path, dtype=np.int8)
    #
    # inference = TPUInference(watchdog_program)
    # inference.load([inp])
    # status = tpu_device.load_inference_sync(inference)
    # assert not status.is_success

# TODO: what about that?:
# @pytest.fixture(scope='module')
# def mem_collision_program(tpu_device: tpu.Device):
#     program_path = "{}/mem_collision.tpu".format(get_programs_path(tpu_device))
#     with tpu_device.load(program_path) as tpu_program:
#         yield tpu_program
