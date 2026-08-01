"""
生成演示用的振动信号数据
包含主频50Hz，并添加一些噪声
"""

import numpy as np

# 设置参数
sampling_rate = 1000  # 采样率 1000 Hz
duration = 1.0  # 时长 1 秒
n_samples = int(sampling_rate * duration)  # 1000个采样点

# 时间轴
t = np.linspace(0, duration, n_samples, endpoint=False)

# 生成信号：主频50Hz + 二次谐波100Hz + 噪声
main_freq = 50  # 主频 50 Hz
second_harmonic = 100  # 二次谐波

signal = (
    1.0 * np.sin(2 * np.pi * main_freq * t) +  # 主频成分
    0.3 * np.sin(2 * np.pi * second_harmonic * t) +  # 二次谐波
    0.1 * np.random.randn(n_samples)  # 随机噪声
)

# 保存为CSV，所有数据在第一行
np.savetxt('demo_data.csv', signal, delimiter=',')

print("[OK] 已生成演示数据文件: demo_data.csv")
print(f"  - 采样率: {sampling_rate} Hz")
print(f"  - 数据点数: {n_samples}")
print(f"  - 主频: {main_freq} Hz")
print(f"  - 二次谐波: {second_harmonic} Hz")
print(f"\n使用方法:")
print(f"  1. 在网页中选择采样率: {sampling_rate} Hz")
print(f"  2. 上传 demo_data.csv 文件")
print(f"  3. 点击'开始分析'按钮")