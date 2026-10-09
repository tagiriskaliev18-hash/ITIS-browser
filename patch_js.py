import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_fetch = 'current_tab.webview.page().toPlainText(lambda text: self._execute_ai_query(user_text, text))'
js_fetch = """
            js_code = '''
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
            '''
            current_tab.webview.page().runJavaScript(js_code, lambda text: self._execute_ai_query(user_text, text))
"""

if old_fetch in content:
    content = content.replace(old_fetch, js_fetch.strip())
else:
    print("Could not find old fetch")

old_system = '{"role": "system", "content": "You are the ITIS Browser AI Agent. You are integrated directly into the corporate browser \'ITIS (Iskaliev Tagir Independent Surfing)\'. You can see the HTML or text of the page the user is on. Be concise, fast, and helpful. Do not output markdown code blocks for normal text."}'
new_system = '{"role": "system", "content": "You are the ITIS Browser AI Agent. You are integrated directly into the corporate browser ITIS. You can see the visible interactive elements on the page. Be concise, fast, and helpful.\\n\\nIMPORTANT: You can draw on the user\'s screen to guide them (like a teacher). To do this, include the command [POINTER: css_selector | text] in your response. For example: \\"To search, click here: [POINTER: input.search-box | Type your query here]\\" or \\"[POINTER: button#submit | Click this button]\\". You MUST use one of the CSS selectors provided in the context exactly as written."}'

if old_system in content:
    content = content.replace(old_system, new_system)
else:
    print("Could not find old system prompt")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
