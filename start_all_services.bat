@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%frontend_vue"

echo ========================================
echo Langchain-Chatchat one-click launcher
echo ========================================
echo.

where conda >nul 2>nul
if errorlevel 1 (
  echo [ERROR] conda not found in PATH.
  echo Please open Anaconda Prompt and run this script again.
  pause
  exit /b 1
)

echo [1/2] Starting backend (api + workers + langserve)...
start "chatchat-backend" cmd /k "cd /d \"%ROOT_DIR%\" && call conda activate chatchat && python start_server.py"

echo [2/2] Starting frontend (vite dev server)...
start "chatchat-frontend" cmd /k "cd /d \"%FRONTEND_DIR%\" && npm run dev"

echo.
echo Backend docs:   http://localhost:7861/docs
echo Frontend page:  http://localhost:5173
echo.
echo Two new terminal windows should be opened.
exit /b 0
