import sys
import os
import threading
import time
from PyQt6.QtCore import QUrl, Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QTabWidget, QSplitter,
                             QTextEdit, QLabel, QListWidget, QProgressBar)
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

# ==========================================
# CORPORATE MONITORING & RESTRICTION SYSTEM
# ==========================================
class CorporateMonitor:
    def __init__(self):
        # Example domains that might be restricted in a corporate environment
        self.blocked_domains = ["facebook.com", "instagram.com", "reddit.com", "games.com", "tiktok.com"]
        self.history_log = []

    def is_allowed(self, url: str) -> bool:
        url_str = url.lower()
        for domain in self.blocked_domains:
            if domain in url_str:
                return False
        return True

    def log_activity(self, url: str):
        self.history_log.append(url)
        print(f"[MONITOR LOG] Accessed: {url}")


# ==========================================
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
                {"role": "system", "content": "Ты — умный ИИ-агент браузера ITIS (как HeyClicky). Ты можешь УПРАВЛЯТЬ страницей. Чтобы кликнуть по видео, кнопке или ссылке, напиши: [CLICK: текст]. Для скролла вниз: [SCROLL_DOWN], вверх: [SCROLL_UP]. Отвечай на русском языке. Если просят включить видео или перейти куда-то — выдавай [CLICK: название]."},
                {"role": "user", "content": f"Содержимое страницы:\n{context}\n\nМой вопрос: {self.query}" if context else self.query}
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


