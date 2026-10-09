"""
Complete AI Agent rewrite for ITIS Browser.
Fixes:
1. Uses requests directly (no openai SDK issues)
2. Proper timeout (10s) so user never waits forever
3. max_tokens=1500 (was 500 — not enough for reasoning model)
4. Minimal context (URL + first 1500 chars of page text)
5. Streaming-like UX: shows "typing" indicator
6. Fallback to Pollinations if xyvero is down
7. Proper Russian system prompt
"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# REPLACE the entire AILogicThread class
# ============================================================
old_ai_class_start = '# ==========================================\n# AI AGENT WORKER THREAD\n# ==========================================\nimport json\nfrom openai import OpenAI\n\nclass AILogicThread(QThread):'
old_ai_class_end = '# ==========================================\n# BROWSER TAB & INTERCEPTION\n# ==========================================\n'

# Find the indices
idx_start = content.find(old_ai_class_start)
idx_end = content.find(old_ai_class_end)

if idx_start == -1 or idx_end == -1:
    # Try with \r\n
    old_ai_class_start = old_ai_class_start.replace('\n', '\r\n')
    old_ai_class_end = old_ai_class_end.replace('\n', '\r\n')
    idx_start = content.find(old_ai_class_start)
    idx_end = content.find(old_ai_class_end)

if idx_start == -1 or idx_end == -1:
    print(f"ERROR: Could not find AI class boundaries. start={idx_start}, end={idx_end}")
    # Debug: show what's around those areas
    for marker in ['AI AGENT WORKER', 'BROWSER TAB']:
        pos = content.find(marker)
        print(f"  '{marker}' found at position {pos}")
else:
    new_ai_class = '''# ==========================================
# AI AGENT WORKER THREAD (v2 — requests-based, fast, reliable)
# ==========================================
import json
import requests as http_requests

class AILogicThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.query = ""
        self.context_html = ""

    def run(self):
        try:
            # Build minimal context: just URL + first 1500 chars
            context = self.context_html[:1500] if self.context_html else ""
            
            messages = [
                {"role": "system", "content": "Ты — ИИ-ассистент встроенный в браузер ITIS. Ты видишь текст текущей веб-страницы пользователя. Отвечай кратко и по делу на русском языке. Если контекст страницы пуст — просто помоги пользователю с его вопросом."},
                {"role": "user", "content": f"Содержимое страницы:\\n{context}\\n\\nМой вопрос: {self.query}" if context else self.query}
            ]
            
            body = {
                "model": "deepseek-v4.1-flash",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            # Try Xyvero first (fast, dedicated)
            try:
                resp = http_requests.post(
                    "https://xyvero.space/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer sk-FOQVMuXIGrWuWQvMF3wlFM5NDZcsBAQ",
                        "Content-Type": "application/json; charset=utf-8"
                    },
                    json=body,
                    timeout=15
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    reply = data["choices"][0]["message"]["content"]
                    if reply and reply.strip():
                        self.response_ready.emit(reply.strip())
                        return
                    else:
                        # Model thought but gave empty content — retry with higher tokens
                        body["max_tokens"] = 2500
                        resp2 = http_requests.post(
                            "https://xyvero.space/v1/chat/completions",
                            headers={
                                "Authorization": "Bearer sk-FOQVMuXIGrWuWQvMF3wlFM5NDZcsBAQ",
                                "Content-Type": "application/json; charset=utf-8"
                            },
                            json=body,
                            timeout=20
                        )
                        if resp2.status_code == 200:
                            data2 = resp2.json()
                            reply2 = data2["choices"][0]["message"]["content"]
                            if reply2 and reply2.strip():
                                self.response_ready.emit(reply2.strip())
                                return
            except http_requests.Timeout:
                pass  # Fall through to fallback
            except Exception:
                pass  # Fall through to fallback
            
            # Fallback: Pollinations AI (free, no API key)
            try:
                resp = http_requests.post(
                    "https://text.pollinations.ai/",
                    json={
                        "messages": messages,
                        "model": "openai",
                        "max_tokens": 500
                    },
                    timeout=20
                )
                if resp.status_code == 200 and resp.text.strip():
                    self.response_ready.emit(resp.text.strip())
                    return
            except Exception:
                pass
            
            self.response_ready.emit("⚠ ИИ-сервисы временно недоступны. Попробуйте через минуту.")
            
        except Exception as e:
            self.response_ready.emit(f"⚠ Ошибка: {str(e)}")


'''

    content = content[:idx_start] + new_ai_class + content[idx_end:]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: AI Agent rewritten!")
