@echo off
REM master_start.bat - 主控版启动脚本
title 跨境电商智能体 - 主控版

echo 正在启动主控面板...
call .venv\Scripts\activate
set PYTHONPATH=%CD%
python -m master_panel.dashboard

pause