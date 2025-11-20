#!/usr/bin/env python
"""
OpenRouter 連接測試腳本
測試 OpenRouter API 是否正確配置並可用
"""

import os
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import requests

def test_openrouter_api_key():
    """測試 API key 是否設置"""
    print("=" * 60)
    print("測試 1: 檢查 OPENROUTER_API_KEY 環境變數")
    print("=" * 60)

    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("[FAIL] OPENROUTER_API_KEY not set")
        print("\nPlease add to .env file:")
        print("OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        return False

    if api_key == "your-openrouter-api-key-here":
        print("[FAIL] OPENROUTER_API_KEY is still placeholder")
        print("\nPlease replace with real API key:")
        print("1. Visit https://openrouter.ai/keys")
        print("2. Create API key")
        print("3. Update .env file")
        return False

    print(f"[OK] OPENROUTER_API_KEY is set")
    print(f"   Key prefix: {api_key[:15]}...")
    return True


def test_openrouter_models():
    """測試 API key 是否有效（查詢可用模型）"""
    print("\n" + "=" * 60)
    print("測試 2: 驗證 API key 有效性（查詢模型列表）")
    print("=" * 60)

    api_key = os.getenv('OPENROUTER_API_KEY')

    try:
        response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )

        if response.status_code == 200:
            models = response.json()['data']
            print(f"[OK] API key is valid")
            print(f"   Available models: {len(models)}")

            # 顯示推薦的模型
            print("\n[RECOMMENDED] Models for Zettelkasten:")
            recommended = [
                'anthropic/claude-3.5-sonnet',
                'anthropic/claude-3-haiku',
                'google/gemini-2.0-flash-exp'
            ]

            for model_id in recommended:
                model = next((m for m in models if m['id'] == model_id), None)
                if model:
                    pricing = model.get('pricing', {})
                    prompt_price = pricing.get('prompt', 'N/A')
                    completion_price = pricing.get('completion', 'N/A')
                    print(f"   [+] {model_id}")
                    print(f"       Input: ${prompt_price}/M tokens, Output: ${completion_price}/M tokens")

            return True

        elif response.status_code == 401:
            print(f"[FAIL] API key invalid (401 Unauthorized)")
            return False

        else:
            print(f"[FAIL] API error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("[FAIL] Request timeout (network issue?)")
        return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_openrouter_simple_call():
    """測試簡單的 API 調用"""
    print("\n" + "=" * 60)
    print("測試 3: 測試簡單的 LLM 調用（Claude 3 Haiku）")
    print("=" * 60)

    api_key = os.getenv('OPENROUTER_API_KEY')

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/claude-lit-workflow",
        "X-Title": "Claude Lit Workflow - Test"
    }

    data = {
        "model": "anthropic/claude-3-haiku",  # 使用便宜的模型測試
        "messages": [
            {"role": "user", "content": "請用一句話回答：什麼是 Zettelkasten？"}
        ],
        "max_tokens": 100
    }

    try:
        print("Sending test request to Claude 3 Haiku...")
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"[OK] API call successful")
            print(f"\n[RESPONSE]:")
            print(f"   {content}")

            # 顯示使用情況
            usage = result.get('usage', {})
            if usage:
                print(f"\n[USAGE] Token usage:")
                print(f"   Input: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   Output: {usage.get('completion_tokens', 'N/A')}")
                print(f"   Total: {usage.get('total_tokens', 'N/A')}")

            return True

        elif response.status_code == 402:
            print("[FAIL] Insufficient credits")
            print("   Please add credits at https://openrouter.ai/credits")
            return False

        else:
            print(f"[FAIL] API error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_slidemaker_integration():
    """測試 SlideMaker 整合"""
    print("\n" + "=" * 60)
    print("測試 4: 測試 SlideMaker 整合")
    print("=" * 60)

    try:
        from src.generators.slide_maker import SlideMaker

        print("Initializing SlideMaker (provider=openrouter)...")
        slide_maker = SlideMaker(llm_provider='openrouter')

        # 檢查是否能檢測到 OpenRouter
        available = slide_maker._detect_available_providers()

        if 'openrouter' in available:
            print(f"[OK] OpenRouter detected successfully")
            print(f"   Available providers: {', '.join(available)}")
        else:
            print(f"[FAIL] OpenRouter not detected")
            print(f"   Available providers: {', '.join(available)}")
            return False

        # 測試簡單調用
        print("\nTesting call_llm()...")
        result, provider = slide_maker.call_llm(
            prompt="What is atomic note in one sentence?",
            provider='openrouter',
            model='anthropic/claude-3-haiku'
        )

        print(f"[OK] call_llm() successful")
        print(f"   Used provider: {provider}")
        print(f"   Response: {result[:100]}...")

        return True

    except Exception as e:
        print(f"[FAIL] SlideMaker integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試流程"""
    print("\n[TEST] OpenRouter Connection Test")
    print("=" * 60)

    results = []

    # 測試 1: API key
    results.append(("API Key Setup", test_openrouter_api_key()))

    # 如果 API key 未設置，停止測試
    if not results[0][1]:
        print("\n" + "=" * 60)
        print("[ABORT] Test aborted: Please set OPENROUTER_API_KEY first")
        print("=" * 60)
        return

    # 測試 2: 模型列表
    results.append(("API Key Validity", test_openrouter_models()))

    # 如果 API key 無效，停止測試
    if not results[1][1]:
        print("\n" + "=" * 60)
        print("[ABORT] Test aborted: API key invalid")
        print("=" * 60)
        return

    # 測試 3: 簡單調用
    results.append(("Simple API Call", test_openrouter_simple_call()))

    # 測試 4: SlideMaker 整合
    results.append(("SlideMaker Integration", test_slidemaker_integration()))

    # 總結
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n[SUCCESS] All tests passed! OpenRouter is correctly configured.")
        print("\nNext steps:")
        print("1. Use regenerate_zettel_with_openrouter.py to regenerate cards")
        print("2. Or directly use llm_provider='openrouter' in scripts")
    else:
        print("\n[WARNING] Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
