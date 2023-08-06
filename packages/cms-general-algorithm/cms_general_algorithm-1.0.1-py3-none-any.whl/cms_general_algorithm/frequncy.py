
import scipy.stats as st
import scipy.signal as sig
import numpy as np
import pandas as pd
import scipy.signal as sp


def fft(signal, fs, detrend=True):
    '''
    傅里叶变换
    @param signal:  信号
    @param fs:      采样频率
    @param detrend: 是否进行去趋势
    @return:        幅值，频率
    '''
    len_data = len(signal)
    if detrend:
        signal = sp.detrend(signal)
    amp = np.abs(np.fft.fft(signal - np.mean(signal))) / len_data * 2
    amp = amp[0: int(len_data / 2)]
    fre = np.arange(len_data) * fs / len_data
    fre = fre[0: int(len_data / 2)]
    return amp, fre


def envelope_spectrum(signal, frequency, detrend=True):
    '''
    包络谱
    @param signal:       信号
    @param frequency:    采样频率
    @param detrend:      是否进行去趋势
    @return:             包络谱的幅值，频率
    '''
    signal = np.abs(sp.hilbert(signal))
    return fft(signal, frequency, detrend)


def get_kurtosis(signal):
    '''
    峭度
    @param signal:   输入原始振动数据
    @return:         峭度
    '''
    if (len(signal) <= 0 or signal is None):
        return None

    return round(st.kurtosis(signal, fisher=False), 6)


def get_rms_spectrum(amplitude, frequency, fre_left, fre_right):  # modified 2022-10-18
    '''
    通过频率计算有效值
    @param amplitude:   fft后的幅值
    @param frequency:   fft后的频率
    @param fre_left:    带通左边界
    @param fre_right:   带通右边界
    @return:            有效值
    '''
    if (fre_left < 0 or fre_right < fre_left or len(amplitude) <= 0 or len(frequency) <= 0):
        return None
    rms = np.sqrt(np.sum(np.square(amplitude[np.logical_and(
        frequency >= fre_left, frequency <= fre_right)])) / 2)
    return round(rms, 6)


def get_rms_fft(signal, frequency, fre_left, fre_right):
    '''
    通过fft滤波后计算的有效值
    @param signal:      信号
    @param frequency:   信号采样频率
    @param fre_left:    带通左边界
    @param fre_right:   带通右边界
    @return:            有效值
    采用傅里叶变换直接滤波计算有效值
    '''
    amp, fre = fft(signal, frequency)
    return get_rms_spectrum(amp, fre, fre_left, fre_right)


def get_rms_butter(signal, frequency, fre_left, fre_right, n=2, t=5):
    '''
    通过巴特沃斯（默认2阶）滤波器滤波后计算有效值
    @param signal:      信号
    @param frequency:   信号采样频率
    @param fre_left:    带通左边界
    @param fre_right:   带通右边界
    @param n:           巴特沃斯滤波器阶数
    @return:            有效值
    采用巴特沃斯数字滤波器计算有效值
    '''
    filterdata = signal
    for i in range(t):
        [b, a] = sig.butter(
            n, [fre_left * 2 / frequency, fre_right * 2 / frequency], 'bandpass')
        filterdata = sig.filtfilt(b, a, signal)
    return get_rms(filterdata)


def get_rms_filter(signal, frequency, fre_left, fre_right, filter, rms_algorithm):
    '''
    采用其他滤波器可使用本方法计算
    @param signal:        信号
    @param frequency:     信号采样频率
    @param fre_left:      带通左边界
    @param fre_right:     带通右边界
    @param filter:        滤波器
    @param rms_algorithm: 滤波后计算方法
    @return:              有效值
    '''
    return rms_algorithm(filter(fre_left, fre_right, signal, frequency))


def get_rms(signal):
    '''
    一个基础的计算rms的方法，输入数据即可
    @param data:   时间序列
    '''
    return np.sqrt(np.sum(np.square(signal)) / len(signal))


def search_max_amplitude(amplitude, frequency, fre_low, fre_high, stop_fre=5000):
    '''
    在搜索频率内搜索最大震动幅值，搜索不到情况下，在0-stop_fre中查找距离(fre_low + fre_high)/2最近的数
    @param amplitude:   fft后的幅值
    @param frequency:   fft后的频率
    @param fre_left:    搜索左边界
    @param fre_right:   带通右边界
    @param stop_fre:    搜索不到情况下，在0-stop_fre中查找距离(fre_low + fre_high)/2最近的数
    @return:            包络谱
    '''
    amplitude = pd.Series(amplitude)
    frequency = pd.Series(frequency)
    range_amp = amplitude[(frequency >= fre_low) & (frequency <= fre_high)]
    range_fre = frequency[(frequency >= fre_low) & (frequency <= fre_high)]

    if len(range_fre) == 0:
        middle = (fre_low + fre_high)/2
        idx = np.argmin(np.abs(frequency.iloc[0:stop_fre] - middle))
        return frequency.iloc[idx], amplitude.iloc[idx]
    mode_fre, mode_amp = range_fre.iloc[range_amp.argmax()], range_amp.max()
    return mode_amp, mode_fre
