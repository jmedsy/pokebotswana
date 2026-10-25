@echo off
setlocal enabledelayedexpansion

REM Prefer venv312 (Python 3.12) — pygame has no wheels for newer Pythons yet
if exist "venv312" (
    call venv312\Scripts\activate.bat
) else if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment with Python 3.12...
    py -3.12 -m venv venv312
    call venv312\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the command with all arguments passed to this script.
REM Output is also written to a new file in logs/.
set PYTHONUNBUFFERED=1
python -m pkbt.run_logged %*

endlocal
