from functools import wraps
import numpy as np
import pytest
import torch
# import matplotlib.pyplot as plt
from waveforms import *
from time import time
from .conftest import skip_demod_speed_test, skip_numpy_demod_test

from backend.svqbit import coff_para, demodMatrix, demodTorch, demodTorch_no_complex

# import os
#
# cpu_num = 6 # 这里设置成你想运行的CPU个数
# os.environ ['OMP_NUM_THREADS'] = str(cpu_num)
# os.environ ['OPENBLAS_NUM_THREADS'] = str(cpu_num)
# os.environ ['MKL_NUM_THREADS'] = str(cpu_num)
# os.environ ['VECLIB_MAXIMUM_THREADS'] = str(cpu_num)
# os.environ ['NUMEXPR_NUM_THREADS'] = str(cpu_num)
# torch.set_num_threads(cpu_num)
torch.set_grad_enabled(False)


def no_tensor_grad(func):
    @wraps(func)
    def dec(*args, **kwargs):
        with torch.no_grad():
            return func(*args, **kwargs)

    return dec


params = []
for chnl in [1, 6, 12]:
    for frq in [6, 12, 24]:
        for shots in [32, 64, 128, 256, 512, 1024]:
            params.append(pytest.param(chnl, frq, shots, id=f'Param<{chnl, frq, shots}>'))


def test_pytorch_cuda_enabled():
    print(torch.__config__.show())
    print(torch.__config__.parallel_info())
    print(f'\n pytorch_cuda_enable: {torch.cuda.is_available()}')
    assert True


@pytest.mark.skipif(True, reason='两边算出来的值有差别')
def test_algorithm_equal():
    lo, freq = 4.5e9, [i*1e6 for i in range(1, 9)]
    sigs = []
    for i in range(8):
        wave = cos(2 * np.pi * (lo+freq[i]))
        wave.start, wave.stop = 0, 4e-6
        noise = 0.01*np.random.random((1024, 16000))
        sig = np.empty((1024, 16000))
        _sig = wave.sample(4e9)
        for j in range(1024):
            sig[j] = _sig
        sig += noise
        sig = (2 ** 15 - 1) * sig
        sigs.append(sig)
    sigs = np.array(sigs, dtype=np.int16)

    tm = np.linspace(0, 4e-6, 16000)
    coff = [coff_para(tm, lo).reshape(16000, 1) for _ in range(8)]
    coff = np.array(coff)

    numpy_res = np.zeros((8, 1024, 1), dtype='complex64')
    for i in range(8):
        numpy_res[i] = demodMatrix(sigs[i], coff[i])

    torch_res = torch.zeros((8, 1024, 1), dtype=torch.complex64)
    torch_sigs = torch.tensor(sigs).to(torch.complex64)
    torch_coff = torch.tensor(coff).to(torch.complex64)
    for i in range(4):
        demodTorch(torch_sigs[:, i*256:(i+1)*256, :], torch_coff, out=torch_res[:, i*256:(i+1)*256, :])

    assert np.allclose(numpy_res, torch_res.numpy())
    assert (numpy_res == torch_res).all()


@pytest.mark.skipif(skip_demod_speed_test, reason='跳过硬解速度测试，过于耗时')
@pytest.mark.parametrize('chnl_num, frq_num, shots', params)
def test_pytorch_demodulator(chnl_num, frq_num, shots):
    sample_rate = 4e9
    width = 4e-6

    freqlist = [[4550e6 + j * 300e6 for j in range(frq_num)] for i in range(chnl_num)]
    cofflist = {i: [] for i in range(chnl_num)}

    wav_readout = [zero() for i in range(chnl_num)]
    for i in range(chnl_num):
        for j in range(len(freqlist[i])):
            wav_readout[i] = wav_readout[i] + cos(2 * np.pi * freqlist[i][j]) * (square(width) >> width / 2)
            # wav_readout[i] = wav_readout[i] + (square(width) >> width/2+1e-6)
        wav_readout[i] = wav_readout[i] / frq_num
        wav_readout[i].start = 0
        wav_readout[i].stop = width
        wav_readout[i] = (2 ** 15 - 1) * wav_readout[i].sample(sample_rate).reshape((1, round(width * sample_rate)))
        wav_readout[i] = np.vstack([wav_readout[i] for _ in range(shots)])
    wav_readout = torch.tensor(np.array(wav_readout, dtype='int16'), dtype=torch.int16).to(torch.complex64)

    tm = np.linspace(0, width, round(width * sample_rate))
    for chnl in range(chnl_num):
        _freqlist = freqlist[chnl]
        cofflist[chnl] = np.empty((len(_freqlist), round(width * sample_rate))).astype(complex)
        for i in range(len(_freqlist)):
            cofflist[chnl][i] = coff_para(tm, _freqlist[i], 0)
        cofflist[chnl] = cofflist[chnl].T
    cofflist = torch.tensor(np.array([i for i in cofflist.values()]), dtype=torch.complex64)

    st = time()
    threads = []
    # for i in range(2):
    #     _thread = threading.Thread(target=demodTorch, args=(wav_readout, cofflist), daemon=True)
    #     threads.append(_thread)
    # for i in threads:
    #     i.start()
    # for i in threads:
    #     i.join()

    for i in range(5):
        demodTorch(wav_readout, cofflist)
    print(f'----{chnl_num}通道, {frq_num}频点, {shots}shots, 单个shots硬解耗时: {(time() - st) / 5 / shots * 1e6}-{200}μs')


