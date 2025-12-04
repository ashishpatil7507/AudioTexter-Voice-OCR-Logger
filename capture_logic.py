import os
import threading
import queue
import whisper
import numpy as np
import pyaudio
import wave
import warnings
warnings.filterwarnings("ignore")

# Save directory for logs
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "AudioTexter")
os.makedirs(SAVE_DIR, exist_ok=True)

# Load Whisper model
try:
    model = whisper.load_model("base")
    print("✅ Whisper model loaded successfully")
except Exception as e:
    print(f"❌ Error loading Whisper model: {e}")
    model = whisper.load_model("base")

# Shared state
audio_queue = queue.Queue()
running = False
audio_stream = None
pa = None

def get_device_name(device_index):
    """Get the name of an audio device by index"""
    try:
        p = pyaudio.PyAudio()
        device_info = p.get_device_info_by_index(device_index)
        p.terminate()
        return device_info['name']
    except:
        return f"Device {device_index}"

def find_stereo_mix_device():
    """Find Stereo Mix or similar loopback device on Windows"""
    try:
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            device_name = device_info['name'].lower()
            # Look for stereo mix, loopback, or similar devices
            if any(keyword in device_name for keyword in ['stereo mix', 'loopback', 'what you hear', 'system audio', 'virtual audio']):
                print(f"🎯 Found system audio device: {device_info['name']}")
                p.terminate()
                return i
        
        # If no stereo mix found, try to find any device with input channels
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"🎯 Using fallback device: {device_info['name']}")
                p.terminate()
                return i
                
        p.terminate()
        return None
    except Exception as e:
        print(f"❌ Error finding audio devices: {e}")
        return None

def start_voice_capture(device_index=None):
    """Starts system audio recording - AUTOMATIC mode"""
    global running, audio_stream, pa
    
    running = True
    
    try:
        pa = pyaudio.PyAudio()
        
        # If no device specified, try to find Stereo Mix
        if device_index is None:
            device_index = find_stereo_mix_device()
            if device_index is None:
                print("❌ No system audio device found. Trying default...")
                device_info = pa.get_default_input_device_info()
                device_index = device_info['index']
        
        device_info = pa.get_device_info_by_index(device_index)
        print(f"🎧 Using audio device: {device_info['name']}")
        
        # Use 16000 Hz sample rate for Whisper
        sample_rate = 16000
        
        audio_stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,  # Mono
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=2048,  # Smaller buffer for faster response
            stream_callback=audio_callback
        )
        
        audio_stream.start_stream()
        print("✅ System audio capture started - AUTO MODE")
        
    except Exception as e:
        print(f"❌ Error starting audio capture: {e}")
        running = False
        if pa:
            pa.terminate()

def audio_callback(in_data, frame_count, time_info, status):
    """Callback for real-time audio processing"""
    if running:
        audio_queue.put(in_data)
    return (in_data, pyaudio.paContinue)

def stop_voice_capture():
    """Stops audio recording"""
    global running, audio_stream, pa
    
    running = False
    if audio_stream:
        try:
            audio_stream.stop_stream()
            audio_stream.close()
        except:
            pass
        audio_stream = None
    
    if pa:
        try:
            pa.terminate()
        except:
            pass
        pa = None
    
    print("🛑 Audio capture stopped")

def voice_transcription_generator():
    """Generator that yields transcribed text from system audio - CONTINUOUS mode"""
    audio_buffer = b""
    silence_counter = 0
    max_silence_chunks = 10  # Continue for 10 chunks of silence before stopping
    
    print("🎙️ Starting continuous transcription...")
    
    while running:
        try:
            # Collect audio data with timeout
            try:
                audio_chunk = audio_queue.get(timeout=1.0)
                audio_buffer += audio_chunk
                silence_counter = 0  # Reset silence counter when we get audio
            except queue.Empty:
                silence_counter += 1
                if silence_counter > max_silence_chunks:
                    print("⚠️ No audio detected for a while...")
                    silence_counter = 0
                continue
            
            # Process when we have enough audio (2 seconds)
            if len(audio_buffer) >= 16000 * 2 * 2:  # 2 seconds at 16kHz, 16-bit
                # Take 2 seconds of audio for processing
                process_data = audio_buffer[:16000 * 2 * 2]
                audio_buffer = audio_buffer[16000 * 2 * 2:]  # Keep remaining audio
                
                # Convert to numpy array for Whisper
                audio_np = np.frombuffer(process_data, np.int16).astype(np.float32) / 32768.0
                
                if len(audio_np) > 1000:  # Ensure we have meaningful audio
                    try:
                        result = model.transcribe(
                            audio_np,
                            language="en",
                            fp16=False,
                            no_speech_threshold=0.6,  # Be less strict about silence
                            logprob_threshold=-1.0,
                            compression_ratio_threshold=2.4
                        )
                        
                        text = result.get('text', '').strip()
                        if text and len(text) > 3:  # Even short phrases
                            # Clean and yield
                            clean_text = ' '.join(text.split())
                            yield f"🎧 {clean_text}"
                        else:
                            # If no speech detected, continue silently
                            continue
                            
                    except Exception as e:
                        print(f"⚠️ Transcription error: {e}")
                        continue
                        
        except Exception as e:
            print(f"⚠️ Processing error: {e}")
            continue
    
    # Process any remaining audio when stopping
    if len(audio_buffer) > 16000 * 1:  # At least 1 second
        try:
            audio_np = np.frombuffer(audio_buffer, np.int16).astype(np.float32) / 32768.0
            result = model.transcribe(audio_np, language="en", fp16=False)
            text = result.get('text', '').strip()
            if text:
                yield f"🎧 {text}"
        except Exception as e:
            print(f"⚠️ Final transcription error: {e}")

if __name__ == "__main__":
    # Test the system
    print("Testing audio devices...")
    stereo_mix_index = find_stereo_mix_device()
    if stereo_mix_index is not None:
        print(f"✅ System audio device found: {get_device_name(stereo_mix_index)}")
    else:
        print("❌ No system audio device found")