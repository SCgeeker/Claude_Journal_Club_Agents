@echo off
echo ========================================
echo 終止所有 Python 測試進程
echo ========================================
echo.

echo [1/3] 顯示當前 Python 進程...
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
echo.

echo [2/3] 終止 Python 進程...
taskkill /IM python.exe /F 2>nul
if %ERRORLEVEL% EQU 0 (
    echo 成功終止 Python 進程
) else (
    echo 沒有需要終止的 Python 進程
)
echo.

echo [3/3] 驗證...
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
echo.

echo ========================================
echo 完成！
echo ========================================
echo.
echo 接下來的步驟:
echo   1. 回到卡住的 PowerShell 終端
echo   2. 按 Enter 鍵
echo   3. 執行: python test_parse_quick.py
echo.
pause
