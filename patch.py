import sys

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('main.py', 'w', encoding='utf-8') as f:
    skip = False
    for i, line in enumerate(lines):
        if 'def on_ai_chat(self):' in line:
            skip = True
            f.write('''    def on_ai_chat(self):
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
            current_tab.webview.page().toPlainText(lambda text: self._execute_ai_query(user_text, text))
        else:
            self._execute_ai_query(user_text, "")

    def _execute_ai_query(self, user_text, page_text):
        # Run AI logic in background
        self.ai_worker.query = user_text
        self.ai_worker.context_html = page_text
        self.ai_worker.start()
''')
        elif skip and 'def on_ai_response(self, response):' in line:
            skip = False
        if not skip:
            f.write(line)
