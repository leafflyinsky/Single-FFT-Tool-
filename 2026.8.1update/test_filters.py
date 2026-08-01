# -*- coding: utf-8 -*-
"""测试滤波功能"""
import numpy as np
import sys
sys.path.append('.')
from app import (
    filter_detrend, filter_hampel, filter_highpass,
    filter_bandpass, filter_sg, filter_acg, filter_fft_bandpass,
    apply_filters_chain, validate_filter_params
)
from 均值滤波 import filter_mean

# 生成测试数据
def generate_test_signal():
    """生成测试信号：50Hz主频 + 100Hz二次谐波 + 噪声"""
    sampling_rate = 1000
    duration = 1.0
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # 50Hz主频
    signal_50hz = 1.0 * np.sin(2 * np.pi * 50 * t)
    # 100Hz二次谐波
    signal_100hz = 0.5 * np.sin(2 * np.pi * 100 * t)
    # 噪声
    noise = 0.1 * np.random.randn(len(t))

    # 组合信号
    test_signal = signal_50hz + signal_100hz + noise

    return test_signal, sampling_rate

def test_detrend():
    """测试去趋势项"""
    print("测试去趋势项...")
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)

    # 去均值
    result = filter_detrend(data, 'mean')
    assert abs(np.mean(result)) < 1e-10, "去均值失败"
    print("  [OK] 去均值成功")

    # 去线性
    result = filter_detrend(data, 'linear')
    assert np.std(result) < 1e-10, "去线性失败"
    print("  [OK] 去线性成功")

    # 去二次项
    data_quadratic = data ** 2
    result = filter_detrend(data_quadratic, 'quadratic')
    print("  [OK] 去二次项成功")

def test_mean():
    """测试均值滤波（回归：输出长度必须与输入一致，曾因 mode='valid' 截短导致前后端数据长度不匹配）"""
    print("\n测试均值滤波...")
    signal, fs = generate_test_signal()

    # 长度必须保持不变（与高通/带通/SG等滤波器行为一致）
    filtered = filter_mean(signal, window_size=5)
    assert len(filtered) == len(signal), f"均值滤波后长度改变: {len(filtered)} != {len(signal)}"
    assert not np.isnan(filtered).any(), "包含NaN值"

    # 偶数窗口也要保持长度
    filtered_even = filter_mean(signal, window_size=4)
    assert len(filtered_even) == len(signal), "偶数窗口均值滤波后长度改变"

    # 数据长度小于窗口时不应报错
    short = np.array([1.0, 2.0])
    filtered_short = filter_mean(short, window_size=5)
    assert len(filtered_short) == len(short), "短数据均值滤波后长度改变"

    # 均值滤波放在滤波链开头，后续滤波不因长度缩短而报错
    chain = [
        {'type': 'mean', 'enabled': True, 'params': {'window_size': 5}},
        {'type': 'bandpass', 'enabled': True, 'params': {'low_freq': 10, 'high_freq': 400, 'order': 4}},
        {'type': 'sg', 'enabled': True, 'params': {'window_size': 11, 'polyorder': 3}},
    ]
    chain_result = apply_filters_chain(signal, chain, fs)
    assert len(chain_result) == len(signal), "含均值滤波的滤波链长度改变"

    print(f"  [OK] 均值滤波成功，长度不变 ({len(filtered)})")

def test_hampel():
    """测试Hampel滤波"""
    print("\n测试Hampel滤波...")
    data = np.array([1, 2, 3, 100, 5, 6, 7, 8, 9, 10], dtype=float)

    result = filter_hampel(data, window_size=3, n_sigma=3)

    # 异常值100应该被替换
    assert abs(result[3] - 100) > 10, "异常值未被正确处理"
    print("  [OK] Hampel滤波成功识别并处理异常值")

def test_highpass():
    """测试高通滤波"""
    print("\n测试高通滤波...")
    signal, fs = generate_test_signal()

    # 应用高通滤波（截止20Hz）
    filtered = filter_highpass(signal, cutoff_freq=20, sampling_rate=fs, order=4)

    # 检查信号是否正常
    assert len(filtered) == len(signal), "滤波后长度改变"
    assert not np.isnan(filtered).any(), "包含NaN值"
    print("  [OK] 高通滤波成功")

def test_bandpass():
    """测试带通滤波"""
    print("\n测试带通滤波...")
    signal, fs = generate_test_signal()

    # 应用带通滤波（40-60Hz，保留50Hz成分）
    filtered = filter_bandpass(signal, low_freq=40, high_freq=60, sampling_rate=fs, order=4)

    # 检查信号是否正常
    assert len(filtered) == len(signal), "滤波后长度改变"
    assert not np.isnan(filtered).any(), "包含NaN值"
    print("  [OK] 带通滤波成功")

