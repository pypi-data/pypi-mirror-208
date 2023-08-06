import matplotlib.pyplot as plt
import pandas as pd
import os
import datetime
from cms_general_algorithm.frequncy import search_max_amplitude
colors = ['green', 'red', 'purple', 'orange', 'pink']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 设置显示负号


def plot_spectrum_from_amp(amp, fre, fre_left, fre_right, fre_dict=None, title='频谱', line_color='b',  axvline_colors=colors, search_range=2, multipliers=[1, 2, 3], save_path='pic',  figsize=(15, 8)):
    '''
    @param amplitude:       幅值序列
    @param frequency:       频率序列
    @param fre_left:        画图左边界
    @param fre_right:       画图右边界
    @param fre_dict:        故障频率字典，画竖线标记
    @param title:           标题
    @param line_color:      折线颜色
    @param axvline_colors:  竖线颜色
    @param search_range:    在一定范围内搜索最大幅值
    @param multipliers:     需要标记故障频率的倍频
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    '''
    fig, axs = plt.subplots(1, 1, figsize=figsize)
    fig.suptitle(title, fontsize=16, x=0.5, y=0.99)
    os.makedirs(save_path, exist_ok=True)
    ax_plot_spectrum(axs, amp, fre, fre_left, fre_right, fre_dict,
                     '', line_color, axvline_colors, search_range, multipliers)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig_name = f'{save_path}/{title}.png'
    fig.savefig(fig_name, bbox_inches='tight')
    plt.close(fig)
    return fig_name


def ax_plot_spectrum(ax, amplitude, frequency, fre_left, fre_right, fre_dict, title, line_color='b', axvline_colors=colors, search_range=2, multipliers=[1, 2, 3]):
    '''
    @param axs:             子图
    @param amplitude:       幅值序列
    @param frequency:       频率序列
    @param fre_left:        画图左边界
    @param fre_right:       画图右边界
    @param fre_dict:        故障频率字典，画竖线标记
    @param title:           子图标题
    @param line_color:      折线颜色
    @param axvline_colors:  竖线颜色
    @param search_range:    在一定范围内搜索最大幅值
    @param multipliers:     需要标记故障频率的倍频
    '''
    amp = pd.Series(amplitude)
    fre = pd.Series(frequency)
    amp = amp[(fre >= fre_left) & (fre <= fre_right)]
    fre = fre[(fre >= fre_left) & (fre <= fre_right)]
    ax.set_xlim(fre_left, fre_right)
    if title != '':
        ax.set_title(title)
    ax.plot(fre, amp, c=line_color)
    ax.set_ylabel("幅值")
    ax.set_xlabel("频率(Hz)")
    if fre_dict is None:
        pass
    else:
        for key, c in zip(fre_dict.keys(), axvline_colors):
            for mul in multipliers:
                value = fre_dict[key]
                fre_low = value*mul - search_range
                fre_high = value*mul + search_range
                temp_amp, temp_fre = search_max_amplitude(
                    amp, fre, fre_low, fre_high)
                ax.axvline(temp_fre, color=c, linestyle='--',
                           label=f'{key}_{mul}', linewidth=1)
    ax.legend()


