@echo off
chcp 65001 >nul
title 京盛传媒企业版智能体 - 启动助手
cd /d "%~dp0"

echo 检查虚拟环境...
if exist .venv\Scripts\activate (
  call .venv\Scripts\activate
) else (
  echo 创建虚拟环境并安装依赖...
  python -m venv .venv
  call .venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
)

:: 检测端口/占用
set PORT=8501
:checkport
netstat -ano | findstr :%PORT% >nul
if %errorlevel%==0 (
  echo 端口 %PORT% 被占用，尝试下一个...
  set /a PORT+=1
  goto checkport
)

echo 启动 Streamlit...
start "" cmd /c "streamlit run run_launcher.py --server.port %PORT%"

echo 启动调度器 (后台)...
start "" cmd /c "python scheduler.py"

timeout /t 2 >nul
start http://localhost:%PORT%

echo 启动完成，浏览器已打开。
pause
