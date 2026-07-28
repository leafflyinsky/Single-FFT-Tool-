@echo off
chcp 65001 >nul
echo ========================================
echo    振动信号分析工具 - 启动脚本
echo ========================================
echo.
echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b
)

echo [OK] Python环境检测成功
echo.
echo 正在安装依赖包...
pip install -r requirements.txt -q

echo [OK] 依赖安装完成
echo.
echo ========================================
echo    服务器启动中...
echo    请在浏览器打开: http://localhost:5000
echo ========================================
echo.

python app.py

pause