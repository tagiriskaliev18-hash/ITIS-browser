import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''    def on_ai_response(self, response):
        self.ai_append("ИИ", response)
        self.ai_status.setText("● Готов")
        self.ai_status.setStyleSheet("color: #00FFD1; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_send_btn.setEnabled(True)'''

new_func = '''    def on_ai_response(self, response):
        import re
        pointers = re.findall(r'\\[POINTER:\\s*(.*?)\\s*\\|\\s*(.*?)\\]', response)
        clean_response = re.sub(r'\\[POINTER:.*?\\]', '', response).strip()
        
        if clean_response:
            self.ai_append("ИИ", clean_response)
            
        self.ai_status.setText("● Готов")
        self.ai_status.setStyleSheet("color: #00FFD1; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_send_btn.setEnabled(True)
        
        current_tab = self.tabs.currentWidget()
        if current_tab and pointers:
            for selector, text in pointers:
                # Escape quotes
                selector = selector.replace('"', '\\\\"')
                text = text.replace('"', '\\\\"')
                js_draw = f"""
                (function() {{
                    let el = document.querySelector("{selector}");
                    if (!el) return;
                    let rect = el.getBoundingClientRect();
                    let overlay = document.createElement('div');
                    overlay.style.position = 'absolute';
                    overlay.style.left = (rect.left + window.scrollX) + 'px';
                    overlay.style.top = (rect.top + window.scrollY) + 'px';
                    overlay.style.width = rect.width + 'px';
                    overlay.style.height = rect.height + 'px';
                    overlay.style.border = '4px solid #0A84FF';
                    overlay.style.boxShadow = '0 0 20px rgba(10,132,255,0.8)';
                    overlay.style.borderRadius = '6px';
                    overlay.style.pointerEvents = 'none';
                    overlay.style.zIndex = '999999';
                    overlay.style.transition = 'all 0.5s ease';
                    
                    let label = document.createElement('div');
                    label.innerText = "{text}";
                    label.style.position = 'absolute';
                    label.style.bottom = '100%';
                    label.style.left = '0';
                    label.style.backgroundColor = '#0A84FF';
                    label.style.color = '#FFF';
                    label.style.padding = '6px 12px';
                    label.style.fontSize = '14px';
                    label.style.fontWeight = 'bold';
                    label.style.borderRadius = '6px';
                    label.style.fontFamily = 'sans-serif';
                    label.style.whiteSpace = 'nowrap';
                    
                    overlay.appendChild(label);
                    document.body.appendChild(overlay);
                    
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    
                    setTimeout(() => overlay.remove(), 8000);
                }})();
                """
                current_tab.webview.page().runJavaScript(js_draw)
'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done")
else:
    print("Could not find old func. Ensure encoding matches.")
