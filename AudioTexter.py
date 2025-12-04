import subprocess
import sys
import pyaudio

# Auto-install required packages
try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout,
        QLabel, QStackedLayout, QHBoxLayout, QComboBox
    )
    from PyQt5.QtGui import QFont, QCursor, QDesktopServices
    from PyQt5.QtCore import Qt, QUrl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout,
        QLabel, QStackedLayout, QHBoxLayout, QComboBox
    )
    from PyQt5.QtGui import QFont, QCursor, QDesktopServices
    from PyQt5.QtCore import Qt, QUrl

import capture_logic
import threading
import time


class AudioTexterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎙️ AudioTexter - Auto System Audio Capture")
        self.setGeometry(400, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e2f; color: #f8f8f2; font-family: 'Segoe UI';")

        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)

        self.init_welcome_page()
        self.init_main_page()
        self.init_help_page()

        self.stacked_layout.setCurrentWidget(self.welcome_widget)
        
        # Auto-detect device on startup
        self.auto_detected_device = None

    def init_welcome_page(self):
        self.welcome_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("🎧 Welcome to AudioTexter")
        label.setFont(QFont("Segoe UI", 24))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        desc = QLabel("Automatically captures system audio from courses, YouTube, etc.\nWorks with Bluetooth & wired headphones!")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #bbbbbb;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        continue_btn = self.styled_button("🚀 Continue to App")
        continue_btn.clicked.connect(lambda: self.stacked_layout.setCurrentWidget(self.main_widget))
        layout.addWidget(continue_btn)

        self.welcome_widget.setLayout(layout)
        self.stacked_layout.addWidget(self.welcome_widget)

    def init_main_page(self):
        self.main_widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("🎙️ Auto System Audio-to-Text")
        header.setFont(QFont("Segoe UI", 20))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Status label
        self.status_label = QLabel("🔍 Ready to capture system audio...")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #50fa7b; padding: 10px;")
        layout.addWidget(self.status_label)

        # Audio device info
        device_info_layout = QHBoxLayout()
        self.device_info_label = QLabel("System Audio Device: Auto-detecting...")
        self.device_info_label.setFont(QFont("Segoe UI", 10))
        self.device_info_label.setStyleSheet("color: #8be9fd;")
        device_info_layout.addWidget(self.device_info_label)
        layout.addLayout(device_info_layout)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont("Segoe UI", 12))
        self.output_box.setStyleSheet("""
            background-color: #2e2e3e;
            color: #ffffff;
            padding: 15px;
            border-radius: 5px;
            min-height: 300px;
        """)
        layout.addWidget(self.output_box)

        button_layout = QHBoxLayout()
        self.start_btn = self.styled_button("🎵 Start Auto Capture")
        self.stop_btn = self.styled_button("⏹️ Stop Capture")
        self.help_btn = self.styled_button("ℹ️ Help")
        self.buy_btn = self.styled_button("☕ Support")

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.help_btn.clicked.connect(lambda: self.stacked_layout.setCurrentWidget(self.help_widget))
        self.buy_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://coff.ee/ashishpatil")))

        for btn in [self.start_btn, self.stop_btn, self.help_btn, self.buy_btn]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        self.main_widget.setLayout(layout)
        self.stacked_layout.addWidget(self.main_widget)
        
        # Auto-detect device on main page load
        self.auto_detect_on_startup()

    def auto_detect_on_startup(self):
        """Auto-detect system audio device when app starts"""
        def detect():
            time.sleep(1)  # Small delay to ensure UI is loaded
            stereo_mix_index = capture_logic.find_stereo_mix_device()
            if stereo_mix_index is not None:
                self.auto_detected_device = stereo_mix_index
                device_name = capture_logic.get_device_name(stereo_mix_index)
                self.device_info_label.setText(f"System Audio Device: {device_name} (Auto-detected)")
                self.status_label.setText("✅ System audio device ready! Click 'Start Auto Capture'")
                self.output_box.append("✅ Auto-detected system audio device")
                self.output_box.append("💡 Play your course audio and click 'Start Auto Capture'")
            else:
                self.status_label.setText("❌ No system audio device found. Check Help page.")
                self.output_box.append("❌ Could not auto-detect system audio device")
        
        threading.Thread(target=detect, daemon=True).start()

    def start_recording(self):
        if self.auto_detected_device is None:
            self.output_box.append("❌ No system audio device detected. Please check setup.")
            return
            
        self.output_box.append("🔊 Starting AUTO system audio capture...")
        self.output_box.append("🎧 Now capturing from: YouTube, courses, apps, etc.")
        self.output_box.append("⏳ Listening for audio...")
        
        self.status_label.setText("🔴 LIVE - Capturing system audio...")
        self.status_label.setStyleSheet("color: #ff5555; font-weight: bold;")
        
        # Start capture with auto-detected device
        capture_logic.start_voice_capture(self.auto_detected_device)
        self.transcription_loop()

    def stop_recording(self):
        capture_logic.stop_voice_capture()
        self.output_box.append("🛑 Stopped audio capture.")
        self.status_label.setText("🟢 Ready to capture system audio...")
        self.status_label.setStyleSheet("color: #50fa7b;")

    def transcription_loop(self):
        def update_loop():
            for text in capture_logic.voice_transcription_generator():
                # Update UI in main thread
                self.output_box.append(text)
                # Auto-scroll to bottom
                self.output_box.verticalScrollBar().setValue(
                    self.output_box.verticalScrollBar().maximum()
                )
        
        threading.Thread(target=update_loop, daemon=True).start()

    def init_help_page(self):
        self.help_widget = QWidget()
        layout = QVBoxLayout()

        help_label = QLabel("ℹ️ Auto System Audio Capture")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_label.setFont(QFont("Segoe UI", 20))
        layout.addWidget(help_label)

        help_text = QLabel("""
            <b>🚀 Automatic System Audio Capture</b><br><br>
            
            <b>How it works:</b><br>
            • Automatically detects system audio device<br>
            • Captures audio from ANY app (YouTube, courses, music, etc.)<br>
            • Works with Bluetooth AND wired headphones<br>
            • Real-time continuous transcription<br>
            • Runs until you click Stop<br><br>
            
            <b>Setup for Windows:</b><br>
            1. Right-click speaker icon → Sounds<br>
            2. Recording tab → Enable "Stereo Mix"<br>
            3. Set Stereo Mix as default device<br>
            4. Restart this app<br><br>
            
            <b>What it captures:</b><br>
            ✓ YouTube videos & courses<br>
            ✓ Zoom/Teams meetings<br>
            ✓ Music & podcasts<br>
            ✓ Game audio<br>
            ✓ Any system sound<br><br>
            
            <b>Tips for best results:</b><br>
            • Keep system volume at 50-80%<br>
            • Reduce background noise<br>
            • Speak clearly in videos<br>
            • Use good quality audio sources<br><br>
            
            <b>Need help?</b><br>
            📧 ashishpatil.cyber@gmail.com<br>
            ☕ https://coff.ee/ashishpatil
        """)
        help_text.setFont(QFont("Segoe UI", 11))
        help_text.setStyleSheet("color: #dddddd; padding: 10px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        back_btn = self.styled_button("⬅ Back to Main")
        back_btn.clicked.connect(lambda: self.stacked_layout.setCurrentWidget(self.main_widget))
        layout.addWidget(back_btn)

        self.help_widget.setLayout(layout)
        self.stacked_layout.addWidget(self.help_widget)

    def styled_button(self, text):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #44475a;
                color: white;
                padding: 10px 15px;
                font-size: 14px;
                border: 1px solid #6272a4;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
        """)
        return btn


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTexterApp()
    window.show()
    sys.exit(app.exec_())