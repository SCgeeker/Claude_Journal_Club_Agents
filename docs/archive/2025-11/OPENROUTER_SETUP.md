# OpenRouter 配置指南

## 注册并获取 API Key

1. **访问**: https://openrouter.ai/
2. **注册账户**
3. **前往**: https://openrouter.ai/keys
4. **创建 API Key** (格式: `sk-or-v1-...`)
5. **添加信用额度** (推荐 $5-10 用于测试)

## 配置到项目

编辑 `.env` 文件，添加：

```bash
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 可选：设置为默认 provider
DEFAULT_LLM_PROVIDER=openrouter

# 可选：设置默认模型
DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

## 推荐模型配置（用于 Zettelkasten）

### 高质量模式（格式遵循优先）

```python
llm_config = {
    'provider': 'openrouter',
    'model': 'anthropic/claude-3.5-sonnet',
    'temperature': 0.3  # 更稳定的输出
}
```

**优势**:
- 🎯 最佳格式遵循能力
- 📝 准确的 Wiki Links 生成
- 💡 深度批判性思考

**成本**: ~$0.05-0.10 per paper (20 cards)

### 经济模式（批量处理）

```python
llm_config = {
    'provider': 'openrouter',
    'model': 'anthropic/claude-3-haiku',
    'temperature': 0.4
}
```

**优势**:
- ⚡ 快速响应
- 💰 成本低（约 Claude Sonnet 的 1/10）
- ✅ 良好的质量

**成本**: ~$0.005-0.01 per paper

### 免费/测试模式

```python
llm_config = {
    'provider': 'openrouter',
    'model': 'google/gemini-2.0-flash-exp',
    'temperature': 0.5
}
```

## 使用方式

### 方式 1: 修改脚本

```python
from src.generators.slide_maker import SlideMaker

slide_maker = SlideMaker(
    llm_provider='openrouter',
    api_key=os.getenv('OPENROUTER_API_KEY')
)

# 指定具体模型
response = slide_maker.call_llm(
    prompt,
    model='anthropic/claude-3.5-sonnet'
)
```

### 方式 2: 环境变量

```bash
export DEFAULT_LLM_PROVIDER=openrouter
export DEFAULT_MODEL=anthropic/claude-3.5-sonnet
export OPENROUTER_API_KEY=sk-or-v1-...

python regenerate_zettel_elegant.py
```

## 成本估算

假设一篇论文生成 20 张卡片：

| 模型 | Input (15K chars) | Output (20K chars) | 总成本 |
|------|-------------------|-------------------|--------|
| Claude 3.5 Sonnet | ~$0.01 | ~$0.08 | **~$0.09** |
| Claude 3 Haiku | ~$0.001 | ~$0.007 | **~$0.008** |
| Gemini 2.0 Flash | Free | Free | **$0.00** |

**批量处理 100 篇论文**:
- Claude 3.5 Sonnet: ~$9
- Claude 3 Haiku: ~$0.80
- Gemini 2.0 Flash: $0

## 故障排除

### 错误 1: 认证失败

```
Error: 401 Unauthorized
```

**解决**: 检查 API key 是否正确设置：
```bash
echo $OPENROUTER_API_KEY
```

### 错误 2: 余额不足

```
Error: Insufficient credits
```

**解决**: 在 https://openrouter.ai/credits 添加信用额度

### 错误 3: 模型不存在

```
Error: Model not found
```

**解决**: 查看可用模型列表：
https://openrouter.ai/models

## 推荐工作流

### Phase 1: 测试（免费）

```bash
# 使用 Gemini 测试流程
DEFAULT_LLM_PROVIDER=google python regenerate_zettel_elegant.py
```

### Phase 2: 优化（小批量）

```bash
# 使用 Claude 3.5 Sonnet 测试 3-5 篇论文
# 确认格式和质量
DEFAULT_LLM_PROVIDER=openrouter DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

### Phase 3: 批量（经济）

```bash
# 使用 Claude 3 Haiku 处理大批量
DEFAULT_LLM_PROVIDER=openrouter DEFAULT_MODEL=anthropic/claude-3-haiku
```

## 高级功能

### 自动 Fallback

OpenRouter 支持自动降级：

```python
# 如果 Sonnet 失败，自动使用 Haiku
response = slide_maker.call_llm(
    prompt,
    model='anthropic/claude-3.5-sonnet',
    fallback_models=['anthropic/claude-3-haiku', 'google/gemini-2.0-flash-exp']
)
```

### 成本追踪

```python
# 启用成本监控
from src.utils.model_monitor import ModelMonitor

monitor = ModelMonitor()
# 每次调用后记录
monitor.track_usage(
    model_name='anthropic/claude-3.5-sonnet',
    tokens_used=5000
)
```

## 相关资源

- **OpenRouter 文档**: https://openrouter.ai/docs
- **模型比较**: https://openrouter.ai/models
- **定价**: https://openrouter.ai/pricing
