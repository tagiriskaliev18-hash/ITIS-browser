with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1) Fix on_ai_chat: replace JS-only context with a reliable two-step approach
old_ai_chat = '''    def on_ai_chat(self):
        user_text = self.ai_input.text()
        if not user_text.strip(): return
        self.ai_append("Вы", user_text)
        self.ai_input.clear()
        
        self.ai_status.setText("● Думает...")
        self.ai_status.setStyleSheet("color: #FF9500; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_send_btn.setEnabled(False)
        
        # Get active tab text dynamically instead of relying on the manual button click
        current_tab = self.tabs.currentWidget()
        if current_tab:
            js_code = \'\'\'
                (function() {
                    let elements = document.querySelectorAll('a, button, input');
                    let res = [];
                    elements.forEach(e => {
                        if(e.offsetParent !== null) {
                            let selector = e.tagName.toLowerCase();
                            if (e.id) selector += '#' + e.id;
                            else if (e.className && typeof e.className === 'string') selector += '.' + e.className.split(' ')[0];
                            let text = (e.innerText || e.value || e.placeholder || '').substring(0, 30).replace(/\\n/g, ' ').trim();
                            if (text) res.push(selector + ' : "' + text + '"');
                        }
                    });
                    return 'Visible elements:\\n' + res.join('\\n');
                })();
            \'\'\'
            current_tab.webview.page().runJavaScript(js_code, lambda text: self._execute_ai_query(user_text, text))
        else:
            self._execute_ai_query(user_text, "")

    def _execute_ai_query(self, user_text, page_text):
        # Run AI logic in background
        self.ai_worker.query = user_text
        self.ai_worker.context_html = str(page_text) if page_text else ""
        self.ai_worker.start()'''

new_ai_chat = '''    def on_ai_chat(self):
        user_text = self.ai_input.text()
        if not user_text.strip(): return
        self.ai_append("Вы", user_text)
        self.ai_input.clear()
        
        self.ai_status.setText("● Думает...")
        self.ai_status.setStyleSheet("color: #FF9500; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_send_btn.setEnabled(False)
        
        # Always use toPlainText — it works on every page reliably (no CSP issues)
        current_tab = self.tabs.currentWidget()
        if current_tab:
            url = current_tab.url_bar.text() or ""
            current_tab.webview.page().toPlainText(lambda text: self._execute_ai_query(user_text, text, url))
        else:
            self._execute_ai_query(user_text, "", "")

    def _execute_ai_query(self, user_text, page_text, url=""):
        # Run AI logic in background
        self.ai_worker.query = user_text
        context = ""
        if url:
            context += f"Current URL: {url}\\n\\n"
        if page_text:
            context += str(page_text)[:3000]
        self.ai_worker.context_html = context
        self.ai_worker.start()'''

if old_ai_chat in content:
    content = content.replace(old_ai_chat, new_ai_chat)
    print("Replaced on_ai_chat OK")
else:
    print("ERROR: Could not find on_ai_chat block")

# 2) Fix the AI system prompt — remove POINTER stuff that confuses the model, make it simple and fast
old_system = '''{"role": "system", "content": "You are the ITIS Browser AI Agent. You are integrated directly into the corporate browser ITIS. You can see the visible interactive elements on the page. Be concise, fast, and helpful.\\n\\nIMPORTANT: You can draw on the user's screen to guide them (like a teacher). To do this, include the command [POINTER: css_selector | text] in your response. For example: \\"To search, click here: [POINTER: input.search-box | Type your query here]\\" or \\"[POINTER: button#submit | Click this button]\\". You MUST use one of the CSS selectors provided in the context exactly as written."}'''
new_system = '''{"role": "system", "content": "Ты — ИИ-ассистент браузера ITIS. Ты видишь текст текущей веб-страницы пользователя. Отвечай кратко и по делу на русском языке. Помогай разобраться в содержимом страницы, отвечай на вопросы о ней, и давай полезные советы."}'''

if old_system in content:
    content = content.replace(old_system, new_system)
    print("Replaced system prompt OK")
else:
    print("ERROR: Could not find system prompt")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All done!")
