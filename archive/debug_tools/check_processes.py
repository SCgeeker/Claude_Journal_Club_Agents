#!/usr/bin/env python3
"""
進程檢測工具 - 偵測系統中的終端機和開發工具進程
"""
import subprocess
import sys
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("進程偵測報告")
    print("=" * 60)
    print(f"檢測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. 檢測 Python 進程
    print("【1. Python 進程】")
    try:
        result = subprocess.run(
            ['wmic', 'process', 'where', "name='python.exe'", 'get', 'ProcessId,CommandLine'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )
        lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and 'CommandLine' not in l]
        if lines:
            for i, line in enumerate(lines[:10], 1):
                parts = line.split()
                if len(parts) >= 2:
                    print(f"  {i}. PID: {parts[-1]:6} | Command: {' '.join(parts[:-1])[:80]}")
        else:
            print("  ✅ 無額外的 Python 進程運行")
    except Exception as e:
        print(f"  ⚠️ 檢測失敗: {e}")

    print()

    # 2. 檢測 PowerShell 進程
    print("【2. PowerShell 進程】")
    try:
        result = subprocess.run(
            ['wmic', 'process', 'where', "name='powershell.exe'", 'get', 'ProcessId,CommandLine'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )
        lines = [l.strip() for l in result.stdout.split('\n') if l.strip() and 'CommandLine' not in l]
        if lines:
            print(f"  找到 {len(lines)} 個 PowerShell 進程")
            for i, line in enumerate(lines[:5], 1):
                parts = line.split()
                if len(parts) >= 1:
                    print(f"  {i}. PID: {parts[-1] if parts else 'N/A'}")
        else:
            print("  ✅ 無 PowerShell 進程")
    except Exception as e:
        print(f"  ⚠️ 檢測失敗: {e}")

    print()

    # 3. 檢測監聽端口
    print("【3. 網絡監聽端口】")
    common_ports = {
        8000: 'HTTP Dev Server',
        8888: 'Jupyter',
        5000: 'Flask',
        3000: 'Node.js',
        11434: 'Ollama'
    }

    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )

        listening = {}
        for line in result.stdout.split('\n'):
            if 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    addr = parts[1]
                    if ':' in addr:
                        port = int(addr.split(':')[-1])
                        if port in common_ports:
                            listening[port] = parts[-1]

        if listening:
            for port, pid in listening.items():
                service = common_ports.get(port, 'Unknown')
                print(f"  ✅ Port {port} ({service}) - PID: {pid}")
        else:
            print("  ✅ 無常用開發端口在監聽")
    except Exception as e:
        print(f"  ⚠️ 檢測失敗: {e}")

    print()

    # 4. 檢測背景 shell
    print("【4. Claude Code 背景 Shell】")
    try:
        shell_dir = r"C:\Users\Sau-Chin Chen\.claude\shell-snapshots"
        import os
        if os.path.exists(shell_dir):
            shells = os.listdir(shell_dir)
            if shells:
                print(f"  找到 {len(shells)} 個 shell snapshot")
                for shell in shells[:5]:
                    print(f"  - {shell}")
            else:
                print("  ✅ 無 shell snapshot")
        else:
            print("  ℹ️ Shell snapshot 目錄不存在")
    except Exception as e:
        print(f"  ⚠️ 檢測失敗: {e}")

    print()
    print("=" * 60)
    print("檢測完成")
    print("=" * 60)

if __name__ == '__main__':
    # 設定 UTF-8 輸出
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    main()
