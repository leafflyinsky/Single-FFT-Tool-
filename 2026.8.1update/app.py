"""
振动信号分析Web工具 - Flask后端
支持：FFT频谱分析、主频检测、时域特征提取
"""

from flask import Flask, render_template, request, jsonify, Response
import numpy as np
from scipy import signal, stats
import pandas as pd
import io
import json
import sys
import os
import csv
from datetime import datetime

# 从独立模块导入均值滤波函数
from 均值滤波 import filter_mean

# PyInstaller 打包后的资源路径处理
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发和打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

# 设置 Flask 的模板路径和静态文件路径
template_folder = get_resource_path('templates')
static_folder = get_resource_path('static')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

def calculate_rms(data):
    """计算均方根值"""
    return np.sqrt(np.mean(data ** 2))

def calculate_crest_factor(data):
    """计算峰值因子 (峰值/RMS)"""
    peak = np.max(np.abs(data))
    rms = calculate_rms(data)
    return peak / rms if rms > 0 else 0

def calculate_kurtosis(data):
    """计算峭度"""
    return stats.kurtosis(data, fisher=False)

def calculate_spectral_centroid(freqs, magnitude):
    """计算频谱中心"""
    return np.sum(freqs * magnitude) / np.sum(magnitude)

def find_dominant_frequency(freqs, magnitude, sampling_rate):
    """寻找主频"""
    # 只分析正频率部分
    positive_freq_idx = freqs > 0
    positive_freqs = freqs[positive_freq_idx]
    positive_magnitude = magnitude[positive_freq_idx]

    # 找到幅值最大的频率
    max_idx = np.argmax(positive_magnitude)
    dominant_freq = positive_freqs[max_idx]

    return dominant_freq, positive_magnitude[max_idx]

# ==================== 滤波处理函数 ====================

def filter_detrend(data, detrend_type='linear'):
    """
    去趋势项
    参数:
        data: 输入信号
        detrend_type: 'mean'去均值, 'linear'去线性趋势, 'quadratic'去二次趋势
    """
    if detrend_type == 'mean':
        return data - np.mean(data)
    elif detrend_type == 'linear':
        return signal.detrend(data, type='linear')
    elif detrend_type == 'quadratic':
        # 手动实现二次去趋势项
        x = np.arange(len(data))
        # 拟合二次多项式
        coeffs = np.polyfit(x, data, 2)
        trend = np.polyval(coeffs, x)
        return data - trend
    else:
        return data


def filter_hampel(data, window_size=5, n_sigma=3):
    """
    Hampel滤波器 - 异常值检测与替换
    参数:
        data: 输入信号
        window_size: 窗口大小（奇数）
        n_sigma: 阈值倍数（超过中位数±n_sigma*MAD的点视为异常值）
    返回:
        滤波后的数据
    """
    # 确保窗口大小为奇数
    if window_size % 2 == 0:
        window_size += 1

    data_filtered = data.copy()
    half_window = window_size // 2
    n = len(data)

    for i in range(n):
        # 定义窗口范围
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)

        # 提取窗口数据
        window = data[start:end]

        # 计算中位数和MAD（中位数绝对偏差）
        median = np.median(window)
        mad = np.median(np.abs(window - median))

        # 标准化MAD（1.4826是正态分布的缩放因子）
        if mad > 0:
            sigma = 1.4826 * mad
        else:
            sigma = 0

        # 检测异常值并用中位数替换
        if sigma > 0 and np.abs(data[i] - median) > n_sigma * sigma:
            data_filtered[i] = median

    return data_filtered

def filter_highpass(data, cutoff_freq, sampling_rate, order=4):
    """
    高通滤波器
    参数:
        data: 输入信号
        cutoff_freq: 截止频率 (Hz)
        sampling_rate: 采样率 (Hz)
        order: 滤波器阶数
    返回:
        滤波后的数据
    """
    nyquist = sampling_rate / 2.0

    # 归一化截止频率
    normalized_cutoff = cutoff_freq / nyquist

    # 确保截止频率有效
    if normalized_cutoff >= 1.0:
        raise ValueError(f"高通滤波截止频率 {cutoff_freq}Hz 超过奈奎斯特频率 {nyquist}Hz")
    if normalized_cutoff <= 0:
        raise ValueError(f"高通滤波截止频率必须大于0")

    # 设计Butterworth高通滤波器
    b, a = signal.butter(order, normalized_cutoff, btype='high', analog=False)

    # 使用filtfilt实现零相位滤波
    return signal.filtfilt(b, a, data)

