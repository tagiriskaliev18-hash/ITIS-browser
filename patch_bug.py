with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('self.ai_worker.context_html = page_text', 'self.ai_worker.context_html = str(page_text) if page_text else ""')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
