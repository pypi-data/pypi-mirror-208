import pytpu as tpu


def test_total_mem():
    tpu_devices = tpu.Device.list_devices()
    assert tpu_devices, 'No TPU device found, check /dev'
    with tpu.Device.open(tpu_devices[0]) as tpu_device:
        device_info = tpu_device.info()
        assert device_info['cache_buf_depth'] > 0
        assert device_info['cache_buf_number'] > 0
        assert device_info['ewp_mem_n_buf'] > 0
        assert device_info['ewp_mem_buf_depth'] > 0
