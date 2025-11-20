# OpenRouter 集成 - 下一步操作指南

## 📊 当前状态

✅ **已完成**:
- [x] `.env` 文件已更新（添加 OPENROUTER_API_KEY）
- [x] 创建 `docs/OPENROUTER_SETUP.md` 配置指南
- [x] 创建 `regenerate_zettel_with_openrouter.py` 脚本

❌ **待完成**:
- [ ] 在 `SlideMaker` 中添加 OpenRouter 支持
- [ ] 测试 OpenRouter 连接
- [ ] 使用不同 LLM 重新生成卡片

---

## 🎯 立即操作（按顺序）

### Option A: 使用现有的 Anthropic API (如果已有)

如果你已经有 Anthropic Claude API key：

```bash
# 1. 设置 API key
export ANTHROPIC_API_KEY=your-key-here

# 2. 使用 Claude 3.5 Sonnet 重新生成
python regenerate_zettel_elegant.py
# 修改脚本中的 llm_provider='anthropic'
```

**优势**:
- ✅ 无需配置 OpenRouter
- ✅ Claude 3.5 Sonnet 格式遵循最佳
- ❌ 需要单独的 Anthropic API key

---

### Option B: 配置 OpenRouter (推荐)

#### Step 1: 注册并获取 API Key

1. 访问: https://openrouter.ai/
2. 注册账户
3. 前往: https://openrouter.ai/keys
4. 创建 API Key (格式: `sk-or-v1-...`)
5. 添加信用额度 (建议 $5-10)

#### Step 2: 配置到项目

编辑 `.env` 文件，将：
```bash
OPENROUTER_API_KEY=your-openrouter-api-key-here
```
替换为你的实际 API key。

#### Step 3: 添加 OpenRouter 支持到 SlideMaker

需要在 `src/generators/slide_maker.py` 中添加以下方法：

```python
def call_openrouter(self, prompt: str, model: str = "anthropic/claude-3.5-sonnet") -> str:
    """
    调用 OpenRouter API

    Args:
        prompt: 提示词
        model: 模型名称 (例如: anthropic/claude-3.5-sonnet)

    Returns:
        LLM 响应
    """
    import requests
    import os

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "Claude Lit Workflow"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=300)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenRouter API call failed: {e}")
```

然后在 `call_llm()` 方法中添加 OpenRouter 支持：

```python
# 在 call_llm() 中添加:
elif attempt_provider == 'openrouter':
    used_model = actual_model or "anthropic/claude-3.5-sonnet"
    result = self.call_openrouter(prompt, used_model)
```

#### Step 4: 测试连接

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

import requests

api_key = os.getenv('OPENROUTER_API_KEY')
if api_key:
    print('✅ OPENROUTER_API_KEY is set')
    # 测试 API
    response = requests.get(
        'https://openrouter.ai/api/v1/models',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    if response.status_code == 200:
        print('✅ API key is valid')
        models = response.json()['data']
        print(f'✅ Available models: {len(models)}')
    else:
        print(f'❌ API error: {response.status_code}')
else:
    print('❌ OPENROUTER_API_KEY not set')
"
```

#### Step 5: 使用 Claude 3.5 Sonnet 重新生成

```bash
# 修改 regenerate_zettel_with_openrouter.py 中的默认配置
python regenerate_zettel_with_openrouter.py --provider openrouter --model anthropic/claude-3.5-sonnet
```

---

### Option C: 多 LLM 对比测试 (最全面)

配置好 OpenRouter 后，运行多 LLM 对比测试：

```bash
python regenerate_zettel_with_openrouter.py --test-all
```

这将测试所有可用的 LLM：
1. Claude 3.5 Sonnet (OpenRouter) - 最佳格式遵循
2. Claude 3 Haiku (OpenRouter) - 快速经济
3. Gemini 2.0 Flash - 免费
4. 直接 Anthropic (如果有 API key)

然后对比每个版本的 AI Notes 连结生成情况。

---

## 🔧 代码修改指南

如果你想自己添加 OpenRouter 支持，需要修改以下文件：

### 1. `src/generators/slide_maker.py`

**位置 1**: 在 `_init_llm_clients()` 中添加检测：

```python
def _init_llm_clients(self):
    """初始化LLM客户端"""
    # ... 现有代码 ...

    # 检测 OpenRouter
    try:
        import requests
        if os.getenv('OPENROUTER_API_KEY'):
            self.openrouter_available = True
        else:
            self.openrouter_available = False
    except ImportError:
        self.openrouter_available = False
```

**位置 2**: 在 `_detect_available_providers()` 中添加：

```python
def _detect_available_providers(self) -> List[str]:
    """检测可用的LLM提供者"""
    available = []

    # ... 现有检测代码 ...

    if hasattr(self, 'openrouter_available') and self.openrouter_available:
        available.append('openrouter')

    return available
```

**位置 3**: 添加 `call_openrouter()` 方法（见上面的代码）

**位置 4**: 在 `call_llm()` 中添加分支

---

## 📚 参考资料

- **OpenRouter 文档**: https://openrouter.ai/docs
- **支持的模型**: https://openrouter.ai/models
- **定价**: https://openrouter.ai/pricing
- **API 参考**: https://openrouter.ai/docs#models

---

## 💡 推荐工作流

### 快速开始（最简单）

1. 注册 OpenRouter，获取 API key
2. 添加到 `.env` 文件
3. 我会帮你添加代码支持
4. 运行测试

### 完整测试（最全面）

1. 配置所有 API keys (OpenRouter + Google + Anthropic)
2. 运行多 LLM 对比测试
3. 分析每个版本的结果
4. 选择最佳 LLM 用于批量处理

---

## ❓ 需要帮助？

**问题 1**: 我想直接测试，不想修改代码

**答案**: 使用 Option A (直接 Anthropic API) 或等我帮你添加 OpenRouter 支持

**问题 2**: OpenRouter 和直接用 Anthropic API 有什么区别？

**答案**:
- **OpenRouter**: 统一接口，访问所有模型，成本更透明
- **直接 API**: 只能访问单个提供商，但设置更简单

**问题 3**: 哪个 LLM 最适合 Zettelkasten？

**答案**: Claude 3.5 Sonnet（最佳格式遵循和批判性思考能力）

---

**下一步**: 告诉我你想用哪个 Option，我会协助你完成配置！
