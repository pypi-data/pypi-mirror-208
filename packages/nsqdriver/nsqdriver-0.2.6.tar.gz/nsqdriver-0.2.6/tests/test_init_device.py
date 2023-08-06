from cython_lib.lib_init_device.init_device import get_board_info


def test_print_board_info():
    print(get_board_info())
