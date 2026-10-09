import requests, time, json

print('=== Xyvero (more tokens) ===')
start = time.time()
try:
    r = requests.post('https://xyvero.space/v1/chat/completions',
        headers={'Authorization': 'Bearer sk-FOQVMuXIGrWuWQvMF3wlFM5NDZcsBAQ', 'Content-Type': 'application/json'},
        json={
            'messages': [
                {'role':'system','content':'Reply in Russian. Be very brief, 1-2 sentences max.'},
                {'role':'user','content':'Privet! Kak dela?'}
            ],
            'model': 'deepseek-v4.1-flash',
            'max_tokens': 2000
        }, timeout=20)
    elapsed = time.time()-start
    print(f'Status: {r.status_code}, Time: {elapsed:.1f}s')
    data = r.json()
    msg = data['choices'][0]['message']
    content = msg.get('content', 'EMPTY')
    reasoning = msg.get('reasoning_content', 'NONE')
    print(f'Content: {content}')
    print(f'Reasoning (first 200): {reasoning[:200]}')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== Xyvero (list models) ===')
try:
    r = requests.get('https://xyvero.space/v1/models',
        headers={'Authorization': 'Bearer sk-FOQVMuXIGrWuWQvMF3wlFM5NDZcsBAQ'},
        timeout=10)
    print(f'Status: {r.status_code}')
    data = r.json()
    if 'data' in data:
        for m in data['data'][:20]:
            print(f"  - {m['id']}")
except Exception as e:
    print(f'Error: {e}')
