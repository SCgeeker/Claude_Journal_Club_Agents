#!/usr/bin/env python3
"""
檢測卡住的測試進程
"""
import subprocess
import sys
import io
from datetime import datetime

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("檢測卡住的 Python 進程")
print("=" * 70)
print(f"檢測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. 檢查所有 Python 進程
print("[1] 檢查所有 Python 進程...")
try:
    result = subprocess.run(
        ['wmic', 'process', 'where', "name='python.exe'", 'get',
         'ProcessId,CreationDate,CommandLine,WorkingSetSize'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    header = lines[0] if lines else ''

    python_procs = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # 解析進程信息
        parts = line.split()
        if len(parts) >= 3:
            # 提取 PID (通常是最後一個數字)
            pid = None
            for part in reversed(parts):
                if part.isdigit():
                    pid = part
                    break

            # 提取命令行
            cmdline = ' '.join(parts[2:-2]) if len(parts) > 4 else 'N/A'

            if pid:
                python_procs.append({
                    'pid': pid,
                    'cmdline': cmdline,
                    'is_test': 'test' in cmdline.lower() or 'zettel' in cmdline.lower()
                })

    print(f"\n找到 {len(python_procs)} 個 Python 進程:\n")

    test_procs = []
    for i, proc in enumerate(python_procs, 1):
        status = "🔴 [測試進程]" if proc['is_test'] else "✅ [正常]"
        print(f"{i}. PID: {proc['pid']:6} {status}")
        print(f"   命令: {proc['cmdline'][:100]}")
        print()

        if proc['is_test']:
            test_procs.append(proc)

    # 2. 如果找到測試進程，詢問是否要終止
    if test_procs:
        print("=" * 70)
        print(f"⚠️ 發現 {len(test_procs)} 個可能卡住的測試進程！")
        print("=" * 70)

        for proc in test_procs:
            print(f"\n進程 PID: {proc['pid']}")
            print(f"命令: {proc['cmdline'][:150]}")
            print("\n建議操作:")
            print(f"  1. 使用任務管理器手動終止 PID {proc['pid']}")
            print(f"  2. 或執行: taskkill /PID {proc['pid']} /F")
            print()
    else:
        print("✅ 沒有發現卡住的測試進程")
        print("\n可能的情況:")
        print("  - 進程已經完成但終端沒有顯示輸出")
        print("  - 進程在等待用戶輸入")
        print("  - 輸出被緩衝區阻塞")

except Exception as e:
    print(f"❌ 檢測失敗: {e}")

print("\n" + "=" * 70)
print("檢測完成")
print("=" * 70)

# 3. 提供解決方案
print("\n【建議的解決方案】")
print("1. 如果發現卡住的進程，在新終端執行:")
print("   taskkill /PID <進程ID> /F")
print("\n2. 如果沒有卡住的進程，嘗試在原終端按:")
print("   - Ctrl+C (中斷)")
print("   - Enter (可能在等待輸入)")
print("\n3. 重新執行測試:")
print("   python test_parse_single_zettel.py")
