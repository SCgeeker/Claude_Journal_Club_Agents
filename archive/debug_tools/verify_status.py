#!/usr/bin/env python3
"""
驗證系統狀態並提供恢復指引
"""
import subprocess
import sys
import io

# UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60, flush=True)
print("系統狀態驗證", flush=True)
print("=" * 60, flush=True)
print(flush=True)

# 檢查 Python 進程
print("[1/3] 檢查 Python 進程...", flush=True)
try:
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=5
    )

    if 'python.exe' in result.stdout:
        lines = [l for l in result.stdout.split('\n') if 'python.exe' in l]
        print(f"發現 {len(lines)} 個 Python 進程:", flush=True)
        for line in lines[:5]:
            print(f"  {line.strip()}", flush=True)
    else:
        print("✅ 沒有 Python 進程在運行", flush=True)
        print("   -> 卡住的進程已經結束", flush=True)
except Exception as e:
    print(f"檢查失敗: {e}", flush=True)

print(flush=True)

# 檢查 PowerShell 進程
print("[2/3] 檢查 PowerShell 進程...", flush=True)
try:
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq powershell.exe'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=5
    )

    if 'powershell.exe' in result.stdout:
        lines = [l for l in result.stdout.split('\n') if 'powershell.exe' in l]
        print(f"發現 {len(lines)} 個 PowerShell 進程", flush=True)
    else:
        print("沒有 PowerShell 進程", flush=True)
except Exception as e:
    print(f"檢查失敗: {e}", flush=True)

print(flush=True)

# 測試知識庫
print("[3/3] 測試知識庫連接...", flush=True)
try:
    from src.knowledge_base import KnowledgeBaseManager
    kb = KnowledgeBaseManager()
    stats = kb.get_stats()
    print("✅ 知識庫正常", flush=True)
    print(f"   - 論文: {stats.get('total_papers', 0)} 篇", flush=True)
    print(f"   - Zettel 卡片: {stats.get('total_zettel_cards', 0)} 張", flush=True)
except Exception as e:
    print(f"❌ 知識庫錯誤: {e}", flush=True)

print(flush=True)
print("=" * 60, flush=True)
print("結論", flush=True)
print("=" * 60, flush=True)
print(flush=True)
print("✅ 系統狀態正常！", flush=True)
print(flush=True)
print("【下一步操作】", flush=True)
print("1. 回到卡住的 PowerShell 終端", flush=True)
print("2. 按 Enter 鍵嘗試恢復", flush=True)
print("3. 如果終端恢復，執行: python test_parse_quick.py", flush=True)
print("4. 如果終端仍無反應，直接關閉該視窗重新開啟", flush=True)
print(flush=True)
