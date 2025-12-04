# 🎙️ AudioTexter  
### 🔊 Automatic System Audio-to-Text Transcription (With Whisper + PyAudio + PyQt5)

AudioTexter is a **desktop application** that automatically captures **system audio** (YouTube, meetings, courses, apps, music, etc.) and converts it into **real-time text** using OpenAI Whisper.

It supports:
- 🎧 Bluetooth headphones  
- 🎧 Wired earphones  
- 🔊 Any Windows system audio output  
- 📝 Live continuous transcription  
- 🚀 Auto-detects system audio device (“Stereo Mix / Loopback”)

---

## 📌 Features

### 🎙 Auto System Audio Capture
- Detects Stereo Mix / Loopback devices automatically  
- Captures audio from:
  - YouTube  
  - Online classes  
  - Zoom/Google Meet/Teams  
  - Games  
  - Music apps  
  - Any system audio  

### 📝 Real-Time Transcription
- Uses **OpenAI Whisper (base model)**  
- Low-latency transcription  
- Works in continuous real-time mode  
- Shows live transcribed text in UI  

### 💻 Modern PyQt5 UI
- Dark themed modern UI  
- Multi-page layout:
  - Welcome Page  
  - Main Recording Page  
  - Help Page  
- Buttons for Start, Stop, Help, Support  

### 💾 Automatic Log Saving
- Saves logs to:


---

## 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| UI | PyQt5 |
| Audio Capture | PyAudio |
| Speech-to-Text | Whisper (OpenAI) |
| Backend Logic | Python |
| OS Support | Windows recommended |

---

## 📥 Installation

### 1️⃣ Install Python 3.9+  
Download from: https://www.python.org/downloads/

### 2️⃣ Install required packages

```bash
pip install pyaudio PyQt5 openai-whisper numpy
```

###▶️ Run the Application
```bash
python AudioTexter.py
```

### 🎧 How It Works – Internally
### 🔍 1. Auto Device Detection

The app automatically looks for devices like:

Stereo Mix

Loopback

Virtual Audio Cable

### “What U Hear”

(from find_stereo_mix_device() in capture_logic.py)

### 🎵 2. Live Audio Capture

PyAudio captures audio stream in callback mode:

audio_stream = pa.open(..., stream_callback=audio_callback)
---

### 🧠 3. Whisper STT

Every ~2 seconds of audio is converted to text:

result = model.transcribe(audio_np, language="en")
---

### 🔁 4. Real-Time UI Updates

UI updates on a background thread without freezing.

### ❓ Help – Enable System Audio Capture on Windows

Right-click volume icon

Sounds → Recording

Enable Stereo Mix

Set as Default Device

Restart AudioTexter
---

