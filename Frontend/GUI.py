import os
from dotenv import dotenv_values
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QPainter, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
import sys

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Initialize required files with default values
required_files = {
    'Status.data': 'Initializing...',
    'Mic.data': 'False',
    'Responses.data': ''
}

for filename, default_content in required_files.items():
    file_path = os.path.join(TempDirPath, filename)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(default_content)

# Utility functions
def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query):
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SetMicrophoneStatus(command):
    with open(os.path.join(TempDirPath, 'Mic.data'), "w", encoding='utf-8') as file:
        file.write(command)

def GetMicrophoneStatus():
    with open(os.path.join(TempDirPath, 'Mic.data'), "r", encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(status):
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(status)

def GetAssistantStatus():
    with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
        return file.read()

def ShowTextToScreen(text):
    with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as file:
        file.write(text)

def GraphicsDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)

def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)

# Chat Section
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #ECEFF4;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.chat_text_edit)

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: #ECEFF4; font-size: 16px;")
        layout.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def loadMessages(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages:
                    self.addMessage(messages, '#ECEFF4')
        except FileNotFoundError:
            self.addMessage("No messages found.", '#888888')

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("Status: Not Available")

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

# Initial Screen
class InitialScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Background Gradient
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#4A90E2"))
        gradient.setColorAt(1, QColor("#1C3F60"))
        palette.setBrush(self.backgroundRole(), gradient)
        self.setPalette(palette)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(800, 450))
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        self.icon_label = QLabel()
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.label = QLabel("")
        self.label.setStyleSheet("color: #ECEFF4; font-size: 16px;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            SetMicrophoneStatus("False")
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'))
            SetMicrophoneStatus("True")
        self.toggled = not self.toggled

    def load_icon(self, path):
        pixmap = QPixmap(path)
        self.icon_label.setPixmap(pixmap.scaled(60, 60))

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("Status: Not Available")

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"{Assistantname} AI")
        self.setGeometry(100, 100, 800, 600)

        stacked_widget = QStackedWidget()
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(ChatSection())

        self.setCentralWidget(stacked_widget)

# Run the application
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()