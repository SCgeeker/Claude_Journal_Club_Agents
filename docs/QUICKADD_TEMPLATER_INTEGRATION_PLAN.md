# QuickAdd + Templater 整合計畫（階段 2）

**版本**: 1.0
**日期**: 2025-11-24
**狀態**: 規劃階段（待條件成熟後實作）

---

## 概述

本計畫描述如何將 `import_zettel.py` 整合到 Obsidian 工作流中，實現「一鍵匯入」的使用體驗。

---

## 目標

- 在 Obsidian 內透過 QuickAdd 命令觸發匯入
- 無需手動開啟終端或輸入命令
- 提供互動式選項（選擇要匯入的論文）
- 匯入完成後自動開啟新建的 Annotation Note

---

## 前置條件

### 1. Templater 設定變更

需要修改 `.obsidian/plugins/templater-obsidian/data.json`：

```json
{
  "enable_system_commands": true,
  "user_scripts_folder": "+/tools/scripts",
  "templates_folder": "Templates"
}
```

**風險說明**：
- `enable_system_commands` 允許執行任意系統命令
- 確保 `user_scripts_folder` 內的腳本來源可信

### 2. 資料夾結構

```
ProgramVerse/
├── +/
│   └── tools/
│       ├── import_zettel.py     # 主程式（階段 1）
│       ├── config.yaml
│       └── scripts/             # Templater user scripts
│           └── import_wrapper.js
│
└── Templates/
    └── Template, Import Zettel.md
```

---

## 架構設計

```
┌─────────────────┐
│   QuickAdd      │  用戶觸發
│   Command       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Templater     │  執行模板
│   Template      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Script    │  JavaScript 包裝
│  (import_       │
│   wrapper.js)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Script  │  實際匯入邏輯
│  (import_       │
│   zettel.py)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Annotation     │  匯入結果
│  Note Created   │
└─────────────────┘
```

---

## 實作元件

### 1. Templater User Script (`import_wrapper.js`)

```javascript
// +/tools/scripts/import_wrapper.js

async function importZettel(tp) {
    const { exec } = require('child_process');
    const path = require('path');

    // 配置路徑
    const vaultPath = app.vault.adapter.basePath;
    const scriptPath = path.join(vaultPath, '+/tools/import_zettel.py');
    const configPath = path.join(vaultPath, '+/tools/config.yaml');

    // 取得可用的 zettel 資料夾
    const claudeLitOutput = 'D:/core/research/claude_lit_workflow/output/zettelkasten_notes';

    // 列出可匯入的論文
    const fs = require('fs');
    const folders = fs.readdirSync(claudeLitOutput)
        .filter(f => f.startsWith('zettel_'))
        .map(f => {
            const match = f.match(/zettel_(.+?)_\d{8}/);
            return match ? match[1] : f;
        });

    if (folders.length === 0) {
        new Notice('沒有可匯入的 Zettelkasten');
        return '';
    }

    // 讓用戶選擇
    const selected = await tp.system.suggester(
        folders,
        folders,
        false,
        '選擇要匯入的論文'
    );

    if (!selected) {
        return '';
    }

    // 執行 Python 腳本
    return new Promise((resolve, reject) => {
        const cmd = `python "${scriptPath}" --citekey "${selected}" --config "${configPath}"`;

        exec(cmd, { cwd: vaultPath }, (error, stdout, stderr) => {
            if (error) {
                new Notice(`匯入失敗: ${stderr}`);
                console.error(stderr);
                resolve('');
                return;
            }

            new Notice(`成功匯入 ${selected}`);
            console.log(stdout);

            // 回傳新建的筆記路徑
            resolve(`ACT/0️⃣Annotation/${selected}/${selected}_annotation.md`);
        });
    });
}

module.exports = importZettel;
```

### 2. Templater Template (`Template, Import Zettel.md`)

```markdown
<%*
const importZettel = tp.user.import_wrapper;
const notePath = await importZettel(tp);

if (notePath) {
    // 開啟新建的筆記
    const file = app.vault.getAbstractFileByPath(notePath);
    if (file) {
        await app.workspace.getLeaf().openFile(file);
    }
}

// 不產生任何輸出（此模板只用於觸發匯入）
tR = '';
%>
```

### 3. QuickAdd 配置

在 QuickAdd 設定中新增：

```json
{
  "id": "import-zettel-command",
  "name": "Import Zettel from Claude Lit",
  "type": "Template",
  "templatePath": "Templates/Template, Import Zettel.md",
  "fileNameFormat": {
    "enabled": false
  },
  "folder": {
    "enabled": false
  },
  "openFile": false,
  "command": true
}
```

