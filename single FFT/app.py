"""
振动信号分析Web工具 - Flask后端
支持：FFT频谱分析、主频检测、时域特征提取
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy import signal, stats
import pandas as pd
import io
import json
import sys
import os

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

def calculate_energy_ratio(freqs, magnitude, dominant_freq, bandwidth=5):
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
    """分析上传的CSV文件"""
    try:
        # 检查文件是否上传
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 获取采样率参数（默认1000Hz）
        sampling_rate = int(request.form.get('sampling_rate', 1000))

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

        # 执行分析
        result, freqs, magnitude = analyze_vibration_signal(data, sampling_rate)

        # 准备图表数据
        # 时域波形数据（采样以提高前端性能）
        time = np.arange(len(data)) / sampling_rate
        waveform_data = {
            'time': time.tolist(),
            'amplitude': data.tolist()
        }

        # 频谱数据（限制频率范围）
        max_freq = sampling_rate / 2  # Nyquist频率
        freq_mask = freqs <= max_freq
        spectrum_data = {
            'frequency': freqs[freq_mask].tolist(),
            'magnitude': magnitude[freq_mask].tolist()
        }

        return jsonify({
            'success': True,
            'result': result,
            'waveform': waveform_data,
            'spectrum': spectrum_data
        })

    except Exception as e:
        return jsonify({'error': f'分析过程出错: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """演示页面，使用模拟数据"""
    return render_template('demo.html')

if __name__ == '__main__':
    print("="*60)
    print("振动信号分析工具已启动")
    print("请在浏览器中打开: http://localhost:5000")
    print("="*60)
    app.run(debug=False, port=5000, use_reloader=False)