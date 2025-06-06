@echo off
echo Starting EditorialAgents Application...
echo.

REM Set project root directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Activate conda environment
echo Activating conda environment: DeepEdit
call conda activate DeepEdit
if errorlevel 1 (
    echo Error: Failed to activate conda environment DeepEdit
    echo Please make sure conda is installed and DeepEdit environment exists
    pause
    exit /b 1
)

REM Start backend service in new window
echo Starting backend server...
start "Backend Server" cmd /k "conda activate DeepEdit && cd /d "%PROJECT_DIR%" && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend service in new window
echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d "%PROJECT_DIR%\frontend-react" && npm run dev"

REM Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo EditorialAgents Application Started!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.

REM Open browser
start http://localhost:5173

echo.
echo Application is running!
echo Close the backend and frontend windows to stop the application.
echo.