import vosk 
import wave
import json
import queue
import sounddevice as sd

DEVICE_INDEX = 1
SAMPLE_RATE  = 16000 

# Load model
model = vosk.Model(r"D:\Others\Projects\PresentBot\PresentBot\vosk-model-en-us-0.22-lgraph")
#grammar = '["Murtaza", "Ghulam", "Muhammad", "Ahad", "AbdulAhad", "Gohar"]'
grammar = '["present","two","five","nine","four"]'
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE,grammar)

#wav_file = wave.open(r"D:\Others\Projects\PresentBot\test_capture.wav", "rb")

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

with sd.RawInputStream(
    samplerate = SAMPLE_RATE,
    channels   = 1,          
    dtype      = 'int16',
    device     = DEVICE_INDEX,
    callback   = audio_callback
):
    while True:
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print("Final:", text)
        else: 
            partial = json.loads(recognizer.PartialResult())
            if partial.get("partial"):
                print("Partial:", partial["partial"])