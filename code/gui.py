import tkinter as tk
from tkinter import filedialog, ttk
import threading
from config import load_config, save_config

cfg = load_config()

SENSITIVITY_PRESETS = {
    1: {"label": "Very Strict",  "activity_limit": 8,  "present_limit": 15, "attendance_limit": 30, "confidence_threshold": 15, "word_confidence": 0.85},
    2: {"label": "Strict",       "activity_limit": 12, "present_limit": 20, "attendance_limit": 38, "confidence_threshold": 12, "word_confidence": 0.75},
    3: {"label": "Balanced",     "activity_limit": 15, "present_limit": 25, "attendance_limit": 45, "confidence_threshold": 10, "word_confidence": 0.65},
    4: {"label": "Loose",        "activity_limit": 20, "present_limit": 32, "attendance_limit": 55, "confidence_threshold": 8,  "word_confidence": 0.55},
    5: {"label": "Very Loose",   "activity_limit": 25, "present_limit": 40, "attendance_limit": 65, "confidence_threshold": 6,  "word_confidence": 0.45},
}

root = tk.Tk()
root.title("PresentBot")
root.geometry("560x640")
root.resizable(False, False)

PAD = {"padx": 20, "pady": (0, 4)}

def add_field(label, default, show=None):
    tk.Label(root, text=label, anchor="w").pack(fill="x", padx=20)
    var = tk.StringVar(value=str(default))
    tk.Entry(root, textvariable=var, width=66, show=show or "").pack(**PAD)
    return var

tk.Label(root, text="PresentBot", font=("Arial", 16, "bold")).pack(pady=(10, 6))

api_key_var = add_field("Deepgram API Key", cfg.get("api_key", ""), show="*")
name_var = add_field("Your Names (comma separated)", cfg.get("names", ""))
roll_var = add_field("Your Roll Number (digits e.g. 2594)", cfg.get("roll", ""))
sample_rolls_var = add_field("Class Roll Numbers Sample (e.g. 2500, 2506, 2512)", cfg.get("sample_rolls", ""))
sample_names_var = add_field("Classmate Names (comma separated)", cfg.get("sample_names", ""))

tk.Label(root, text="Mode", anchor="w").pack(fill="x", padx=20)
mode_var = tk.StringVar(value=cfg.get("mode", "present"))
mode_frame = tk.Frame(root)
mode_frame.pack(anchor="w", **PAD)
for label, val in [("Alarm", "alarm"), ("Say Present", "present"), ("Both", "both")]:
    tk.Radiobutton(mode_frame, text=label, variable=mode_var, value=val).pack(side="left", padx=10)

tk.Label(root, text="  (← greater true negatives chance   |   greater false positive chance →)", anchor="w").pack(fill="x", padx=20)
sens_frame = tk.Frame(root)
sens_frame.pack(fill="x", padx=20, pady=(0, 6))
sens_var   = tk.IntVar(value=cfg.get("sensitivity", 3))
sens_label = tk.Label(sens_frame, text=SENSITIVITY_PRESETS[3]["label"], width=12, anchor="w")
sens_label.pack(side="right")

def on_sensitivity(val):
    level = int(float(val))
    sens_label.config(text=SENSITIVITY_PRESETS[level]["label"])
    try:
        conf_bar["maximum"] = SENSITIVITY_PRESETS[level]["confidence_threshold"]
        conf_label.config(text=f"Confidence: 0 / {SENSITIVITY_PRESETS[level]['confidence_threshold']}")
    except NameError:
        pass

tk.Scale(sens_frame, from_=1, to=5, orient="horizontal", variable=sens_var,
         showvalue=False, command=on_sensitivity, length=380).pack(side="left")
on_sensitivity(sens_var.get())

options_row = tk.Frame(root)
options_row.pack(fill="x", padx=20, pady=(0, 6))

vb_cable_var = tk.BooleanVar(value=cfg.get("vb_cable", True))
tk.Checkbutton(options_row, text="VB-Cable (uncheck = Stereo Mix)",
               variable=vb_cable_var).pack(side="left")

tk.Label(options_row, text="  |  Model:").pack(side="left")
model_var = tk.StringVar(value=cfg.get("model", "deepgram"))
tk.Radiobutton(options_row, text="Deepgram", variable=model_var, value="deepgram").pack(side="left", padx=(6, 2))
tk.Radiobutton(options_row, text="Vosk",     variable=model_var, value="vosk").pack(side="left")

