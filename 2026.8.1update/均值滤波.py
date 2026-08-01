import numpy as np

def filter_mean(data, window_size=5):
    """
    均值滤波（滑动平均）
    参数:
        data: 输入信号
        window_size: 窗口大小（3-20）
    返回:
        滤波后的数据（长度与原始数据相同，边缘用边界值补齐，不截断）
    """
    # 参数校验
    if window_size < 3:
        window_size = 3
    if window_size > 20:
        window_size = 20

    # 空数据直接返回
    if len(data) == 0:
        return data.copy()

    # 如果数据长度小于窗口大小，调整窗口大小
    if len(data) < window_size:
        window_size = len(data)

    # 使用卷积实现滑动平均，边缘用边界值填充以保证输出长度不变
    # （这样均值滤波与高通/带通/SG等滤波器行为一致，不会引起数据长度不匹配）
    pad = window_size // 2
    padded = np.pad(data, (pad, window_size - 1 - pad), mode='edge')
    window = np.ones(window_size) / window_size
    filtered = np.convolve(padded, window, mode='valid')

    return filtered
