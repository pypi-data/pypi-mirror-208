import pytpu as tpu

from ._helpres import get_programs_path


def test_program_lut_parameters():
    tpu_devices = tpu.Device.list_devices()
    assert tpu_devices, 'No TPU device found, check /dev'
    with tpu.Device.open(tpu_devices[0]) as tpu_device:
        program_path = "{}/resnet50.tpu".format(get_programs_path(tpu_device))

        with tpu_device.load(program_path) as tpu_program:
            program_info = tpu_program.info()
            lut_activation_params = program_info['hardware_parameters']['lut_activation_params']
            assert lut_activation_params["input_bw"] == 12
            assert lut_activation_params["lut_bw"] == 16
            assert lut_activation_params["lut_depth"] == 8
            assert lut_activation_params["output_bw"] == 16
