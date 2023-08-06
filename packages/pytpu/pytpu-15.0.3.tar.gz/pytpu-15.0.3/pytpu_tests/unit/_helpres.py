import os

import pytpu as tpu


def get_data_path():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "../data"
    )


def get_programs_path(tpu_device: tpu.Device):
    dev_info = tpu_device.info()

    ddr_word_length = dev_info["axi_word_len"] // 8
    cache_word_length = dev_info["cache_word_len"] // 8
    programs_path = os.path.join(
        get_data_path(),
        "ddr_{}/cache_{}".format(ddr_word_length, cache_word_length)
    )
    if not os.path.isdir(programs_path):
        raise RuntimeError(
            "No device pytpu_tests for axi word length {} cache word length {}".format(ddr_word_length,
                                                                                       cache_word_length))
    return programs_path
