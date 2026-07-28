#!/bin/bash
echo "========================================"
echo "   振动信号分析工具 - 启动脚本"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "[OK] Python环境检测成功"
echo ""

# 安装依赖
echo "正在安装依赖包..."
pip3 install -r requirements.txt -q

echo "[OK] 依赖安装完成"
echo ""

echo "========================================"
echo "   服务器启动中..."
echo "   请在浏览器打开: http://localhost:5000"
echo "========================================"
echo ""

python3 app.py