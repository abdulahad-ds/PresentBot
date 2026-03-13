import wave
import sounddevice as sd
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pygame
import requests
import io
import pyautogui
import win32gui
import re
from config import load_config ,grammar as g2
import numpy as np
import os, sys

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename

os.environ['SSL_CERT_FILE'] = resource_path('cacert.pem')

log_callback = print
confidence_callback = lambda v: None
stop_flag = lambda: False

cfg = load_config()

DEEPGRAM_API_KEY  = cfg["api_key"]
NAME = [n.strip() for n in cfg["names"].split(",")]
ROLL_NO = cfg["roll_list"]
PRESENT_AUDIO = cfg["present_audio"]
CHUNK_DURATION = cfg["chunk_duration"]
activity_limit = cfg["activity_limit"]
present_limit = cfg["present_limit"]
attendance_limit = cfg["attendance_limit"]
selected_option = cfg["mode"]          # "alarm" / "present" / "both"
browser = cfg["browser"]
vb_cable = cfg["vb_cable"]
model_choice = cfg["model"]         # "deepgram" / "vosk"
SAMPLE_RATE = 16000
other_rolls= cfg["other_rolls"]
other_names= [[n] for n in cfg["classmate_names"]]
threshold = cfg["confidence_threshold"]

if model_choice == "deepgram":
    keywords_param = ",".join([f"{name}:5" for name in NAME])
    frames = []

elif model_choice == "vosk":
    import vosk, json, queue
    audio_queue  = queue.Queue()
    word_confidence = cfg.get("word_confidence", 0.6)

    # build grammar from NAME + common words
    grammar_names = ",".join([f'"{n}"' for n in NAME])
    grammar = g2

    vosk_model      = vosk.Model(cfg["vosk_path"])
    vosk_recognizer = vosk.KaldiRecognizer(vosk_model, SAMPLE_RATE, grammar)
    vosk_recognizer.SetWords(True)

name_called          = False
attendance_confidence= 0
attendance_started   = False
wake_up_triggered    = False
present_count        = 0
timer_attendance     = 0
timer_last_present   = 0
timer_last_activity  = 0
attendance_word_used = False


pygame.init()
pygame.mixer.init()

def has_audio(audio_bytes, threshold=200):
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
    return rms > threshold

def find_audio_device():
    devices = sd.query_devices()
    
    if vb_cable:
        for i, device in enumerate(devices):
            if "cable output" in device['name'].lower() and device['max_input_channels'] > 0:
                log_callback(f"Found VB-Cable: [{i}] {device['name']}")
                return i
        log_callback("VB-Cable not found! Falling back to Stereo Mix.")

    for i, device in enumerate(devices):
        if "stereo mix" in device['name'].lower() and device['max_input_channels'] > 0:
            log_callback(f"Found Stereo Mix: [{i}] {device['name']}")
            return i

    log_callback("Neither VB-Cable nor Stereo Mix found! Check audio settings.")
    return None

def transcribe_deepgram(audio_bytes):
    try:
        response = requests.post(
            f"https://api.deepgram.com/v1/listen?model=nova-2&language=hi-Latn&punctuate=false&keywords={keywords_param}",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            data=audio_bytes,
            timeout=10
        )
        return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"].lower().strip()
    except Exception as e:
        log_callback(f"Deepgram error: {e}")
        return ""

def transcribe_vosk(data):
    if vosk_recognizer.AcceptWaveform(data):
        result = json.loads(vosk_recognizer.Result())
        words  = result.get("result", [])
        if words:
            filtered = [w["word"] for w in words if w["conf"] >= word_confidence]
            return " ".join(filtered)
    return ""

def alarm():

    devices = AudioUtilities.GetSpeakers()
    interface = devices._dev.Activate(       
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)
    log_callback("Volume maximized!")

    pygame.mixer.music.load("alarm.mp3")
    pygame.mixer.music.play(-1)
    log_callback("ALARM! Will stop after 10 seconds.")
    time.sleep(10)
    pygame.mixer.music.stop()

def is_active_meet(window_title):
    pattern = r"meet - .+ - google chrome"
    return bool(re.search(pattern, window_title.lower()))

def find_session():

    current = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()    
    if browser not in current:
        for i in range (1,8):
            pyautogui.keyDown('alt')
            time.sleep(0.05)
            for _ in range(i):
                pyautogui.press('tab')
                time.sleep(0.05)
            pyautogui.keyUp('alt')
            time.sleep(0.1)
            current = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()
            if browser in current:
                for _ in range (8):
                    current = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()
                    if not is_active_meet(current):
                        pyautogui.hotkey('ctrl', 'tab')
                        time.sleep(0.1)
                    else :
                        return True
        else:
            log_callback("Error! Browser not in recent tabs, cannot turn mic on.")   
            return False
        current = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()

        
    
    else:
        return False

