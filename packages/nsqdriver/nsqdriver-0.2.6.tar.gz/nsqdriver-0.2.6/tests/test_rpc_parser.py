import pytest
from copy import copy
import numpy as np
import waveforms

from nsqdriver.NS_MCI import RPCValueParser
from rfskit.config import dumps_dict


class TestRPCValueParser:
    """
    测试RPCValueParser.dump与RPCValueParser.load的完备性
    """
    @pytest.mark.parametrize('value',
                             [pytest.param(['tom', 1, 2, [1, 2]], id='Type<list>'),
                              pytest.param(np.array([1], dtype=np.float64)[0], id='Type<np.float64>'),
                              pytest.param(np.array([1], dtype=np.int32)[0], id='Type<np.int32>'),
                              pytest.param(15.34, id='Type<num>'),
                              pytest.param(15 + 1j, id='Type<complex>'),
                              pytest.param(waveforms.cos(100), id='Type<waveforms.Waveform>')])
    def test_parser_common(self, value):
        """
        通用测试

        :param value:
        :return:
        """
        data = RPCValueParser.dump(value)
        _res = RPCValueParser.load(data)
        assert value == _res

    def test_parser_ndarray(self):
        """
        测试ndarray

        :return:
        """
        # 普通array
        _value = np.arange(100).reshape((10, 10))
        data = RPCValueParser.dump(_value)
        _res = RPCValueParser.load(data)
        assert _value.dtype == _res.dtype
        assert (_value == _res).all()

        # 复数array
        _value = np.arange(100).reshape((10, 10)).astype(complex)
        data = RPCValueParser.dump(_value)
        _res = RPCValueParser.load(data)
        assert _value.dtype == _res.dtype
        assert (_value == _res).all()

    def test_parser_tuple(self):
        """
        测试元组

        :return:
        """
        _value = (1, 2, '2')
        data = RPCValueParser.dump(_value)
        _res = RPCValueParser.load(data)

        assert _value == tuple(_res)

    def test_parser_nested(self):
        """
        多层嵌套测试

        :return:
        """
        _list = [1, 2, 3]
        _tuple = (4, 5, 6)
        _ndarray = np.array([6, 7, 8])
        _list_tuple = copy(_list)
        _list_tuple.append(copy(_tuple))
        _waveform = waveforms.sinc(10)

        _value = [_list, _tuple, _ndarray, _list_tuple, _waveform]
        data = RPCValueParser.dump(_value)
        _res = RPCValueParser.load(data)

        assert _list == _res[0]
        assert _tuple == tuple(_res[1])
        assert (_ndarray == _res[2]).all()
        assert _list_tuple[:len(_list)] == _res[3][:len(_list)]
        assert _list_tuple[len(_list)] == tuple(_res[3][len(_list)])
        assert _waveform == _res[4]


@pytest.mark.parametrize('value',
                         [pytest.param({}, id='Type<empty>'),
                          pytest.param({0: ['34', 'list', {1: 1}]}, id='Type<list>'),
                          pytest.param({'array': np.arange(10000)}, id='Type<np.float64>'),
                          pytest.param({'np.int32': np.array([1], dtype=np.int32)[0]}, id='Type<np.int32>'),
                          pytest.param({'num': 15.34}, id='Type<num>'),
                          pytest.param({'complex': 15 + 1j}, id='Type<complex>'),
                          pytest.param({'waveform': waveforms.cos(100)}, id='Type<waveforms.Waveform>'),
                          pytest.param({'collection': {1, 2, 3}}, id='Type<collection>'),
                          pytest.param({'dict': {'num': 123.34345, 'array': np.arange(10000)}}, id='Type<nested>')])
def test_dumps_dict(value):
    data = dumps_dict(value)
    print('\n'+data)
    assert isinstance(data, str)
