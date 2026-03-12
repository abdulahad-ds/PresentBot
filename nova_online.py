import vosk 
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import wave
import json
import queue
import sounddevice as sd
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pygame
import requests
import io

DEEPGRAM_API_KEY = ""


ROLL_NO=["two","five","nine","four"]
NAME=["muhammad","abdul","muhammad abdul","muhammadabdul","muhammadabdulahad", "abdulahad","ahad"]
DEVICE_INDEX = 2
CHUNK_DURATION = 3
frames = []
SAMPLE_RATE  = 16000 

attendance_confidence = 0       
attendance_started = False  
wake_up_triggered = False   
present_count=0

timer_attendance   = 0      # when "attendance" was last heard
timer_last_present = 0      
timer_last_activity= 0      
attendance_word_used = False 

activity_limit=15   #the maximum gap between each activty
present_limit=25
attendance_limit=45

other_names=[["hamza","hamza sheikh","hamzasheikh"],["saqib","saqib qazi"],["hassan","hassan shakil"], ["eman", "eman faisal"]]
other_rolls=["zero six","zero two", "one two", "two zero"]
roll_keywords = ["two five","five zero","five one","five two", "five three","five four","five six"]

def transcribe_chunk(audio_bytes):
    try:
        response = requests.post(
            "https://api.deepgram.com/v1/listen?model=nova-2&language=hi-Latn&punctuate=false",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            data=audio_bytes,
            timeout=10
        )
        return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"].lower().strip()
    except Exception as e:
        print(f"API error: {e}")
        return ""

def alarm():
    pygame.init()
    pygame.mixer.init()
    devices = AudioUtilities.GetSpeakers()
    interface = devices._dev.Activate(       
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)
    print("Volume maximized!")

    pygame.mixer.music.load("alarm.mp3")
    pygame.mixer.music.play(-1)
    print("ALARM! Press Enter to stop...")
    input()
    pygame.mixer.music.stop()

def audio_callback(indata, frames_count, time_info, status):
    frames.append(bytes(indata))

def process_text(text):

    global attendance_confidence, attendance_word_used, timer_attendance
    global timer_last_present, present_count, timer_last_activity, present_limit, attendance_limit, activity_limit

    now = time.time()
    

    if "attendance" in text:
        if not attendance_word_used:
            attendance_confidence += 3
            attendance_word_used   = True
            timer_attendance       = now
            print(f" +3 attendance | confidence: {attendance_confidence}")

    if "present" in text:
        
        if now - timer_last_present <=present_limit or timer_last_present==0:
            attendance_confidence+= 2
            present_count+= 1
            timer_last_present= now
            print(" +2 Present | Confidence: ", attendance_confidence)
        else:
            timer_last_present=now
    

    for roll in roll_keywords+other_rolls:
        if roll in text:
            if now - timer_last_present<=activity_limit or now - timer_last_activity <=activity_limit:
                attendance_confidence += 1
                timer_last_activity    = now
                print(" +1 Roll No | Confidence: ", attendance_confidence)
            break

    for name_group in other_names:
        for name in name_group:
            if name in text:
                if now - timer_last_present<=activity_limit or now - timer_last_activity <=activity_limit:
                    attendance_confidence += 1
                    timer_last_activity    = now
                    print(" +1 Name | Confidence: ", attendance_confidence)
                break

def checktimers():
    global attendance_confidence, attendance_word_used
    global timer_attendance, present_count, present_limit, attendance_limit, activity_limit

    now = time.time()
    if attendance_word_used and present_count == 0:
        if now - timer_attendance >= attendance_limit:
            print(f"Reset Confidence, No activity within {attendance_limit} seconds after attendance keyword.\n")
            attendance_confidence = 0
            attendance_word_used  = False
            timer_attendance      = 0

    if attendance_word_used and now - timer_attendance >= attendance_limit:
        attendance_word_used = False


def start():
    with sd.RawInputStream(
        samplerate = SAMPLE_RATE,
        channels   = 1,          
        dtype      = 'int16',
        device     = DEVICE_INDEX,
        callback   = audio_callback
    ):
        print("Starting hearing...\n")
        while True:
            time.sleep(CHUNK_DURATION)
            if not frames:
                continue
            audio_data = b"".join(frames)
            frames.clear()
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(SAMPLE_RATE)
                f.writeframes(audio_data)
            text = transcribe_chunk(wav_buffer.getvalue())

            if text:
                print(f"Heard: {text}")
                process_text(text)

            checktimers()

            if attendance_confidence > 10 :
                attendance_started=True
                print(f"attendance confirmed with {attendance_confidence} points")
                alarm()
                wake_up_triggered=True
                break


start()