def say_present():

    if not find_session():
        print("Error!Meet session not found, starting alarm.")
        alarm()
        return


    devices = AudioUtilities.GetSpeakers()
    interface = devices._dev.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

    pyautogui.hotkey('ctrl', 'd')   # unmute
    time.sleep(0.3)

    sound = pygame.mixer.Sound(PRESENT_AUDIO)
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))

    pyautogui.hotkey('ctrl', 'd')   # mute again
    log_callback("Said Present!")

def process_text(text):

    global attendance_confidence, attendance_word_used, timer_attendance
    global timer_last_present, present_count, timer_last_activity, present_limit, attendance_limit, activity_limit
    global name_called, attendance_started

    now = time.time()

    if attendance_started:
        for roll in ROLL_NO:
            log_callback(roll)
            if roll in text:
                name_called = True
                return

        for name in NAME:
            if name in text:
                log_callback(f" MY NAME DETECTED: '{name}'")
                name_called = True
                return
    else:
        if "attendance" in text:
            if not attendance_word_used:
                attendance_confidence += 3
                attendance_word_used   = True
                timer_attendance       = now
                log_callback(f" +3 attendance | confidence: {attendance_confidence}")

        if "present" in text:
            
            if now - timer_last_present <=present_limit or timer_last_present==0:
                attendance_confidence+= 2
                present_count+= 1
                timer_last_present= now
                log_callback(" +2 Present | Confidence: ", attendance_confidence)
            else:
                timer_last_present=now
        

        for roll in other_rolls:
            if roll in text:
                if now - timer_last_present<=activity_limit or now - timer_last_activity <=activity_limit:
                    attendance_confidence += 1
                    timer_last_activity    = now
                    log_callback(" +1 Roll No | Confidence: ", attendance_confidence)
                break

        for name_group in other_names:
            for name in name_group:
                if name in text:
                    if now - timer_last_present<=activity_limit or now - timer_last_activity <=activity_limit:
                        attendance_confidence += 1
                        timer_last_activity    = now
                        log_callback(" +1 Name | Confidence: ", attendance_confidence)
                    break
    
def checktimers():
    global attendance_confidence, attendance_word_used,timer_last_present
    global timer_attendance, present_count, present_limit, attendance_limit, activity_limit

    now = time.time()
    if attendance_word_used and present_count == 0:
        if now - timer_attendance >= attendance_limit:
            log_callback(f"Reset Confidence, No activity within {attendance_limit} seconds after attendance keyword.\n")
            attendance_confidence = 0
            attendance_word_used  = False
            timer_attendance      = 0

    if attendance_word_used and now - timer_attendance >= attendance_limit:
        attendance_word_used = False

    if timer_last_present != 0 and now - timer_last_present >= present_limit:
        threshold = cfg["confidence_threshold"]  
        if attendance_confidence < threshold * 0.5:
            log_callback(f"Confidence reset: was below 50% threshold.")
            attendance_confidence = 0
            confidence_callback(0)
        else:
            attendance_confidence = max(0, attendance_confidence - 2)
            log_callback(f"Confidence decayed to {attendance_confidence}")
            confidence_callback(attendance_confidence)
        timer_last_present = now
    
def audio_callback_deepgram(indata, frames_count, time_info, status):
    frames.append(bytes(indata))

def audio_callback_vosk(indata, frames_count, time_info, status):
    audio_queue.put(bytes(indata))

def start():
    global attendance_started, wake_up_triggered

    DEVICE_INDEX = find_audio_device()
    if DEVICE_INDEX is None:
        log_callback("No audio device found! Exiting.")
        return

    callback = audio_callback_deepgram if model_choice == "deepgram" else audio_callback_vosk

    with sd.RawInputStream(
        samplerate = SAMPLE_RATE,
        channels   = 1,
        dtype      = 'int16',
        device     = DEVICE_INDEX,
        callback   = callback
    ):
        log_callback("Starting hearing...\n")
        text=""
        while True:

            if model_choice == "deepgram":
                time.sleep(CHUNK_DURATION)
                if not frames:
                    continue
                audio_data = b"".join(frames)
                frames.clear()
                if has_audio(audio_data):
                    wav_buffer = io.BytesIO()
                    with wave.open(wav_buffer, 'wb') as f:
                        f.setnchannels(1)
                        f.setsampwidth(2)
                        f.setframerate(SAMPLE_RATE)
                        f.writeframes(audio_data)
                    text = transcribe_deepgram(wav_buffer.getvalue())

            elif model_choice == "vosk":
                data = audio_queue.get()
                text = transcribe_vosk(data)


            if text:
                log_callback(f"Heard: {text}")
                process_text(text)

            checktimers()
            confidence_callback(attendance_confidence)

            if attendance_confidence >= threshold and not attendance_started:
                attendance_started = True
                log_callback(f"Attendance confirmed with {attendance_confidence} points")
                if selected_option in ("alarm", "both"):
                    alarm()
                    wake_up_triggered = True
                    if selected_option == "alarm":
                        break

            if name_called and attendance_started and selected_option in ("present", "both"):
                say_present()
                break
            if stop_flag():
                break
            