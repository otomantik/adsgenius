@echo off
echo ========================================
echo   Marketing Intelligence Platform
echo   Starting Application...
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python...
)

echo.
echo Starting Streamlit application...
echo.
echo ========================================
echo   Application will open in your browser
echo   Press CTRL+C to stop the server
echo ========================================
echo.

python -m streamlit run streamlit_app.py

pause