file_row = tk.Frame(root)
file_row.pack(fill="x", padx=20, pady=(0, 6))

audio_col = tk.Frame(file_row)
audio_col.pack(side="left", fill="x", expand=True)
tk.Label(audio_col, text="Present Audio (.wav)", anchor="w").pack(fill="x")
audio_inner = tk.Frame(audio_col)
audio_inner.pack(anchor="w")
audio_label = tk.Label(audio_inner, text=cfg.get("present_audio", "present.wav"), fg="gray")
audio_label.pack(side="left", padx=(0, 6))
def browse_audio():
    path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if path:
        audio_label.config(text=path)
tk.Button(audio_inner, text="Browse", command=browse_audio).pack(side="left")

vosk_col = tk.Frame(file_row)
vosk_col.pack(side="left", fill="x", expand=True, padx=(10, 0))
tk.Label(vosk_col, text="Vosk Model Folder", anchor="w").pack(fill="x")
vosk_inner = tk.Frame(vosk_col)
vosk_inner.pack(anchor="w")
vosk_label = tk.Label(vosk_inner, text=cfg.get("vosk_path", "Not selected"), fg="gray")
vosk_label.pack(side="left", padx=(0, 6))
def browse_vosk():
    path = filedialog.askdirectory(title="Select Vosk Model Folder")
    if path:
        vosk_label.config(text=path)
tk.Button(vosk_inner, text="Browse", command=browse_vosk).pack(side="left")

conf_label = tk.Label(root, text="Confidence: 0 / 10")
conf_label.pack(pady=(6, 2))
conf_bar = ttk.Progressbar(root, length=516, maximum=10)
conf_bar.pack()

def toggle_bot():
    global bot_running
    if not bot_running:
        save()
        bot_running = True
        start_btn.config(text="⏹  Stop", bg="red", fg="white")
        log("Bot started...")
        threading.Thread(target=run_bot, daemon=True).start()
    else:
        bot_running = False
        start_btn.config(text="▶  Start", bg="SystemButtonFace", fg="black")
        log("Bot stopped.")

start_btn = tk.Button(root, text="▶  Start", font=("Arial", 13, "bold"),
                       width=18, height=1, command=toggle_bot)
start_btn.pack(pady=5)

log_box = tk.Text(root, height=4, width=66, font=("Arial", 10), state="disabled")
log_box.pack(padx=20, pady=(8, 0))

bot_running = False

def log(msg, *args):
    if args:
        msg = str(msg) + " " + " ".join(str(a) for a in args)
    log_box.config(state="normal")
    log_box.insert("end", f"→ {msg}\n")
    log_box.see("end")
    log_box.config(state="disabled")

def update_confidence(value):
    max_val = SENSITIVITY_PRESETS[sens_var.get()]["confidence_threshold"]
    conf_bar["maximum"] = max_val
    conf_bar["value"] = min(value, max_val)
    conf_label.config(text=f"Confidence: {value} / {max_val}")

def save():
    preset = SENSITIVITY_PRESETS[sens_var.get()]
    save_config({
        **cfg,
        "api_key"              : api_key_var.get(),
        "names"                : name_var.get(),
        "roll"                 : roll_var.get(),
        "sample_rolls"         : sample_rolls_var.get(),
        "sample_names"         : sample_names_var.get(),
        "mode"                 : mode_var.get(),
        "model"                : model_var.get(),
        "vb_cable"             : vb_cable_var.get(),
        "present_audio"        : audio_label.cget("text"),
        "vosk_path"            : vosk_label.cget("text"),
        "sensitivity"          : sens_var.get(),
        "activity_limit"       : preset["activity_limit"],
        "present_limit"        : preset["present_limit"],
        "attendance_limit"     : preset["attendance_limit"],
        "confidence_threshold" : preset["confidence_threshold"],
        "word_confidence"      : preset["word_confidence"],
    })

def run_bot():
    global bot_running
    try:
        import importlib, bot
        importlib.reload(bot)
        bot.log_callback        = log
        bot.confidence_callback = update_confidence
        bot.stop_flag           = lambda: not bot_running
        bot.start()
    except Exception as e:
        log(f"Error: {e}")
    finally:
        bot_running = False
        start_btn.config(text="▶  Start", bg="SystemButtonFace", fg="black")




root.mainloop()