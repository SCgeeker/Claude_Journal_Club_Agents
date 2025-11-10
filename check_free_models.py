#!/usr/bin/env python
"""查詢 OpenRouter 免費模型"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')

# 查詢所有模型
response = requests.get(
    'https://openrouter.ai/api/v1/models',
    headers={'Authorization': f'Bearer {api_key}'},
    timeout=10
)

if response.status_code == 200:
    models = response.json()['data']

    # 篩選免費或超低價模型
    free_models = []
    cheap_models = []

    for model in models:
        pricing = model.get('pricing', {})
        prompt_price = pricing.get('prompt', '0')
        completion_price = pricing.get('completion', '0')

        # 轉換為數字
        try:
            prompt_price = float(prompt_price)
            completion_price = float(completion_price)
        except:
            continue

        model_info = {
            'id': model['id'],
            'name': model.get('name', 'N/A'),
            'context': model.get('context_length', 0),
            'prompt_price': prompt_price,
            'completion_price': completion_price
        }

        # 完全免費
        if prompt_price == 0 and completion_price == 0:
            free_models.append(model_info)
        # 超低價（每 M tokens < $0.0001）
        elif prompt_price < 0.0001 and completion_price < 0.001:
            cheap_models.append(model_info)

    print('=' * 80)
    print(f'OpenRouter 免費模型 ({len(free_models)} 個)')
    print('=' * 80)

    # 按 context length 排序
    free_models.sort(key=lambda x: x['context'], reverse=True)

    for i, model in enumerate(free_models, 1):
        print(f'\n{i}. {model["id"]}')
        print(f'   Context: {model["context"]:,} tokens')
        print(f'   Price: FREE')

    print('\n' + '=' * 80)
    print(f'超低價模型 (< $0.0001 input, < $0.001 output) ({len(cheap_models)} 個)')
    print('=' * 80)

    cheap_models.sort(key=lambda x: x['prompt_price'] + x['completion_price'])

    for i, model in enumerate(cheap_models[:10], 1):  # 只顯示前 10 個
        print(f'\n{i}. {model["id"]}')
        print(f'   Context: {model["context"]:,} tokens')
        print(f'   Input: ${model["prompt_price"]:.8f}/M tokens')
        print(f'   Output: ${model["completion_price"]:.8f}/M tokens')

        # 估算一篇論文成本（假設 15K input + 20K output）
        cost = (15000 * model["prompt_price"] / 1000000) + (20000 * model["completion_price"] / 1000000)
        print(f'   估算成本: ${cost:.6f} per paper')

    # 特別推薦適合 Zettelkasten 的模型
    print('\n' + '=' * 80)
    print('推薦用於 Zettelkasten 的模型')
    print('=' * 80)

    recommendations = [
        'google/gemini-2.0-flash-exp',
        'google/gemini-flash-1.5',
        'meta-llama/llama-3.2-3b-instruct:free',
        'meta-llama/llama-3.1-8b-instruct:free',
        'qwen/qwen-2-7b-instruct:free',
        'microsoft/phi-3-mini-128k-instruct:free',
    ]

    for rec_id in recommendations:
        model = next((m for m in free_models + cheap_models if m['id'] == rec_id), None)
        if model:
            is_free = model in free_models
            print(f'\n[{"FREE" if is_free else "CHEAP"}] {model["id"]}')
            print(f'  Context: {model["context"]:,} tokens')
            if not is_free:
                cost = (15000 * model["prompt_price"] / 1000000) + (20000 * model["completion_price"] / 1000000)
                print(f'  Cost: ${cost:.6f} per paper')

else:
    print(f'Error: {response.status_code}')