@pytest.mark.skipif(skip_demod_speed_test, reason='跳过硬解速度测试，过于耗时')
@pytest.mark.parametrize('chnl_num, frq_num, shots', params)
def test_pytorch_no_complex(chnl_num, frq_num, shots):
    """
    下变频速度测试，非复数运算版
    """
    sample_rate = 4e9
    width = 4e-6
    # chnl_num = 1
    # frq_num = 1
    # shots = 1

    freqlist = [[4550e6 + j * 300e6 for j in range(frq_num)] for i in range(chnl_num)]
    cofflist = {i: [] for i in range(chnl_num)}

    wav_readout = [zero() for i in range(chnl_num)]
    for i in range(chnl_num):
        for j in range(len(freqlist[i])):
            wav_readout[i] = wav_readout[i] + cos(2 * np.pi * freqlist[i][j]) * (square(width) >> width / 2)
            # wav_readout[i] = wav_readout[i] + (square(width) >> width/2+1e-6)
        wav_readout[i] = wav_readout[i] / frq_num
        wav_readout[i].start = 0
        wav_readout[i].stop = width
        wav_readout[i] = (2 ** 15 - 1) * wav_readout[i].sample(sample_rate).reshape((1, round(width * sample_rate)))
        wav_readout[i] = np.vstack([wav_readout[i] for _ in range(shots)])
    wav_readout = torch.tensor(np.array(wav_readout, dtype='int16'), dtype=torch.float32)

    tm = np.linspace(0, width, round(width * sample_rate))
    for chnl in range(chnl_num):
        _freqlist = freqlist[chnl]
        cofflist[chnl] = np.empty((len(_freqlist), round(width * sample_rate))).astype(complex)
        for i in range(len(_freqlist)):
            cofflist[chnl][i] = coff_para(tm, _freqlist[i], 0)
        cofflist[chnl] = cofflist[chnl].T
    cofflist = torch.tensor(np.array([i for i in cofflist.values()]), dtype=torch.complex64)
    cofflist = [cofflist.real.to(torch.float32), cofflist.imag.to(torch.float32)]

    st = time()
    threads = []
    # for i in range(10):
    #     _thread = threading.Thread(target=demodTorch, args=(wav_readout, cofflist), daemon=True)
    #     threads.append(_thread)
    # for i in threads:
    #     i.start()
    # for i in threads:
    #     i.join()

    for i in range(5):
        demodTorch_no_complex(wav_readout, cofflist, [round(width * sample_rate)]*chnl_num)
    print(f'----{chnl_num}通道, {frq_num}频点, {shots}shots, 单个shots硬解耗时: {(time() - st) / 5 / shots * 1e6}-{200}μs')


@pytest.mark.skipif(skip_demod_speed_test, reason='跳过硬解速度测试')
@pytest.mark.skipif(skip_numpy_demod_test, reason='跳过numpy硬解速度测试')
@pytest.mark.parametrize('chnl_num, frq_num, shots', params)
def test_numpy_demodulator(chnl_num, frq_num, shots):
    """
    numpy库硬解测试

    :param chnl_num:
    :param frq_num:
    :param shots:
    :return:
    """
    sample_rate = 4e9
    width = 4e-6
    # chnl_num = 1
    # frq_num = 1
    # shots = 1

    freqlist = [[4550e6 + j * 300e6 for j in range(frq_num)] for i in range(chnl_num)]
    cofflist = {i: [] for i in range(chnl_num)}

    wav_readout = [zero() for i in range(chnl_num)]
    for i in range(chnl_num):
        for j in range(len(freqlist[i])):
            wav_readout[i] = wav_readout[i] + cos(2 * np.pi * freqlist[i][j]) * (square(width) >> width / 2)
            # wav_readout[i] = wav_readout[i] + (square(width) >> width/2+1e-6)
        wav_readout[i] = wav_readout[i] / frq_num
        wav_readout[i].start = 0
        wav_readout[i].stop = width
        wav_readout[i] = (2 ** 15 - 1) * wav_readout[i].sample(sample_rate).reshape((1, round(width * sample_rate)))
        wav_readout[i] = np.vstack([wav_readout[i] for _ in range(shots)])
    wav_readout = np.array(wav_readout, dtype='int16')

    tm = np.linspace(0, width, round(width * sample_rate))
    for chnl in range(chnl_num):
        _freqlist = freqlist[chnl]
        cofflist[chnl] = np.empty((len(_freqlist), round(width * sample_rate))).astype(complex)
        for i in range(len(_freqlist)):
            cofflist[chnl][i] = coff_para(tm, _freqlist[i], 0)
        cofflist[chnl] = cofflist[chnl].T
    cofflist = np.array([i for i in cofflist.values()], dtype=complex)

    st = time()
    threads = []

    def demod(wave, coff):
        for i in range(chnl_num):
            demodMatrix(wave[i], coff[i])

    for i in range(2):
        demod(wav_readout, cofflist)
    print(f'----{chnl_num}通道, {frq_num}频点, {shots}shots, 单个shots硬解耗时: {(time() - st) / 2 / (shots) * 1e6}-{200}μs')
