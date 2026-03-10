import vosk 
import wave
import json
import queue
import sounddevice as sd
import time

ROLL_NO=["two","five","nine","four"]
NAME=["muhammad","abdul","muhammad abdul","muhammadabdul","muhammadabdulahad", "abdulahad","ahad"]
DEVICE_INDEX = 2
SAMPLE_RATE  = 16000 

attendance_confidence = 0       
attendance_started = False  
wake_up_triggered = False    
timer1=time.time()
timer2=time.time()
timer3=time.time()
timer4=time.time()

other_names=[["hamza","hamza sheikh","hamzasheikh"],["saqib","saqib qazi"],["hassan","hassan shakil"], ["eman", "eman faisal"]]
other_rolls=["zero six","zero two", "one two", "two zero"]
# Load model
model = vosk.Model(r"D:\Others\Projects\PresentBot\PresentBot\vosk-model-en-us-0.22-lgraph")
#grammar = '["Murtaza", "Hassan", "Muhammad", "Ahad", "AbdulAhad", "Gohar"]'

grammar = '["present","attendance","ahad","muhammad","abdul","abdulahad",' \
'"zero","one","two","three","four","five","six","seven","eight","nine","ten",' \
'"eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen",' \
'"twenty","twenty one","twenty two","twenty three","twenty four","twenty five","twenty six","twenty seven","twenty eight","twenty nine",' \
'"thirty","thirty one","thirty two","thirty three","thirty four","thirty five","thirty six","thirty seven","thirty eight","thirty nine",' \
'"forty","forty one","forty two","forty three","forty four","forty five","forty six","forty seven","forty eight","forty nine",' \
'"fifty","fifty one","fifty two","fifty three","fifty four","fifty five","fifty six","fifty seven","fifty eight","fifty nine",' \
'"sixty","sixty one","sixty two","sixty three","sixty four","sixty five","sixty six","sixty seven","sixty eight","sixty nine",' \
'"seventy","seventy one","seventy two","seventy three","seventy four","seventy five","seventy six","seventy seven","seventy eight","seventy nine",' \
'"eighty","eighty one","eighty two","eighty three","eighty four","eighty five","eighty six","eighty seven","eighty eight","eighty nine",' \
'"ninety","ninety one","ninety two","ninety three","ninety four","ninety five","ninety six","ninety seven","ninety eight","ninety nine","one hundred",' \
'"hamza","hamza sheikh","hamzasheikh",' \
'"sadeem","sadeem arshad","sadeemarshad",' \
'"saqib",' \
'"farwa","farwa batool","farwabatool",' \
'"zahra","zahra saeed","zahrasaeed",' \
'"eman","eman faisal","emanfaisal",' \
'"ayesha","ayesha farooqui","ayeshafarooqui",' \
'"hassan","hassan shakil","hassanshakil",' \
'"haider","haider ali","haiderali",' \
'"munam","munam ansari","munamansari",' \
'"aima","aima shakeel","aimashakeel",' \
'"mahnoor","mahnoor fatima","mahnoorfatima",' \
'"abuzar","abuzar rizwan","abuzarrizwan",' \
'"dawood","dawood majeed","dawoodmajeed",' \
'"yousaf",' \
'"mahareb","mahareb ammar","maharebammar",' \
'"salman","salman ali","salmanali",' \
'"aliyah","aliyah rasheed","aliyahrasheed",' \
'"afras","afras shahnawaz","afrasshahnawaz",' \
'"hannan","hannan khan","hannankhan",' \
'"waniya","waniya sohail","waniyasohail",' \
'"khadija","khadija faiz","khadijafaiz",' \
'"azan","azan wasty","azanwasty",' \
'"nauman","nauman iqbal","naumaniqbal",' \
'"ghulam","ghulam murtaza","ghulammurtaza",' \
'"muhammad asjad","muhammadasjad",' \
'"ammara","ammara saleem","ammarasaleem",' \
'"ali","ali naveed","alinaveed",' \
'"sanan","sanan zahid","sananzahid",' \
'"dua","dua sarfraz","duasarfraz",' \
'"muhammad noyan","muhammadnoyan",' \
'"muhammad abdul","muhammadabdul","muhammadabdulahad", "abdulahad",' \
'"rafia","rafia mohsin","rafiamohsin",' \
'"laiba","laiba shahzad","laibashahzad",' \
'"khushbakht","khushbakht sohail","khushbakhtsohail",' \
'"kashishfatima",' \
'"saaif","saaif suleman","saaifsuleman",' \
'"romaisa","romaisa sajjad","romaisasajjad",' \
'"abdulrehman"]'

recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE,grammar)

#wav_file = wave.open(r"D:\Others\Projects\PresentBot\test_capture.wav", "rb")

audio_queue = queue.Queue()
present_count=0

def alarm():
    pass

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
                if "attendance" in text:
                    attendance_confidence+=5
                    timer1=time.time() #check if after using word attendance someone said present within 15 seconds 
                    timer2=time.time() #check for each detection of names and roll numbers
                if "present" in text:
                    present_count+=1
                    timer3=time.time() #check if word present is being said within interval of 8 seconds
                    timer2=time.time()
                    attendance_confidence+=2
                    

                if "two five" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five zero" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five one" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five two" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five three" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five four" in text:
                    attendance_confidence+=1
                    timer2=time.time()
                if "five six" in text:
                    attendance_confidence+=1
                    timer2=time.time()

                for roll in other_rolls:
                    if roll in text:
                        attendance_confidence += 1
                        timer2 = time.time()

                for name_group in other_names:
                    for name in name_group:
                        if name in text:
                            attendance_confidence += 2
                            timer2 = time.time()
                            break
                print("Text: ", text,"confidence: ",attendance_confidence, "timer 1:", time.time()-timer1,"timer 2:", time.time()-timer2,"timer 3:", time.time()-timer3)
        
        if time.time()-timer1>=45 and present_count==0:
            attendance_confidence=0

        if time.time()-timer2>=15:
            attendance_confidence=0

        if time.time()-timer3>=10:
            timer3=time.time()
            if(present_count<8):
                present_count=0
                if(attendance_confidence>5):
                    attendance_confidence-=2
            else :
                present_count-=5
                present_count=0 if present_count<0 else present_count
        
        
        if attendance_confidence > 10 and time.time()-timer4>90:
            timer4=time.time()
            print(f"attendance confirmed with {attendance_confidence} points")
            alarm()
