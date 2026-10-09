import sys

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('self.model = "xyvero"', 'self.model = "deepseek-v4.1-flash"')
content = content.replace('trimmed_context = self.context_html[:15000]', 'trimmed_context = self.context_html[:5000]')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
