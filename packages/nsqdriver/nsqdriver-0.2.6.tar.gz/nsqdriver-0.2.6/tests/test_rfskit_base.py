import pytest
import time

from .conftest import FakeTCPHandler, skip_rfskit_test
from rfskit import RFSKit
from rfskit.interface import CommandTCPInterface, DataTCPInterface


class TestRFSKit:
    @pytest.mark.skipif(skip_rfskit_test,
                        reason='越过rfskit测试')
    def test_init_rfskit(self, fake_cmd_server):
        CommandTCPInterface._target_id = '127.0.0.1'
        kit = RFSKit(auto_load_icd=True,
                     auto_write_file=False,
                     cmd_interface=CommandTCPInterface,
                     data_interface=DataTCPInterface)
        connected = kit.start_command('127.0.0.1')

        assert isinstance(kit, RFSKit)
        assert connected
        assert connected == kit._connected

    @pytest.mark.skipif(skip_rfskit_test,
                        reason='越过rfskit测试')
    @pytest.mark.skipif(not FakeTCPHandler.finished,
                        reason='处理函数未完成')
    def test_send_tcp_command(self, fake_cmd_server):
        time.sleep(1)
        CommandTCPInterface._target_id = '127.0.0.1'
        kit = RFSKit(auto_load_icd=True,
                     auto_write_file=False,
                     cmd_interface=CommandTCPInterface,
                     data_interface=DataTCPInterface)
        kit.start_command('127.0.0.1')
        assert kit.execute_command('内部PRF产生')
