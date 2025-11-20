#!/usr/bin/env python3
"""
終端恢復工具 - 診斷並恢復卡住的 PowerShell 終端
"""
import subprocess
import sys
import io
import time
from datetime import datetime

# UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_flush(msg=''):
    print(msg, flush=True)

def get_process_details(process_name):
    """獲取進程詳細信息"""
    try:
        result = subprocess.run(
            ['wmic', 'process', 'where', f"name='{process_name}'", 'get',
             'ProcessId,CreationDate,WorkingSetSize,CommandLine'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"錯誤: {e}"

def kill_process(pid):
    """終止進程"""
    try:
        result = subprocess.run(
            ['taskkill', '/PID', str(pid), '/F'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print_flush("=" * 70)
    print_flush("終端恢復工具")
    print_flush("=" * 70)
    print_flush(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. 檢測 Python 進程
    print_flush("[步驟 1/5] 檢測 Python 進程...")
    python_info = get_process_details('python.exe')

    python_pids = []
    for line in python_info.split('\n'):
        if line.strip() and 'ProcessId' not in line:
            parts = line.split()
            for part in parts:
                if part.isdigit() and len(part) <= 8:
                    python_pids.append(int(part))
                    break

    if python_pids:
        print_flush(f"✅ 找到 {len(python_pids)} 個 Python 進程:")
        for pid in python_pids:
            print_flush(f"   - PID: {pid}")
    else:
        print_flush("✅ 沒有 Python 進程在運行")
    print_flush()

    # 2. 檢測 PowerShell 進程
    print_flush("[步驟 2/5] 檢測 PowerShell 進程...")
    ps_info = get_process_details('powershell.exe')

    ps_pids = []
    for line in ps_info.split('\n'):
        if line.strip() and 'ProcessId' not in line:
            parts = line.split()
            for part in parts:
                if part.isdigit() and len(part) <= 8:
                    ps_pids.append(int(part))
                    break

    if ps_pids:
        print_flush(f"✅ 找到 {len(ps_pids)} 個 PowerShell 進程:")
        for pid in ps_pids:
            print_flush(f"   - PID: {pid}")
    else:
        print_flush("✅ 沒有 PowerShell 進程")
    print_flush()

    # 3. 診斷問題
    print_flush("[步驟 3/5] 診斷問題...")

    if python_pids:
        print_flush(f"⚠️ 發現 Python 進程可能卡住")
        print_flush(f"   PID: {python_pids}")
        has_issue = True
    else:
        print_flush("✅ 沒有卡住的 Python 進程")
        has_issue = False

    print_flush()

    # 4. 提供解決方案
    print_flush("[步驟 4/5] 解決方案...")

    if has_issue:
        print_flush("建議操作:")
        print_flush(f"  1. 終止卡住的 Python 進程 (PID: {python_pids[0]})")
        print_flush(f"  2. 清理 PowerShell 終端狀態")
        print_flush(f"  3. 重新執行測試\n")

        # 詢問是否自動處理
        print_flush("=" * 70)
        print_flush("自動修復選項:")
        print_flush("=" * 70)
        print_flush(f"\n要自動終止 Python 進程嗎？")
        print_flush(f"執行命令: python recover_terminal.py --kill\n")

    else:
        print_flush("✅ 系統狀態正常")
        print_flush("\n可能的原因:")
        print_flush("  1. 進程已經結束，但終端緩衝區沒有刷新")
        print_flush("  2. PowerShell 終端本身卡住")
        print_flush("  3. 輸出重定向問題\n")

        print_flush("建議操作:")
        print_flush("  1. 在卡住的終端按 Ctrl+C")
        print_flush("  2. 如果沒反應，關閉該終端重開")
        print_flush("  3. 重新執行測試: python test_parse_quick.py\n")

    # 5. 檢查是否有 --kill 參數
    if '--kill' in sys.argv and python_pids:
        print_flush("[步驟 5/5] 執行自動修復...")
        print_flush(f"\n正在終止 Python 進程 (PID: {python_pids[0]})...")

        success, output = kill_process(python_pids[0])

        if success:
            print_flush(f"✅ 成功終止進程 {python_pids[0]}")
            print_flush("\n接下來:")
            print_flush("  1. 切換到原 PowerShell 終端")
            print_flush("  2. 按 Enter 鍵清理終端狀態")
            print_flush("  3. 重新執行: python test_parse_quick.py")
        else:
            print_flush(f"❌ 終止失敗: {output}")
            print_flush(f"\n手動終止命令:")
            print_flush(f"  taskkill /PID {python_pids[0]} /F")
    else:
        print_flush("[步驟 5/5] 等待用戶確認...")
        print_flush("未執行自動修復（需要 --kill 參數）\n")

    print_flush("=" * 70)
    print_flush("診斷完成")
    print_flush("=" * 70)

    # 生成摘要報告
    print_flush("\n【摘要報告】")
    print_flush(f"  Python 進程: {len(python_pids)} 個")
    print_flush(f"  PowerShell 進程: {len(ps_pids)} 個")
    print_flush(f"  系統狀態: {'⚠️ 需要修復' if has_issue else '✅ 正常'}")

    if has_issue:
        print_flush(f"\n【快速修復】")
        print_flush(f"  執行: python recover_terminal.py --kill")

if __name__ == '__main__':
    main()
