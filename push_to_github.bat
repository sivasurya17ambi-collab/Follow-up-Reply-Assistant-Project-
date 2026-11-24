@echo off
title Push Follow-up Reply Assistant to GitHub
echo ===================================================================
echo   PUSH PROJECT TO GITHUB (PRJ-042)
echo   Student: SIVASURYA.B (Reg No: 411723205052)
echo ===================================================================
echo.
echo Step 1: Make sure you created a NEW EMPTY repository on GitHub:
echo         https://github.com/new
echo         (Do NOT initialize with README, .gitignore, or license)
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo.
    echo Error: No repository URL entered. Exiting.
    pause
    exit /b
)

echo.
echo Configuring remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing commits to GitHub...
git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ===================================================================
    echo   SUCCESSFULLY PUSHED TO GITHUB!
    echo ===================================================================
) else (
    echo.
    echo If push failed, check:
    echo 1. Your GitHub username and Personal Access Token (or password).
    echo 2. Verify that the repository on GitHub is empty and exists.
)
echo.
pause