def filter_bandpass(data, low_freq, high_freq, sampling_rate, order=4):
    """
    带通滤波器
    参数:
        data: 输入信号
        low_freq: 低频截止 (Hz)
        high_freq: 高频截止 (Hz)
        sampling_rate: 采样率 (Hz)
        order: 滤波器阶数
    返回:
        滤波后的数据
    """
    nyquist = sampling_rate / 2.0

    # 归一化频率
    normalized_low = low_freq / nyquist
    normalized_high = high_freq / nyquist

    # 参数校验
    if normalized_low >= 1.0 or normalized_high >= 1.0:
        raise ValueError(f"带通滤波高频截止 {high_freq}Hz 超过奈奎斯特频率 {nyquist}Hz")
    if normalized_low <= 0:
        raise ValueError(f"带通滤波低频截止必须大于0")
    if normalized_low >= normalized_high:
        raise ValueError(f"带通滤波低频截止 {low_freq}Hz 必须小于高频截止 {high_freq}Hz")

    # 设计Butterworth带通滤波器
    b, a = signal.butter(order, [normalized_low, normalized_high], btype='band', analog=False)

    # 使用filtfilt实现零相位滤波
    return signal.filtfilt(b, a, data)

def filter_sg(data, window_size=11, polyorder=3):
    """
    Savitzky-Golay平滑滤波
    参数:
        data: 输入信号
        window_size: 窗口大小（奇数）
        polyorder: 多项式阶数
    返回:
        滤波后的数据
    """
    # 确保窗口大小为奇数
    if window_size % 2 == 0:
        window_size += 1

    # 参数校验
    if polyorder >= window_size:
        raise ValueError(f"SG滤波多项式阶数 {polyorder} 必须小于窗口大小 {window_size}")

    return signal.savgol_filter(data, window_size, polyorder)

def filter_acg(data, target_rms=1.0):
    """
    自动增益控制 (Automatic Gain Control)
    调整信号幅度到目标RMS值
    参数:
        data: 输入信号
        target_rms: 目标RMS值
    返回:
        增益调整后的数据
    """
    current_rms = calculate_rms(data)

    if current_rms > 0:
        gain = target_rms / current_rms
        return data * gain
    else:
        return data

def filter_frequency_domain_integration(data, fs, cutoff_freq=10, dominant_freq=16.6, high_freq_ratio=2):
    """
    频域积分滤波器 - 将加速度信号转换为位移信号
    参数:
        data: 输入加速度信号
        fs: 采样率 (Hz)
        cutoff_freq: 低频截止频率 (Hz)，默认10Hz
        dominant_freq: 主频 (Hz)，默认16.6Hz
        high_freq_ratio: 高频比率，高频截止=主频×high_freq_ratio，默认2
    返回:
        积分后的位移信号
    """
    from scipy.fft import fft, ifft, fftfreq

    N = len(data)
    if N == 0:
        return np.array([])

    # 计算频率参数
    df = fs / N
    nyquist = fs / 2

    # 参数合理化处理
    low_freq = cutoff_freq

    # 截止频率不能低于频率分辨率
    if low_freq < df:
        low_freq = df

    # 如果未指定主频，使用截止频率
    if dominant_freq <= 0:
        dominant_freq = low_freq

    # 计算高频截止频率
    high_freq = dominant_freq * high_freq_ratio

    # 保护：不能超过Nyquist频率的95%
    high_freq = min(high_freq, nyquist * 0.95)

    # 确保通带有效
    if high_freq <= low_freq:
        high_freq = min(low_freq * 2.0, nyquist * 0.95)

    # 执行FFT
    fft_result = fft(data)
    freqs = fftfreq(N, 1/fs)

    # 频域处理
    for k in range(len(fft_result)):
        freq = abs(freqs[k])

        # 检查是否在通带内
        in_passband = (freq >= low_freq and freq <= high_freq)

        # 检查是否为DC或极低频（数值稳定性）
        is_dc_or_near_dc = (freq < 1e-12)

        # 不在通带内或是DC分量，置零
        if not in_passband or is_dc_or_near_dc:
            fft_result[k] = 0.0
            continue

        # 频域积分（加速度→位移：除以 -ω²）
        omega = 2 * np.pi * freq
        denom = -(omega * omega)  # 二阶积分的传递函数

        # 高频衰减（抗混叠保护）
        atten_factor = 1.0
        if freq > 0.4 * nyquist:
            # 使用smoothstep过渡
            t = (freq - 0.4 * nyquist) / (0.6 * nyquist)
            t = max(0.0, min(1.0, t))
            atten_factor = 1.0 - t * t * (3.0 - 2.0 * t)  # smoothstep

        # 应用积分因子
        scale = atten_factor / denom
        fft_result[k] = fft_result[k] * scale

    # 执行逆FFT
    displacement = ifft(fft_result)

    # 返回实部
    return np.real(displacement)

