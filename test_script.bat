@echo off
REM Test Batch Script for CMD Manager Application
REM This demonstrates batch file management capabilities

setlocal EnableDelayedExpansion
set counter=0

echo.
echo 🚀 Batch Test Script Started!
echo ⏰ Start time: %DATE% %TIME%
echo 📝 This batch script demonstrates:
echo    - Continuous output generation
echo    - Windows batch file execution
echo    - Simple counter operations
echo    - System information display
echo --------------------------------------------------

:main_loop
set /a counter+=1

REM Different outputs based on counter
set /a remainder=!counter! %% 10
if !remainder! equ 0 (
    echo 🔢 Batch milestone: !counter! at %TIME%
) else (
    set /a remainder=!counter! %% 5
    if !remainder! equ 0 (
        echo ⚙️  Processing batch operation !counter!...
        timeout /t 1 /nobreak >nul
        echo ✅ Batch operation complete!
    ) else (
        echo 📊 Regular batch output #!counter! - %TIME%
    )
)

REM Simulate events at specific counters
if !counter! equ 15 (
    echo ⚠️  Batch warning simulation
)
if !counter! equ 25 (
    echo ❌ ERROR: Simulated batch error >&2
)
if !counter! equ 35 (
    echo 🎉 Batch script milestone reached!
)

REM System information every 20 iterations
set /a remainder=!counter! %% 20
if !remainder! equ 0 (
    echo 💻 System Info:
    echo    Computer: %COMPUTERNAME%
    echo    User: %USERNAME%
    echo    OS: %OS%
    echo    Processor: %PROCESSOR_ARCHITECTURE%
)

REM Reset counter after 50 iterations
if !counter! geq 50 (
    echo 🏁 Batch test cycle completed! Restarting...
    set counter=0
)

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Check if script should continue (simple way)
if not exist "%TEMP%\stop_batch_test.txt" goto main_loop

echo 🔚 Batch script ending at %TIME%
echo 👋 Goodbye from Batch!
del "%TEMP%\stop_batch_test.txt" 2>nul