# -*- coding: utf-8 -*-
"""测试新增功能：均值滤波和去趋势项多选"""
import numpy as np
import sys
sys.path.append('.')
from app import filter_mean, apply_filters_chain, validate_filter_params

def test_mean_filter():
    """测试均值滤波"""
    print("测试均值滤波...")

    # 生成测试信号
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)

    # 测试窗口大小3
    result = filter_mean(data, window_size=3)
    assert len(result) == len(data), "均值滤波后长度改变"
    print("  [OK] 窗口大小3测试通过")

    # 测试窗口大小5
    result = filter_mean(data, window_size=5)
    assert len(result) == len(data), "均值滤波后长度改变"
    print("  [OK] 窗口大小5测试通过")

    # 测试窗口大小20（最大值）
    result = filter_mean(data, window_size=20)
    assert len(result) == len(data), "均值滤波后长度改变"
    print("  [OK] 窗口大小20测试通过")

    # 测试窗口大小超过范围（应自动限制）
    result = filter_mean(data, window_size=25)
    assert len(result) == len(data), "均值滤波后长度改变"
    print("  [OK] 超范围窗口自动限制测试通过")

def test_detrend_multiple():
    """测试去趋势项多选"""
    print("\n测试去趋势项多选...")

    # 生成有趋势的测试信号
    x = np.arange(100)
    data = 2.0 * x + 0.01 * x**2 + np.random.randn(100)

    # 测试单个去趋势项
    filters_config = [
        {'type': 'detrend', 'enabled': True, 'params': {'types': ['linear']}}
    ]
    result = apply_filters_chain(data, filters_config, 1000)
    assert len(result) == len(data), "滤波后长度改变"
    print("  [OK] 单个去趋势项测试通过")

    # 测试多个去趋势项（去均值 + 去线性）
    filters_config = [
        {'type': 'detrend', 'enabled': True, 'params': {'types': ['mean', 'linear']}}
    ]
    result = apply_filters_chain(data, filters_config, 1000)
    assert len(result) == len(data), "滤波后长度改变"
    print("  [OK] 去均值+去线性测试通过")

    # 测试全部去趋势项
    filters_config = [
        {'type': 'detrend', 'enabled': True, 'params': {'types': ['mean', 'linear', 'quadratic']}}
    ]
    result = apply_filters_chain(data, filters_config, 1000)
    assert len(result) == len(data), "滤波后长度改变"
    print("  [OK] 全部去趋势项测试通过")

def test_mean_filter_validation():
    """测试均值滤波参数校验"""
    print("\n测试均值滤波参数校验...")

    # 测试窗口太小
    filters_config = [
        {'type': 'mean', 'enabled': True, 'params': {'window_size': 2}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert not is_valid, "窗口太小应该校验失败"
    print("  [OK] 窗口太小校验通过")

    # 测试窗口太大
    filters_config = [
        {'type': 'mean', 'enabled': True, 'params': {'window_size': 25}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert not is_valid, "窗口太大应该校验失败"
    print("  [OK] 窗口太大校验通过")

    # 测试有效窗口
    filters_config = [
        {'type': 'mean', 'enabled': True, 'params': {'window_size': 10}}
    ]
    is_valid, error_msg = validate_filter_params(filters_config, 1000)
    assert is_valid, "有效窗口应该校验通过"
    print("  [OK] 有效窗口校验通过")

def test_combined_filters():
    """测试组合滤波（包括均值滤波和去趋势项多选）"""
    print("\n测试组合滤波...")

    # 生成复杂信号
    fs = 1000
    t = np.linspace(0, 1.0, fs, endpoint=False)
    signal = (2.0 * t +  # 线性趋势
              0.5 * t**2 +  # 二次趋势
              1.0 * np.sin(2 * np.pi * 50 * t) +  # 50Hz成分
              0.1 * np.random.randn(len(t)))  # 噪声

    # 组合滤波：去趋势项多选 + 均值滤波
    filters_config = [
        {
            'type': 'detrend',
            'enabled': True,
            'params': {'types': ['mean', 'linear', 'quadratic']}
        },
        {
            'type': 'mean',
            'enabled': True,
            'params': {'window_size': 5}
        }
    ]

    result = apply_filters_chain(signal, filters_config, fs)
    assert len(result) == len(signal), "滤波后长度改变"
    assert not np.isnan(result).any(), "包含NaN值"
    print("  [OK] 组合滤波测试通过")

def main():
    print("="*60)
    print("测试新增功能：均值滤波 + 去趋势项多选")
    print("="*60)

    try:
        test_mean_filter()
        test_detrend_multiple()
        test_mean_filter_validation()
        test_combined_filters()

        print("\n" + "="*60)
        print("[SUCCESS] 所有新功能测试通过！")
        print("="*60)

    except AssertionError as e:
        print(f"\n[ERROR] 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)