---

## 進階功能（可選）

### A. 批次匯入選項

```javascript
// 在 import_wrapper.js 中加入多選支援
const selectedMultiple = await tp.system.suggester(
    ['匯入單篇', '批次匯入全部'],
    ['single', 'batch']
);

if (selectedMultiple === 'batch') {
    // 執行批次匯入
    const cmd = `python "${scriptPath}" --batch --config "${configPath}"`;
    // ...
}
```

### B. 匯入前預覽

```javascript
// 顯示即將匯入的內容摘要
const previewCmd = `python "${scriptPath}" --citekey "${selected}" --dry-run --json`;
// 解析 JSON 輸出並顯示預覽
```

### C. 匯入後自動更新 Dataview

```javascript
// 匯入完成後觸發 Dataview 重新索引
app.commands.executeCommandById('dataview:reload-data');
```

---

## 安裝步驟

### 步驟 1: 啟用 Templater 系統命令

1. 開啟 Obsidian 設定
2. 進入 Templater 設定頁面
3. 啟用 `Enable System Commands`
4. 設定 `User Scripts Folder` 為 `+/tools/scripts`

### 步驟 2: 建立檔案結構

```bash
# 在 ProgramVerse vault 中
mkdir -p "+/tools/scripts"
```

### 步驟 3: 複製腳本

1. 將 `import_wrapper.js` 放入 `+/tools/scripts/`
2. 將 `Template, Import Zettel.md` 放入 `Templates/`
3. 確保 `import_zettel.py` 已在 `+/tools/`

### 步驟 4: 設定 QuickAdd

1. 開啟 QuickAdd 設定
2. 新增 Template 類型的選項
3. 設定為命令（Command）模式
4. 綁定快捷鍵（可選）

### 步驟 5: 測試

1. 按 `Ctrl+P` 開啟命令面板
2. 搜尋 "Import Zettel"
3. 選擇論文並確認匯入

---

## 故障排除

### 問題 1: "User script not found"

**原因**: Templater 找不到 user scripts 資料夾

**解決**:
1. 確認 `user_scripts_folder` 設定正確
2. 重新載入 Obsidian

### 問題 2: "Python not found"

**原因**: 系統 PATH 中沒有 Python

**解決**:
1. 在 `import_wrapper.js` 中使用完整路徑
2. 或將 Python 加入系統 PATH

```javascript
// 使用完整路徑
const pythonPath = 'C:/Users/YourName/AppData/Local/Programs/Python/Python310/python.exe';
const cmd = `"${pythonPath}" "${scriptPath}" ...`;
```

### 問題 3: 編碼問題（中文檔名）

**原因**: Windows 命令列編碼問題

**解決**:
```javascript
const cmd = `chcp 65001 && python "${scriptPath}" ...`;
```

### 問題 4: 權限不足

**原因**: Obsidian 沙盒限制

**解決**:
1. 確認 Obsidian 有足夠權限
2. 考慮使用 Terminal 插件作為替代方案

---

## 與階段 1 的關係

| 項目 | 階段 1 (Terminal) | 階段 2 (QuickAdd) |
|------|------------------|------------------|
| 觸發方式 | 手動開啟終端 | 命令面板/快捷鍵 |
| 互動性 | 命令列參數 | GUI 選擇器 |
| 學習曲線 | 需熟悉 CLI | 更直覺 |
| 靈活性 | 高（完整參數） | 中（預設選項） |
| 維護複雜度 | 低 | 中 |

**建議**：先完成階段 1，確認 `import_zettel.py` 穩定後再實作階段 2。

---

## 時程預估

| 階段 | 工作項目 | 時間 |
|------|---------|------|
| 準備 | 啟用 Templater 設定 | 0.5 小時 |
| 開發 | import_wrapper.js | 2-3 小時 |
| 整合 | QuickAdd 配置 | 1 小時 |
| 測試 | 各種情境測試 | 2-3 小時 |
| **總計** | | **5-7 小時** |

---

## 安全考量

1. **系統命令風險**: 啟用 `enable_system_commands` 後，任何模板都可執行系統命令
2. **緩解措施**:
   - 只放置可信的腳本在 `user_scripts_folder`
   - 定期審查腳本內容
   - 考慮使用白名單機制

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2025-11-24 | 初版規劃 |

---

*本文檔為階段 2 整合計畫，待階段 1 完成並驗證後實作*
