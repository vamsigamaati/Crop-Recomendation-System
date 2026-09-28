@echo off
echo ====================================================
echo   AgroAI - Crop Recommendation System Launcher
echo ====================================================
echo.
echo Running download_data.py to check dataset...
python src/download_data.py
if %ERRORLEVEL% NEQ 0 (
    echo Error downloading dataset. Exiting.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo Running train.py to build ML models...
python src/train.py
if %ERRORLEVEL% NEQ 0 (
    echo Error training models. Exiting.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo Starting Flask server...
echo Access the dashboard at http://127.0.0.1:5000
python src/app.py
pause
