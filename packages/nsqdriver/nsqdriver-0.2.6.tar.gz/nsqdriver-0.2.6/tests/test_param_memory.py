import pytest
import numpy as np
import waveforms

from rfskit.config import dumps_dict
from backend.param_memory import ParamMemory, global_param_memory, AttributeWithMemory, BoardProperty


class ExampleClass(AttributeWithMemory):
    def __init__(self):
        self.attr_a = 'a'
        self.attr_b = 156


EXAMPLE_OBJ = ExampleClass()


class TestParamMemory:
    """
    测试ParamMemory
    """

    def test_is_singleton_memory(self):
        """
        测试全局只有一个memory
        """
        print(f'\n{self.test_is_singleton_memory.__doc__}')
        assert ParamMemory() is global_param_memory

    @pytest.mark.parametrize('name, value',
                             [pytest.param('save_list', [1, 2, 3], id='Type<list>'),
                              pytest.param('save_waveforms', waveforms.cos(10), id='Type<waveforms>')])
    def test_set_param(self, name, value):
        """
        测试向memory里设置和取出参数
        """
        # print(f'\n{self.test_set_param.__doc__} {name}-{value}')
        setattr(global_param_memory, name, value)
        assert getattr(global_param_memory, name) == value

    def test_like_obj_attr(self):
        _value = np.array([1, 2, 3])
        global_param_memory.data = _value
        assert (global_param_memory.data == _value).all()
        assert 'data' in global_param_memory._memory

    def test_memory_like_dict(self):
        _value = np.array([1, 2, 3])
        global_param_memory['data_dict'] = _value
        assert (global_param_memory['data_dict'] == _value).all()
        assert 'data_dict' in global_param_memory['_memory']

    def test_debug_param(self):
        debug_name = 'debug_test'
        assert global_param_memory.get_debug_value(debug_name) is None
        # global_param_memory.debug_params.add(debug_name)
        global_param_memory.add_debug_param(debug_name)
        for i in range(10):
            global_param_memory.debug_test = i

        # print(f'\n{global_param_memory.debug_test}')
        assert global_param_memory.debug_test == 9
        assert list(global_param_memory.get_debug_value(debug_name).values()) == list(range(10))
        print(f"\n{dumps_dict(global_param_memory.get_debug_value(debug_name))}")
        # clear_debug_log
        global_param_memory.clear_debug_log(debug_name)
        assert global_param_memory.get_debug_value(debug_name) == {}

    def test_print_memory(self):
        print(f'\n keys: {global_param_memory.show_keys()}')
        print(f'\n repr: {repr(global_param_memory)}')
        print(f'\n str: {global_param_memory}')


class TestAttributeWithMemory:
    def test_auto_memory_name(self):
        assert getattr(EXAMPLE_OBJ, 'memory_name', None) == EXAMPLE_OBJ.__class__.__name__

    def test_remember_obj_attr(self):
        assert global_param_memory[EXAMPLE_OBJ.get_memory_name('attr_a')] == EXAMPLE_OBJ.attr_a
        assert global_param_memory[EXAMPLE_OBJ.get_memory_name('attr_b')] == EXAMPLE_OBJ.attr_b


class Board(AttributeWithMemory):
    aa = BoardProperty('aa_p', 10)

    def __init__(self, aa):
        self.aa = aa


class TestBoardProperty:
    def test_set_prop(self):
        a = Board(3)
        b = Board(6)
        c = Board({'aa_p': 8})
        assert a.aa == 3 and b.aa == 6 and c.aa == 8

    def test_immutable_prop(self):
        a = Board({'!aa_p': 9})
        a.aa = 15
        assert a.aa == 9