def filter_fft_bandpass(data, fs, low_freq=10, high_freq=500):
    """
    频域带通滤波器 - 在频域直接截取指定频率范围
    对信号做FFT，只保留 [low_freq, high_freq] 范围内的频率分量，其余置零，再逆FFT。
    相比时域带通无相位失真、过渡带更陡（矩形通带）。
    参数:
        data: 输入信号
        fs: 采样率 (Hz)
        low_freq: 低频截止频率 (Hz)
        high_freq: 高频截止频率 (Hz)
    返回:
        带通滤波后的信号（长度与输入一致）
    """
    from scipy.fft import fft, ifft, fftfreq

    N = len(data)
    if N == 0:
        return np.array([])

    # 计算频率参数
    df = fs / N
    nyquist = fs / 2

    # 参数合理化处理
    low_freq = float(low_freq)
    high_freq = float(high_freq)

    # 低频截止不能低于频率分辨率
    if low_freq < df:
        low_freq = df

    # 高频截止不能超过Nyquist频率的95%
    high_freq = min(high_freq, nyquist * 0.95)

    # 确保通带有效
    if high_freq <= low_freq:
        high_freq = min(low_freq * 2.0, nyquist * 0.95)

    # 执行FFT
    fft_result = fft(data)
    freqs = fftfreq(N, 1/fs)

    # 通带外的频率分量置零
    for k in range(len(fft_result)):
        freq = abs(freqs[k])

        # 检查是否在通带内
        in_passband = (freq >= low_freq and freq <= high_freq)

        # 检查是否为DC或极低频（数值稳定性）
        is_dc_or_near_dc = (freq < 1e-12)

        # 不在通带内或是DC分量，置零
        if not in_passband or is_dc_or_near_dc:
            fft_result[k] = 0.0

    # 执行逆FFT
    filtered = ifft(fft_result)

    # 返回实部
    return np.real(filtered)

