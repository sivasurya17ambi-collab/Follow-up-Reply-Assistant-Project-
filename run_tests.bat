@echo off
title Follow-up Reply Assistant - Automated Test Suite
echo ===================================================================
echo   RUNNING AUTOMATED PYTEST SUITE (PRJ-042)
echo ===================================================================
echo.
pytest -v tests/
echo.
pause
