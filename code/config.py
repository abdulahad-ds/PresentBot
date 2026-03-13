import json, os
import num2words
import sys, os

if hasattr(sys, '_MEIPASS'):
    CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), "config.json")
else:
    CONFIG_FILE = "config.json"


DEFAULT_CONFIG = {
    "api_key"          : "",
    "names"            : "ahad, abdul ahad, muhammad abdul",
    "roll"             : 2594,
    "mode"             : "alarm",        # alarm / present / both
    "device_index"     : None,
    "present_audio"    : "present.wav",
    "chunk_duration"   : 3,
    "activity_limit"   : 15,
    "present_limit"    : 25, 
    "attendance_limit" : 45,
    "confidence_threshold" : 10,
    "browser"          : "chrome",
    "model"       : "deepgram",   # "deepgram" or "vosk"
    "vosk_path"   : "",           # path to vosk model folder
    "vb_cable"    : True,         # True = VB-Cable, False = Stereo Mix
    "sample_names"  : "",
    "sample_rolls"  : ""       #2500, 2502, 2506, 2512, 2520
    
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        for key, val in DEFAULT_CONFIG.items():
            if key not in data:
                data[key] = val
    else:
        data = DEFAULT_CONFIG.copy()


    if data["sample_rolls"]:
        data["other_rolls"] = generate_roll_keywords(data["sample_rolls"])
    else:
        data["other_rolls"] = []

    data["classmate_names"] = [n.strip().lower() for n in data["sample_names"].split(",") if n.strip()]

    data["roll_list"] = generate_user_roll(str(data["roll"]))

    return data


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_user_roll(roll_str):
    digits = roll_str.strip()
    if not digits:
        return []
    digit_by_digit = " ".join([num2words.num2words(int(d)) for d in digits])
    first_last     = num2words.num2words(int(digits[:2])).replace("-", " ") + " " + num2words.num2words(int(digits[-2:])).replace("-", " ")
    return list({digit_by_digit, first_last})

def generate_roll_keywords(sample_rolls_str):
    keywords = set()

    rolls = [r.strip() for r in sample_rolls_str.split(",") if r.strip()]

    for roll_str in rolls:
        digits = roll_str.strip()

        first2_text = num2words.num2words(int(digits[:2])).replace("-", " ").strip()
        last2_text = num2words.num2words(int(digits[-2:])).replace("-", " ").strip()
        all_digits_text = " ".join([num2words.num2words(int(d)).replace("-", " ").strip() for d in digits])
        first_last_text = first2_text + " " + last2_text

        keywords.add(first2_text)      
        keywords.add(last2_text)         
        keywords.add(all_digits_text)    
        keywords.add(first_last_text)   

    return list(keywords)

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
'"ninety","ninety one","ninety two","ninety three","ninety four","ninety five","ninety six","ninety seven","ninety eight","ninety nine","one hundred" , "thousand" ]'