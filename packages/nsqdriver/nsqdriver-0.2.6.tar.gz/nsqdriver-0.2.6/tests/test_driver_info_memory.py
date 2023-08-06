import pytest
import multiprocessing

from nsqdriver.NS_MCI import SHARED_DEVICE_MEM as MCI_MEM
from nsqdriver.NS_QSYNC import SHARED_DEVICE_MEM as QSYNC_MEM

DEVICES_IP = ['192.168.1.205', '192.168.1.206', '192.168.1.207', '192.168.1.208']


def test_driver_info_shared():
    """
    测试进程内确实可以共享info信息

    :return:
    """
    for ip in DEVICES_IP:
        MCI_MEM.ip = ip
    assert set(QSYNC_MEM.ip) == set(DEVICES_IP)


def other_process():
    for ip in DEVICES_IP:
        MCI_MEM.ip = ip


def test_shared_to_other_process():
    """
    测试跨进程增加信息

    :return:
    """
    MCI_MEM.clear_ip()
    assert QSYNC_MEM.ip == []
    process = multiprocessing.Process(target=other_process, daemon=True)
    process.start()
    process.join(2)
    assert set(QSYNC_MEM.ip) == set(DEVICES_IP)