def apply_filters_chain(data, filters_config, sampling_rate):
    """
    按顺序应用多个滤波器
    """
    filtered_data = data.copy()

    for filter_item in filters_config:
        if not filter_item.get('enabled', False):
            continue

        filter_type = filter_item['type']
        params = filter_item.get('params', {})

        try:
            if filter_type == 'detrend':
                # 去趋势项支持多选：params['types']是一个列表
                detrend_types = params.get('types', ['linear'])
                if isinstance(detrend_types, str):
                    detrend_types = [detrend_types]

                # 依次应用所有选中的去趋势项
                for detrend_type in detrend_types:
                    filtered_data = filter_detrend(filtered_data, detrend_type)

            elif filter_type == 'mean':
                window_size = params.get('window_size', 5)
                filtered_data = filter_mean(filtered_data, window_size)

            elif filter_type == 'hampel':
                window_size = params.get('window_size', 5)
                n_sigma = params.get('n_sigma', 3)
                filtered_data = filter_hampel(filtered_data, window_size, n_sigma)

            elif filter_type == 'highpass':
                cutoff_freq = params.get('cutoff_freq', 10)
                order = params.get('order', 4)
                filtered_data = filter_highpass(filtered_data, cutoff_freq, sampling_rate, order)

            elif filter_type == 'bandpass':
                low_freq = params.get('low_freq', 10)
                high_freq = params.get('high_freq', 500)
                order = params.get('order', 4)
                filtered_data = filter_bandpass(filtered_data, low_freq, high_freq, sampling_rate, order)

            elif filter_type == 'fft_bandpass':
                low_freq = params.get('low_freq', 10)
                high_freq = params.get('high_freq', 500)
                filtered_data = filter_fft_bandpass(filtered_data, sampling_rate, low_freq, high_freq)

            elif filter_type == 'sg':
                window_size = params.get('window_size', 11)
                polyorder = params.get('polyorder', 3)
                filtered_data = filter_sg(filtered_data, window_size, polyorder)

            elif filter_type == 'acg':
                target_rms = params.get('target_rms', 1.0)
                filtered_data = filter_acg(filtered_data, target_rms)

            elif filter_type == 'freq_integration':
                cutoff_freq = params.get('cutoff_freq', 10)
                dominant_freq = params.get('dominant_freq', 16.6)
                high_freq_ratio = params.get('high_freq_ratio', 2)
                filtered_data = filter_frequency_domain_integration(
                    filtered_data, sampling_rate, cutoff_freq, dominant_freq, high_freq_ratio
                )

        except Exception as e:
            raise ValueError(f"滤波器 {filter_type} 处理失败: {str(e)}")

    return filtered_data

def validate_filter_params(filters_config, sampling_rate):
    """
    校验滤波器参数
    返回:
        (is_valid, error_message)
    """
    nyquist = sampling_rate / 2.0

    for filter_item in filters_config:
        if not filter_item.get('enabled', False):
            continue

        filter_type = filter_item['type']
        params = filter_item.get('params', {})

        # 均值滤波参数校验
        if filter_type == 'mean':
            window_size = params.get('window_size', 5)
            if window_size < 3 or window_size > 20:
                return False, f"均值滤波窗口大小必须在3-20之间，当前为 {window_size}"

        # 高通滤波参数校验
        elif filter_type == 'highpass':
            cutoff_freq = params.get('cutoff_freq', 10)
            if cutoff_freq >= nyquist:
                return False, f"高通滤波截止频率 {cutoff_freq}Hz 不能超过奈奎斯特频率 {nyquist}Hz"
            if cutoff_freq <= 0:
                return False, f"高通滤波截止频率必须大于0Hz"

        # 带通滤波参数校验
        elif filter_type == 'bandpass':
            low_freq = params.get('low_freq', 10)
            high_freq = params.get('high_freq', 500)

            if low_freq <= 0:
                return False, f"带通滤波低频截止必须大于0Hz"
            if high_freq >= nyquist:
                return False, f"带通滤波高频截止 {high_freq}Hz 不能超过奈奎斯特频率 {nyquist}Hz"
            if low_freq >= high_freq:
                return False, f"带通滤波低频截止 {low_freq}Hz 必须小于高频截止 {high_freq}Hz"

        # 频域带通滤波参数校验
        elif filter_type == 'fft_bandpass':
            low_freq = params.get('low_freq', 10)
            high_freq = params.get('high_freq', 500)

            if low_freq <= 0:
                return False, f"频域带通低频截止必须大于0Hz"
            if high_freq >= nyquist:
                return False, f"频域带通高频截止 {high_freq}Hz 不能超过奈奎斯特频率 {nyquist}Hz"
            if low_freq >= high_freq:
                return False, f"频域带通低频截止 {low_freq}Hz 必须小于高频截止 {high_freq}Hz"

        # SG滤波参数校验
        elif filter_type == 'sg':
            window_size = params.get('window_size', 11)
            polyorder = params.get('polyorder', 3)

            if window_size % 2 == 0:
                return False, f"SG滤波窗口大小必须是奇数，当前为 {window_size}"
            if polyorder >= window_size:
                return False, f"SG滤波多项式阶数 {polyorder} 必须小于窗口大小 {window_size}"

        # Hampel滤波参数校验
        elif filter_type == 'hampel':
            window_size = params.get('window_size', 5)
            if window_size < 3:
                return False, f"Hampel滤波窗口大小至少为3"

        # 频域积分参数校验
        elif filter_type == 'freq_integration':
            cutoff_freq = params.get('cutoff_freq', 10)
            dominant_freq = params.get('dominant_freq', 16.6)
            high_freq_ratio = params.get('high_freq_ratio', 2)

            if cutoff_freq <= 0:
                return False, f"频域积分低频截止必须大于0Hz"
            if cutoff_freq >= nyquist:
                return False, f"频域积分低频截止 {cutoff_freq}Hz 不能超过奈奎斯特频率 {nyquist}Hz"
            if dominant_freq < 0:
                return False, f"频域积分主频不能为负数"
            if high_freq_ratio <= 0:
                return False, f"频域积分高频比率必须大于0"

            # 检查高频截止是否有效
            high_freq = dominant_freq * high_freq_ratio if dominant_freq > 0 else cutoff_freq * high_freq_ratio
            if high_freq >= nyquist:
                return False, f"频域积分高频截止 {high_freq:.1f}Hz 不能超过奈奎斯特频率 {nyquist}Hz"

    return True, ""