# ==========================================
# BROWSER TAB & INTERCEPTION
# ==========================================
class CustomWebPage(QWebEnginePage):
    def __init__(self, intercept_callback, profile, parent=None):
        super().__init__(profile, parent)
        self.intercept_callback = intercept_callback

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        if url_str.startswith("itis-search:"):
            self.intercept_callback(url_str)
            return False # Block OS from handling it
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class WebTab(QWidget):
    def __init__(self, monitor: CorporateMonitor, ai_callback):
        super().__init__()
        self.monitor = monitor
        self.ai_callback = ai_callback

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar Container
        self.toolbar_container = QWidget()
        self.toolbar_container.setFixedHeight(55) # Fixes the squished layout issue
        self.toolbar_container.setStyleSheet("background-color: #16161D; border-bottom: 1px solid #282833;")
        self.toolbar = QHBoxLayout(self.toolbar_container)
        self.toolbar.setContentsMargins(12, 10, 12, 10)
        self.toolbar.setSpacing(10)

        self.back_btn = QPushButton("◀")
        self.forward_btn = QPushButton("▶")
        self.reload_btn = QPushButton("↻")
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Поиск ITIS или введите URL...")
        self.ask_ai_btn = QPushButton("✨ ИИ-Анализ")

        # Style toolbar buttons
        btn_style = """
            QPushButton { background: transparent; color: #A0A0B0; border: none; font-size: 14px; padding: 6px 10px; border-radius: 6px; }
            QPushButton:hover { background: rgba(255, 255, 255, 0.05); color: #FFFFFF; }
            QPushButton:pressed { background: rgba(10, 132, 255, 0.2); color: #FFFFFF; }
        """
        self.back_btn.setStyleSheet(btn_style)
        self.forward_btn.setStyleSheet(btn_style)
        self.reload_btn.setStyleSheet(btn_style)
        
        # Style URL bar (3D glassmorphism)
        self.url_bar.setStyleSheet("""
            QLineEdit { 
                background: linear-gradient(180deg, #1A1A24 0%, #12121A 100%); 
                color: #E2E2E2; 
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-top: 1px solid rgba(255, 255, 255, 0.15);
                padding: 8px 16px; 
                border-radius: 16px; font-size: 13px; font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #0A84FF; background: #1C1C26; }
        """)
        
        # 3D glowing primary button
        self.ask_ai_btn.setStyleSheet("""
            QPushButton { 
                background: linear-gradient(180deg, #0A84FF 0%, #0055FF 100%);
                color: #FFFFFF; border-radius: 14px; padding: 8px 18px; font-weight: bold; font-family: 'Segoe UI'; 
                border: 1px solid #0055FF;
                border-top: 1px solid rgba(255, 255, 255, 0.4);
                border-bottom: 2px solid #003399;
            }
            QPushButton:hover { background: linear-gradient(180deg, #1A94FF 0%, #0066FF 100%); }
        """)

        self.toolbar.addWidget(self.back_btn)
        self.toolbar.addWidget(self.forward_btn)
        self.toolbar.addWidget(self.reload_btn)
        self.toolbar.addWidget(self.url_bar, 1)
        self.toolbar.addWidget(self.ask_ai_btn)

        self.layout.addWidget(self.toolbar_container)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(2)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { border: none; background: #16161D; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0A84FF, stop:1 #00FFD1); }
        """)
        self.layout.addWidget(self.progress)

        # Web View
        self.webview = QWebEngineView()
        # Set custom page to intercept protocols
        self.custom_page = CustomWebPage(self.navigate_to, self.webview.page().profile(), self.webview)
        self.webview.setPage(self.custom_page)
        self.layout.addWidget(self.webview)

        # Connections
        self.url_bar.returnPressed.connect(self.navigate)
        self.back_btn.clicked.connect(self.webview.back)
        self.forward_btn.clicked.connect(self.webview.forward)
        self.reload_btn.clicked.connect(self.webview.reload)
        self.webview.urlChanged.connect(self.update_url_bar)
        self.webview.loadProgress.connect(self.update_progress)
        self.webview.loadFinished.connect(self.load_finished)
        
        self.ask_ai_btn.clicked.connect(self.trigger_ai)

        # Start URL
        start_url = QUrl.fromLocalFile(os.path.abspath("start_page.html")).toString()
        self.navigate_to(start_url)

    def navigate(self):
        url = self.url_bar.text()
        if not url.startswith("http") and not url.startswith("file://") and not url.startswith("itis-search:"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                import urllib.parse
                url = "itis-search://search/?q=" + urllib.parse.quote(url)
        self.navigate_to(url)

    def navigate_to(self, url):
        import urllib.parse
        if url.startswith("itis-search://search/?q="):
            query = url.replace("itis-search://search/?q=", "")
            query = urllib.parse.unquote(query)
            
            # Switch to Brave Search for optimal independent/pirate search experience.
            # No Google tracking, no Yandex, no CAPTCHAs.
            search_url = f"https://search.brave.com/search?q={urllib.parse.quote(query)}"
            self.webview.setUrl(QUrl(search_url))
            self.monitor.log_activity(search_url)
            return

        if self.monitor.is_allowed(url):
            self.monitor.log_activity(url)
            self.webview.setUrl(QUrl(url))
        else:
            self.webview.setHtml(f"<html><body style='background-color:#0D0D12; color:#FF3B30; font-family:sans-serif; text-align:center; margin-top: 150px;'><h1>ДОСТУП ЗАПРЕЩЕН</h1><p>Домен <b>{url}</b> заблокирован корпоративной политикой безопасности ITIS.</p></body></html>")
            self.url_bar.setText(url)

    def update_url_bar(self, q):
        url_str = q.toString()
        if "start_page.html" in url_str and url_str.startswith("file:///"):
            self.url_bar.clear()
        else:
            self.url_bar.setText(url_str)
            self.url_bar.setCursorPosition(0)
        
    def update_progress(self, progress):
        self.progress.setValue(progress)
        self.progress.show()
        
    def load_finished(self):
        self.progress.hide()

    def trigger_ai(self):
        # We fetch the plain text of the current page and send it to the AI
        self.webview.page().toPlainText(self._on_html_ready)
        
    def _on_html_ready(self, text):
        url = self.url_bar.text()
        self.ai_callback(url, text)


# ==========================================
# MAIN WINDOW & AI AGENT
# ==========================================
class ITISBrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ITIS - Intelligence Browser")
        self.setWindowIcon(QIcon("logo.png"))
        self.resize(1600, 900)
        self.setStyleSheet("background-color: #0D0D12; color: #E2E2E2; font-family: 'Segoe UI', sans-serif;")

        self.monitor = CorporateMonitor()
        
        # Bypass CAPTCHAs by setting a Firefox User-Agent (Firefox system)
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0")

        # Main layout splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #282833; width: 1px; }")
        self.setCentralWidget(self.splitter)

        # Tab Widget for Browser
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #0D0D12; color: #7A7A8C; padding: 12px 24px; border: none; font-size: 13px; font-weight: 500;}
            QTabBar::tab:selected { background: #16161D; color: #FFFFFF; border-top: 2px solid #0A84FF; border-top-left-radius: 6px; border-top-right-radius: 6px;}
            QTabBar::tab:hover:!selected { background: #1C1C24; color: #E2E2E2; }
        """)
        
        # Add new tab button to tab bar
        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setStyleSheet("QPushButton { background: transparent; color: #7A7A8C; font-weight: bold; font-size: 18px; padding: 8px 12px; } QPushButton:hover { color: #FFFFFF; }")
        self.add_tab_btn.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.add_tab_btn, Qt.Corner.TopRightCorner)

        self.splitter.addWidget(self.tabs)

        # AI Agent Panel
        self.ai_panel = QWidget()
        self.ai_panel.setStyleSheet("background-color: #16161D;")
        self.ai_layout = QVBoxLayout(self.ai_panel)
        self.ai_layout.setContentsMargins(20, 20, 20, 20)
        self.ai_layout.setSpacing(15)
        
        # Header
        self.ai_header = QLabel("⚡ ИИ-Ассистент ITIS")
        self.ai_header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.ai_header.setStyleSheet("color: #FFFFFF; padding-bottom: 5px;")
        self.ai_layout.addWidget(self.ai_header)
        
        # Status Label
        self.ai_status = QLabel("● Готов")
        self.ai_status.setStyleSheet("color: #00FFD1; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_layout.addWidget(self.ai_status)
        
        # Chat log
        self.ai_chat_log = QTextEdit()
        self.ai_chat_log.setReadOnly(True)
        self.ai_chat_log.setStyleSheet("""
            QTextEdit {
                background-color: #0D0D12; border: 1px solid #282833; 
                padding: 15px; border-radius: 12px; font-size: 13px; line-height: 1.5;
            }
        """)
        self.ai_layout.addWidget(self.ai_chat_log)
        
        # Input area layout
        self.input_layout = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Спросите что-нибудь об этой странице...")
        self.ai_input.setStyleSheet("""
            QLineEdit {
                background-color: #0D0D12; border: 1px solid #282833; 
                padding: 12px 15px; border-radius: 20px; color: #FFFFFF; font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #0A84FF; }
        """)
        self.input_layout.addWidget(self.ai_input)
        
        self.ai_send_btn = QPushButton("➤")
        self.ai_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF; color: white; border-radius: 20px; 
                min-width: 40px; max-width: 40px; min-height: 40px; font-size: 16px;
            }
            QPushButton:hover { background-color: #0070DF; }
        """)
        self.input_layout.addWidget(self.ai_send_btn)
        
        self.ai_layout.addLayout(self.input_layout)

        self.splitter.addWidget(self.ai_panel)
        
        # Splitter sizes (80% browser, 20% AI)
        self.splitter.setSizes([1280, 320])

        self.last_html_context = ""
        self.ai_worker = AILogicThread()
        self.ai_worker.response_ready.connect(self.on_ai_response)

        # Add initial tab
        self.add_new_tab()

        # Connect AI signals
        self.ai_send_btn.clicked.connect(self.on_ai_chat)
        self.ai_input.returnPressed.connect(self.on_ai_chat)

        self.ai_append("Система", "Добро пожаловать в ITIS Browser. ИИ-агент готов к работе.")

    def add_new_tab(self):
        new_tab = WebTab(self.monitor, self.handle_ai_page_context)
        idx = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(idx)
        
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def handle_ai_page_context(self, url, html):
        self.last_html_context = html
        self.ai_append("Система", f"Захвачено {len(html)} символов контекста с {url}.")
        self.ai_append("ИИ", f"Я проанализировал страницу: {url}. Что вы хотите узнать?")

    def on_ai_chat(self):
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
            context += f"Current URL: {url}\n\n"
        if page_text:
            context += str(page_text)[:3000]
        self.ai_worker.context_html = context
        self.ai_worker.start()
    def on_ai_response(self, response):
        import re
        pointers = re.findall(r'\[POINTER:\s*(.*?)\s*\|\s*(.*?)\]', response)
        clicks = re.findall(r'\[CLICK:\s*(.*?)\]', response)
        scroll_down = '[SCROLL_DOWN]' in response
        scroll_up = '[SCROLL_UP]' in response
        
        clean_response = re.sub(r'\[POINTER:.*?\]', '', response)
        clean_response = re.sub(r'\[CLICK:.*?\]', '', clean_response)
        clean_response = clean_response.replace('[SCROLL_DOWN]', '').replace('[SCROLL_UP]', '').strip()
        
        if clean_response:
            self.ai_append("ИИ", clean_response)
            
        self.ai_status.setText("● Готов")
        self.ai_status.setStyleSheet("color: #00FFD1; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        self.ai_send_btn.setEnabled(True)
        
        current_tab = self.tabs.currentWidget()
        if not current_tab: return
        
        if scroll_down:
            current_tab.webview.page().runJavaScript("window.scrollBy({ top: window.innerHeight * 0.8, left: 0, behavior: 'smooth' });")
        if scroll_up:
            current_tab.webview.page().runJavaScript("window.scrollBy({ top: -window.innerHeight * 0.8, left: 0, behavior: 'smooth' });")
            
        if clicks:
            for text in clicks:
                text_clean = text.replace('"', '\"').replace("'", "\'")
                js_click = f"""
                (function() {{
                    let text = "{text_clean}".toLowerCase();
                    let elements = Array.from(document.querySelectorAll('a, button, [role="button"], span, div, h1, h2, h3, h4, h5, h6, yt-formatted-string'));
                    for (let el of elements) {{
                        if (el.innerText && el.innerText.toLowerCase().includes(text) && el.offsetParent !== null) {{
                            el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            el.style.border = '3px solid #FF3366';
                            el.style.boxShadow = '0 0 15px #FF3366';
                            setTimeout(() => el.click(), 800);
                            return true;
                        }}
                    }}
                    return false;
                }})();
                """
                current_tab.webview.page().runJavaScript(js_click)

        if pointers:
            for selector, text in pointers:
                # Escape quotes
                selector = selector.replace('"', '\\"')
                text = text.replace('"', '\\"')
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


    def ai_append(self, sender, text):
        color = "#FFFFFF"
        if sender == "Вы":
            color = "#00FFD1"
        elif sender == "ИИ":
            color = "#0A84FF"
        elif sender == "Система":
            color = "#FF9500"
            
        self.ai_chat_log.append(f'<span style="color: {color};"><b>{sender}:</b></span> {text}<br>')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Cleaner cross-platform look
    window = ITISBrowserApp()
    window.show()
    sys.exit(app.exec())

