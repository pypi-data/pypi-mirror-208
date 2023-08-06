from functools import wraps
import platform
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pytest
from waveforms import *
from time import time

from cython_lib.lib_gen_waveform.gen_waveform import gen_wave

sample_rate = 4e9
width = 20e-9
time_line = np.linspace(0, width * 100, int(width * 100 * sample_rate))
waves = {
    'poly': poly([1, -1 / 2, 1 / 6, -1 / 12]),
    'cos': cos(2 * pi * 5.2e9),
    'sin': sin(2 * pi * 5.2e9),
    'gaussian': gaussian(width) >> (width * 2),
    'sinc': sinc(6e8),
    'square': square(width) >> (width * 2),
    'cosPulse': cosPulse(width) >> (width * 2),
    'chirp_linear': chirp(1e9, 1.5e9, width * 10, type='linear'),
    'chirp_exponential': chirp(1e9, 1.5e9, width * 10, type='exponential'),
    'chirp_hyperbolic': chirp(1e9, 1.5e9, width * 10, type='hyperbolic'),
    'cos*gaussian': cos(2 * pi * 5.2e9) * gaussian(width) >> (width * 2),
    'cos*cosPulse': cos(2 * pi * 5.2e9) * cosPulse(width) >> (width * 2),
    'gaussian_with_window': (gaussian(10) >> width*2) + square(width, edge=5, type='linear') * cos(2 * pi * 5.2e9),
}


def gen(_wave, _width, rate):
    line = np.arange(0, _width, 1 / rate)
    gen_wave(_wave, line)


def gen_numpy(_wave, _width, rate):
    line = np.arange(0, _width, 1 / rate)
    _wave(line)


class TestCyGenWave:
    @pytest.mark.skipif(platform.system() == 'Windows', reason='gen_wave暂不支持windows')
    @pytest.mark.parametrize('wave', [pytest.param(j, id=f'Wave<{i}>') for i, j in waves.items()])
    def test_waveform_close(self, wave: Waveform):
        """
        判断生成的float64数据是否全部接近
        """
        wave_numpy = wave(time_line)
        wave_cython = gen_wave(wave, time_line)
        assert np.allclose(wave_numpy, wave_cython)

    @pytest.mark.skipif(platform.system() == 'Windows', reason='gen_wave暂不支持windows')
    @pytest.mark.parametrize('wave', [pytest.param(j, id=f'Wave<{i}>') for i, j in waves.items()])
    def test_waveform_equal(self, wave):
        """
        判断生成的数据转为int16后是否完全相等
        """
        wave_numpy = wave(time_line)
        wave_cython = gen_wave(wave, time_line)
        assert ((wave_numpy * (2 ** 15 - 1)).astype(np.int16) == (wave_cython * (2 ** 15 - 1)).astype(np.int16)).all()

    @pytest.mark.skipif(platform.system() == 'Windows', reason='gen_wave暂不支持windows')
    def test_pulse_speed(self):
        """
        pulse信号生成速度测试
        """
        sample_rate = 6e9
        width = 30e-9
        width_all = 100e-6
        frq = 4200e6
        chnl_num = 24

        wave_lo = cos(2 * pi * frq)
        wave_30 = [(gaussian(width) >> (width / 2)) * wave_lo for i in range(chnl_num)]
        for wave in wave_30:
            wave.start = 0
            wave.stop = width
        wave_100 = [zero() for i in range(chnl_num)]
        for index, wave in enumerate(wave_100):
            for i in range(int(300)):
                wave += (gaussian(width) >> (width * 2 * i + width / 2)) * wave_lo
            wave.start = 0
            wave.stop = width_all
            wave_100[index] = wave

        st = time()
        for i in range(10):
            for wave in wave_30:
                line = np.arange(0, width_all, 1 / sample_rate)
                wave_numpy = wave_lo(line)
        print(f'\n{chnl_num}通道, numpy长波形生成耗时: {(time() - st) / 10}')

        st = time()
        for i in range(10):
            for wave in wave_30:
                line = np.arange(0, width_all, 1 / sample_rate)
                wave_cython = gen_wave(wave_lo, line)
        print(f'{chnl_num}通道, cython长波形生成耗时: {(time() - st) / 10}')

        assert np.allclose(wave_numpy, wave_cython)

        pool = ProcessPoolExecutor(max_workers=6)
        st = time()
        for i in range(5):
            futures = [pool.submit(gen_numpy, wave_lo, width_all, sample_rate) for wave in wave_30]
            [_.result() for _ in futures]
        print(f'{chnl_num}通道, 进程池numpy长波形生成耗时: {(time() - st) / 5}')
        pool.shutdown(wait=True)

        pool = ProcessPoolExecutor(max_workers=6)
        st = time()
        for i in range(5):
            futures = [pool.submit(gen, wave_lo, width_all, sample_rate) for wave in wave_30]
            [_.result() for _ in futures]
        print(f'{chnl_num}通道, 进程池cython长波形生成耗时: {(time() - st) / 5}')
        pool.shutdown(wait=True)

        st = time()
        for i in range(100):
            for wave in wave_30:
                line = np.arange(0, width_all, 1/sample_rate)
                wave_numpy = wave(line)
        print(f'\n{chnl_num}通道, numpy简单波形生成耗时: {(time() - st) / 100}')

        st = time()
        for i in range(100):
            for wave in wave_30:
                line = np.arange(0, width_all, 1 / sample_rate)
                wave_cython = gen_wave(wave, line)
        print(f'{chnl_num}通道, cython简单波形生成耗时: {(time() - st) / 100}')

        assert np.allclose(wave_numpy, wave_cython)

        st = time()
        for i in range(5):
            for wave in wave_100:
                line = np.arange(0, width_all, 1 / sample_rate)
                wave_numpy = wave(line)
        print(f'{chnl_num}通道, numpy复杂波形生成耗时: {(time() - st) / 10}')

        st = time()
        for i in range(5):
            for wave in wave_100:
                line = np.arange(0, width_all, 1 / sample_rate)
                wave_cython = gen_wave(wave, line)
        print(f'{chnl_num}通道, cython复杂波形生成耗时: {(time() - st) / 5}')

        assert np.allclose(wave_numpy, wave_cython)