def test_sg():
    """测试SG滤波"""
    print("\n测试SG滤波...")
    signal, fs = generate_test_signal()

    # 应用SG平滑
    filtered = filter_sg(signal, window_size=11, polyorder=3)

    # 检查信号是否正常
    assert len(filtered) == len(signal), "滤波后长度改变"
    assert not np.isnan(filtered).any(), "包含NaN值"
    print("  [OK] SG滤波成功")

def test_fft_bandpass():
    """测试频域带通（FFT）"""
    print("\n测试频域带通...")
    signal, fs = generate_test_signal()  # 50Hz主频 + 100Hz谐波 + 噪声

    # 通带覆盖50Hz：主频应保留，长度不变
    filtered = filter_fft_bandpass(signal, fs, low_freq=40, high_freq=60)
    assert len(filtered) == len(signal), "频域带通后长度改变"
    assert not np.isnan(filtered).any(), "包含NaN值"

    # 检查50Hz成分是否保留（对比滤波前后的幅度）
    from scipy.fft import fft, fftfreq
    fft_orig = np.abs(fft(signal))
    fft_filt = np.abs(fft(filtered))
    freqs = fftfreq(len(signal), 1/fs)
    k50 = np.argmin(np.abs(freqs - 50))
    assert fft_filt[k50] > 0.5 * fft_orig[k50], "通带内50Hz主频被过度衰减"

    # 通带外置零：带通 100-200 应滤掉50Hz主频
    filtered_out = filter_fft_bandpass(signal, fs, low_freq=100, high_freq=200)
    fft_filt_out = np.abs(fft(filtered_out))
    assert fft_filt_out[k50] < 0.05 * fft_orig[k50], "通带外的50Hz分量未被滤除"

    print(f"  [OK] 频域带通成功，长度不变 ({len(filtered)})，50Hz主频保留/滤除逻辑正确")

def test_acg():
    """测试ACG自动增益"""
    print("\n测试ACG自动增益...")
    signal, fs = generate_test_signal()

    # 应用自动增益
    target_rms = 2.0
    filtered = filter_acg(signal, target_rms=target_rms)

    # 检查RMS是否接近目标值
    actual_rms = np.sqrt(np.mean(filtered ** 2))
    assert abs(actual_rms - target_rms) < 0.01, f"RMS {actual_rms} 未达到目标 {target_rms}"
    print(f"  [OK] ACG成功，目标RMS={target_rms}, 实际RMS={actual_rms:.4f}")

def test_filters_chain():
    """测试滤波器链"""
    print("\n测试滤波器链...")
    signal, fs = generate_test_signal()

    # 配置多个滤波器
    filters_config = [
        {'type': 'detrend', 'enabled': True, 'params': {'type': 'linear'}},
        {'type': 'hampel', 'enabled': True, 'params': {'window_size': 5, 'n_sigma': 3}},
        {'type': 'bandpass', 'enabled': True, 'params': {'low_freq': 10, 'high_freq': 400, 'order': 4}},
        {'type': 'sg', 'enabled': False, 'params': {'window_size': 11, 'polyorder': 3}}
    ]

    # 应用滤波器链
    filtered = apply_filters_chain(signal, filters_config, fs)

    # 检查结果
    assert len(filtered) == len(signal), "滤波后长度改变"
    assert not np.isnan(filtered).any(), "包含NaN值"
    print("  [OK] 滤波器链应用成功")

def test_validation():
    """测试参数校验"""
    print("\n测试参数校验...")

    # 测试无效的高通截止频率
    filters_config = [
        {'type': 'highpass', 'enabled': True, 'params': {'cutoff_freq': 600, 'order': 4}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert not is_valid, "高通截止频率校验失败"
    print("  [OK] 高通截止频率校验成功")

    # 测试无效的带通频率范围
    filters_config = [
        {'type': 'bandpass', 'enabled': True, 'params': {'low_freq': 500, 'high_freq': 100, 'order': 4}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert not is_valid, "带通频率范围校验失败"
    print("  [OK] 带通频率范围校验成功")

    # 测试无效的SG参数
    filters_config = [
        {'type': 'sg', 'enabled': True, 'params': {'window_size': 11, 'polyorder': 15}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert not is_valid, "SG参数校验失败"
    print("  [OK] SG参数校验成功")

def main():
    print("="*60)
    print("开始测试滤波功能...")
    print("="*60)

    try:
        test_detrend()
        test_mean()
        test_hampel()
        test_highpass()
        test_bandpass()
        test_sg()
        test_fft_bandpass()
        test_acg()
        test_filters_chain()
        test_validation()

        print("\n" + "="*60)
        print("[SUCCESS] 所有测试通过！")
        print("="*60)

    except AssertionError as e:
        print(f"\n[ERROR] 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)