@echo off
title Tata AI Legal Document Intelligence
echo ========================================================
echo  Starting Tata AI Legal Document Intelligence
echo ========================================================

set PYTHON_CMD=python

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
) else if exist "C:\Users\dynamic\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD="C:\Users\dynamic\AppData\Local\Programs\Python\Python313\python.exe"
) else (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py -3.13
    )
)

echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% run.py
pause