def plot_rms(data,  time_col='data_time', data_cols={'滤波有效值': 'rms_vdi', '总振动有效值': 'rms'}, title='有效值', observe_period=[], threshold_warn=10, threshold_error=16, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_cols:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    用plot_cols方法，只不过预设了一些值，方便调用
    '''
    return plot_cols(data,  time_col, data_cols, title, observe_period, threshold_warn, threshold_error, save_path,  figsize)


def plot_rms_dual(data: dict,  time_col='data_time', data_cols={'滤波有效值': 'rms_vdi', '总振动有效值': 'rms'}, title='有效值', observe_period=[], threshold_warn=10, threshold_error=16, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            dict，key是两张图的标题，value是对应的张表，包含时间，有效值的data_frame
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_dict:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    用plot_cols_dual方法，只不过预设了一些值，方便调用
    '''
    return plot_cols_dual(data,  time_col, data_cols, title, observe_period, threshold_warn, threshold_error, save_path,  figsize)


def plot_kurtosis(data,  time_col='data_time', data_cols={'峭度': 'kurtosis'}, title='峭度', observe_period=[], threshold_warn=8, threshold_error=None, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_cols:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    '''
    return plot_cols(data,  time_col, data_cols, title, observe_period, threshold_warn, threshold_error, save_path,  figsize)


def plot_kurtosis_dual(data: dict,  time_col='data_time', data_cols={'峭度': 'kurtosis'}, title='峭度', observe_period=[], threshold_warn=8, threshold_error=None, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            dict，key是两张图的标题，value是对应的张表，包含时间，有效值的data_frame
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_dict:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    '''
    return plot_cols_dual(data,  time_col, data_cols, title, observe_period, threshold_warn, threshold_error, save_path,  figsize)


def plot_cols(data,  time_col='data_time', data_cols={}, title='', observe_period=[], threshold_warn=None, threshold_error=None, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_cols:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    '''
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=18, color='#000000', y=0.93)
    ax = fig.subplots(1, 1)
    ax_plot_cols(ax,  data, time_col, data_cols, '', observe_period,
                 threshold_warn, threshold_error)

    fig.autofmt_xdate()
    fig_name = f'{save_path}/{title}.png'
    fig.savefig(fig_name, bbox_inches='tight')
    plt.close(fig)
    return fig_name


def plot_cols_dual(data: dict,  time_col='data_time', data_cols={}, title='', observe_period=[], threshold_warn=None, threshold_error=None, save_path='pic',  figsize=(20, 16)):
    '''
    @param data:            dict，key是两张图的标题，value是对应的张表，包含时间，有效值的data_frame
    @param data:            包含时间，有效值的data_frame
    @param time_col:        时间的列名
    @param data_dict:       key是legend的名字，value是有效值的列
    @param title:           标题
    @param observe_period:  观测区间
    @param threshold_warn:  告警阈值,为None不显示
    @param threshold_error: 故障阈值,为None不显示
    @param save_path:       存图路径
    @param figsize:         图片大小
    @return :               图片存储路径
    '''
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=18, color='#000000', y=0.93)
    axs = fig.subplots(1, 2)
    keys = data.keys()
    for ax, key in zip(axs, keys):
        ax_plot_cols(ax,  data[key], time_col, data_cols, key, observe_period,
                     threshold_warn, threshold_error)

    fig.autofmt_xdate()
    fig_name = f'{save_path}/{title}.png'
    fig.savefig(fig_name, bbox_inches='tight')
    plt.close(fig)
    return fig_name


def ax_plot_cols(ax, data, time_col='data_time', data_cols={}, title='', observe_period=[], threshold_warn=None, threshold_error=None):
    ax.tick_params(axis='x', labelsize=12)
    ax.set_ylabel('振动幅值mm/s^2', fontsize=15, color='#000000')
    ax.set_xlabel('时间', fontsize=15, color='#000000')
    for key, value in data_cols.items():
        ax.plot(data[time_col], data[value], label=key, linewidth=3)
    # 画告警故障阈值线
    if threshold_warn is not None:
        ax.axhline(threshold_warn, color='yellow',
                   linestyle='--', label='告警阈值', linewidth=3)
    if threshold_error is not None:
        ax.axhline(threshold_error, color='red',
                   linestyle='--', label='故障阈值', linewidth=3)
    # 设置观测区间
    if len(observe_period) == 2:
        filter_e = datetime.datetime.strptime(observe_period[0], "%Y-%m-%d")
        filter_s = datetime.datetime.strptime(
            observe_period[1], "%Y-%m-%d") + datetime.timedelta(1)
        ax.axvspan(filter_s, filter_e, color="yellow",
                   alpha=0.3, zorder=1, label='当前观测区间')
    ax.legend(loc=2, fontsize=18, labelcolor='#000000',
              ncol=1, edgecolor='#000000', facecolor='none')
    # 画转速
    ax_t = ax.twinx()
    ax_t.plot(data['data_time'], data['speed'], '--', label='高速轴转速', linewidth=0.5,
              color='darkgreen')

    ax_t.legend(loc=1, fontsize=18, labelcolor='#000000',
                ncol=1, edgecolor='#000000', facecolor='none')
    # 设置图片标题
    if title != '':
        ax.set_title(title, fontsize=18, color='#000000')
