import requests, time

print('=== Xyvero encoding test ===')
start = time.time()
r = requests.post('https://xyvero.space/v1/chat/completions',
    headers={'Authorization': 'Bearer sk-FOQVMuXIGrWuWQvMF3wlFM5NDZcsBAQ', 'Content-Type': 'application/json; charset=utf-8'},
    json={
        'messages': [
            {'role':'system','content':'Отвечай на русском языке. Кратко, 1-2 предложения.'},
            {'role':'user','content':'Привет! Как дела?'}
        ],
        'model': 'deepseek-v4.1-flash',
        'max_tokens': 1000
    }, timeout=20)
elapsed = time.time()-start
print(f'Status: {r.status_code}, Time: {elapsed:.1f}s')
print(f'Encoding: {r.encoding}')

# Try different decodings
raw = r.content
print(f'Raw bytes (first 200): {raw[:200]}')
print(f'UTF-8: {raw.decode("utf-8", errors="replace")[:500]}')

import json
data = json.loads(raw.decode('utf-8'))
content = data['choices'][0]['message']['content']
print(f'Content: {content}')
