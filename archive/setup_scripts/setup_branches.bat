@echo off
REM 雙分支設置腳本 (Windows版本)

echo 🌳 Knowledge Production System - 雙分支設置
echo ==========================================

REM 1. 初始化Git
if not exist .git (
    echo 📦 初始化Git倉庫...
    git init
    echo ✅ Git倉庫已初始化
)

REM 2. 確保.env在gitignore中
findstr /C:".env" .gitignore >nul 2>&1
if errorlevel 1 (
    echo .env >> .gitignore
    echo ✅ .env已加入.gitignore
)

REM 3. 創建develop分支
echo.
echo 🔧 創建develop分支（私人開發版本）...
git checkout -b develop 2>nul || git checkout develop
git add .
git commit -m "feat: Full development version" 2>nul
echo ✅ develop分支已創建

REM 4. 創建main分支
echo.
echo 🌍 創建main分支（公開版本）...
git checkout -b main 2>nul || git checkout main

REM 複製公開版README
if exist README_PUBLIC.md (
    copy /Y README_PUBLIC.md README.md
    echo ✅ 使用公開版README
)

REM 清理私人內容
echo 🧹 清理私人內容...
if exist knowledge_base\papers (
    del /Q knowledge_base\papers\*.md 2>nul
    type nul > knowledge_base\papers\.gitkeep
)
if exist output (
    del /Q output\*.pptx output\*.md 2>nul
    type nul > output\.gitkeep
)
echo ✅ 私人數據已清理

git add .
git commit -m "feat: Public release v0.4.0-alpha" 2>nul
echo ✅ main分支已創建

REM 5. 顯示狀態
echo.
echo 📊 分支狀態：
git branch -v

echo.
echo ✨ 設置完成！
echo.
echo 📋 下一步：
echo 1. 在GitHub創建倉庫
echo 2. 連接遠端：git remote add origin https://github.com/YOUR_USERNAME/repo.git
echo 3. 推送公開分支：git push -u origin main
echo 4. 可選推送私人分支：git checkout develop ^&^& git push -u origin develop
echo.
pause