def calculate_energy_ratio(freqs, magnitude, dominant_freq, bandwidth=2):
    """计算主频能量占比"""
    # 总能量
    total_energy = np.sum(magnitude ** 2)

    # 主频附近的能量（带宽内的能量）
    freq_mask = (freqs >= dominant_freq - bandwidth) & (freqs <= dominant_freq + bandwidth)
    dominant_energy = np.sum(magnitude[freq_mask] ** 2)

    return (dominant_energy / total_energy * 100) if total_energy > 0 else 0

def analyze_vibration_signal(data, sampling_rate=1000):
    """
    完整的振动信号分析

    参数:
        data: 加速度数据数组
        sampling_rate: 采样率 (Hz)

    返回:
        包含所有分析结果的字典
    """
    n = len(data)

    # 1. 时域分析
    rms_value = calculate_rms(data)
    crest_factor = calculate_crest_factor(data)
    kurtosis_value = calculate_kurtosis(data)
    peak_value = np.max(np.abs(data))
    mean_value = np.mean(data)
    std_value = np.std(data)

    # 2. FFT频谱分析
    # 使用Hanning窗减少频谱泄漏
    window = np.hanning(n)
    windowed_data = data * window

    # FFT计算
    fft_result = np.fft.fft(windowed_data)
    freqs = np.fft.fftfreq(n, 1/sampling_rate)

    # 只取正频率部分
    positive_freq_idx = freqs >= 0
    freqs_positive = freqs[positive_freq_idx]
    magnitude = np.abs(fft_result[positive_freq_idx]) * 2 / n  # 归一化

    # 3. 主频分析
    dominant_freq, dominant_magnitude = find_dominant_frequency(
        freqs_positive, magnitude, sampling_rate
    )

    # 4. 主频能量占比
    energy_ratio = calculate_energy_ratio(freqs_positive, magnitude, dominant_freq)

    # 5. 频谱中心
    spectral_centroid = calculate_spectral_centroid(freqs_positive, magnitude)

    # 6. 前N个主要频率成分
    top_n = 5
    top_indices = np.argsort(magnitude[1:])[-top_n:][::-1] + 1  # 跳过DC分量
    top_frequencies = freqs_positive[top_indices].tolist()
    top_magnitudes = magnitude[top_indices].tolist()

    # 准备返回结果
    result = {
        'time_domain': {
            'rms': float(rms_value),
            'peak': float(peak_value),
            'crest_factor': float(crest_factor),
            'kurtosis': float(kurtosis_value),
            'mean': float(mean_value),
            'std': float(std_value)
        },
        'frequency_domain': {
            'dominant_freq': float(dominant_freq),
            'dominant_magnitude': float(dominant_magnitude),
            'energy_ratio': float(energy_ratio),
            'spectral_centroid': float(spectral_centroid),
            'top_frequencies': top_frequencies,
            'top_magnitudes': top_magnitudes
        },
        'signal_info': {
            'length': n,
            'sampling_rate': sampling_rate,
            'duration': n / sampling_rate
        }
    }

    return result, freqs_positive, magnitude

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析上传的CSV文件，支持滤波"""
    try:
        # 检查文件是否上传
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 获取采样率参数（默认1000Hz）
        sampling_rate = int(request.form.get('sampling_rate', 1000))

        # 获取滤波器配置（如果有）
        filters_config = []
        if 'filters' in request.form:
            try:
                filters_config = json.loads(request.form.get('filters'))
            except:
                filters_config = []

        # 读取CSV文件
        content = file.read().decode('utf-8')

        # 尝试解析数据
        try:
            # 首先尝试用pandas读取
            df = pd.read_csv(io.StringIO(content), header=None)

            # 如果数据在第一行
            if df.shape[0] == 1:
                data = df.iloc[0].values
            else:
                # 如果有多行，取第一列或合并所有数据
                data = df.iloc[:, 0].values

            # 确保数据是数值型
            data = pd.to_numeric(data, errors='coerce')
            data = data[~np.isnan(data)]  # 移除NaN值

            if len(data) == 0:
                return jsonify({'error': '无法从文件中解析出有效数据'}), 400

        except Exception as e:
            return jsonify({'error': f'文件解析错误: {str(e)}'}), 400

        # 校验滤波器参数
        if filters_config:
            is_valid, error_msg = validate_filter_params(filters_config, sampling_rate)
            if not is_valid:
                return jsonify({'error': error_msg}), 400

        # 原始信号分析
        original_result, original_freqs, original_magnitude = analyze_vibration_signal(data, sampling_rate)

        # 应用滤波器（如果配置了）
        filtered_data = data.copy()
        if filters_config:
            try:
                filtered_data = apply_filters_chain(data, filters_config, sampling_rate)
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        # 滤波后信号分析
        filtered_result, filtered_freqs, filtered_magnitude = analyze_vibration_signal(filtered_data, sampling_rate)

        # 准备图表数据
        # 时域波形数据（采样以提高前端性能）
        time = np.arange(len(data)) / sampling_rate
        original_waveform = {
            'time': time.tolist(),
            'amplitude': data.tolist()
        }
        filtered_waveform = {
            'time': time.tolist(),
            'amplitude': filtered_data.tolist()
        }

        # 频谱数据（限制频率范围）
        max_freq = sampling_rate / 2  # Nyquist频率
        freq_mask = original_freqs <= max_freq
        original_spectrum = {
            'frequency': original_freqs[freq_mask].tolist(),
            'magnitude': original_magnitude[freq_mask].tolist()
        }
        filtered_spectrum = {
            'frequency': filtered_freqs[freq_mask].tolist(),
            'magnitude': filtered_magnitude[freq_mask].tolist()
        }

        return jsonify({
            'success': True,
            'original_result': original_result,
            'filtered_result': filtered_result,
            'original_waveform': original_waveform,
            'filtered_waveform': filtered_waveform,
            'original_spectrum': original_spectrum,
            'filtered_spectrum': filtered_spectrum,
            'filters_applied': len([f for f in filters_config if f.get('enabled', False)]) > 0
        })

    except Exception as e:
        return jsonify({'error': f'分析过程出错: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """演示页面，使用模拟数据"""
    return render_template('demo.html')

@app.route('/export', methods=['POST'])
def export_csv():
    """导出滤波后的数据为CSV"""
    try:
        # 获取数据
        data = request.json

        if not data or 'filtered_data' not in data:
            return jsonify({'error': '没有数据可导出'}), 400

        filtered_data = data['filtered_data']
        sampling_rate = data.get('sampling_rate', 1000)

        # 创建CSV内容
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(['Time (s)', 'Amplitude'])

        # 写入数据
        for i, amp in enumerate(filtered_data):
            time = i / sampling_rate
            writer.writerow([f'{time:.6f}', f'{amp:.6f}'])

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'filtered_signal_{timestamp}.csv'

        # 返回CSV文件
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("="*60)
    print("振动信号分析工具已启动")
    print("请在浏览器中打开: http://localhost:8080")
    print("="*60)
    app.run(debug=False, port=8080, use_reloader=False)