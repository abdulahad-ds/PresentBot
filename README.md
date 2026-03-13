# 🎓 PresentBot
### Automatic Attendance Detection for Google Meet

PresentBot listens to your Google Meet class audio in the background while you sleep, work on something else, or just want to step away. When your teacher starts calling attendance and your name or roll number is called, it automatically wakes you up with an alarm, says "Present" in your recorded voice, or both — based on your choice.

---

## How It Works

PresentBot captures your Google Meet audio using either VB-Cable (a virtual audio device) or Stereo Mix. It sends this audio to a speech recognition engine (Deepgram or Vosk) which converts it to text. The program then analyzes the text to detect when attendance is being called by looking for keywords like "attendance" and "present" being said repeatedly. Once it is confident that attendance has started, it listens for your name or roll number and responds automatically.

---

## Speech Recognition Options

PresentBot supports two speech recognition engines. You only need to set up one.

### Option A: Deepgram (Online) — Recommended

Deepgram works over the internet and is more accurate, especially for mixed Urdu/English classrooms. It requires a free API key.

**How to get a free Deepgram API key:**
1. Go to https://deepgram.com and click Sign Up
2. Create a free account (no credit card required)
3. Go to your dashboard and click **API Keys**
4. Click **Create a New API Key** and copy it
5. Paste it into the Deepgram API Key field in PresentBot

> The free tier includes 200 hours of audio per month which is more than enough for daily use.

---

### Option B: Vosk (Offline)

Vosk works completely offline — no internet or API key needed. It is slightly less accurate but works without any account.

**How to get the Vosk model:**

A Vosk model zip file (`vosk-model-small-en-in-0.4.zip`) is already included in the repository. Simply:
1. Extract/unzip `vosk-model-small-en-in-0.4.zip` — you will get a folder named `vosk-model-small-en-in-0.4`
2. In PresentBot, click Browse next to **Vosk Model Folder** and select the extracted folder

**Want better accuracy?** The included model is the small/fast version. For noticeably better recognition — especially with varied accents and noisy audio — download the larger Indian English model:
1. Go to https://alphacephei.com/vosk/models
2. Download **vosk-model-en-in-0.5** (larger Indian English model)
3. Extract it and select it in PresentBot the same way

> The larger model is slower but significantly more accurate. Recommended if you have a decent PC and want fewer missed detections.

---

## Installation and Setup

### Step 1: Download PresentBot

1. Go to the GitHub repository: https://github.com/yourusername/PresentBot
2. Click the green **Code** button and select **Download ZIP**, then extract it — or run:
```
git clone https://github.com/yourusername/PresentBot.git
```

---

### Step 2: Install Requirements

1. Make sure Python 3.10 or later is installed from https://python.org
2. Open the PresentBot folder
3. Double-click **setup.bat** — this installs all required Python packages automatically

---

### Step 3: Set Up VB-Cable (Recommended)

VB-Cable is a free virtual audio device that routes your Google Meet audio into PresentBot. This is the most reliable method. It also lets you mute your speakers while still having PresentBot listen to the class audio — Meet plays audio through VB-Cable, which PresentBot captures.

**How to install VB-Cable:**
1. Download VB-Cable from https://vb-audio.com/Cable
2. Extract and run `VBCABLE_Setup_x64.exe` as Administrator
3. Restart your PC after installation
4. In Google Meet settings, change the **Speaker** to **CABLE Input (VB-Audio Virtual Cable)**

> After changing the Meet speaker to CABLE Input, you will not hear the class directly through your speakers. PresentBot automatically unmutes your system volume when attendance is detected so the alarm or Present response plays audibly.

---

### Step 4: Enable Stereo Mix (Alternative to VB-Cable)

If you do not want to install VB-Cable, you can use Stereo Mix instead. This captures all system audio directly.

1. Right-click the speaker icon in your taskbar and select **Sounds**
2. Go to the **Recording** tab
3. Right-click in the empty area and enable **Show Disabled Devices**
4. Right-click **Stereo Mix** and click **Enable**
5. In PresentBot, uncheck the **VB-Cable** checkbox to use Stereo Mix

---

### Step 5: Present Audio

A `present.wav` file is already included in the repository — you can use it directly without doing anything.

If you want to use your own voice instead, record yourself clearly saying **"Present"** and replace the existing `present.wav` file with your recording (keep the same filename), or use the **Browse** button in PresentBot to select your file from anywhere on your PC.

---

### Step 6: Run PresentBot

Double-click **PresentBot.exe** to launch the app.

If the exe gives an error or does not open, run from source instead:
1. Open a terminal inside the `code` folder or use vs code
2. Run:
```
python gui.py
```

---


## Entering Your Details in PresentBot

When you open PresentBot, fill in the following fields:

| Field | What to enter |
|---|---|
| **Deepgram API Key** | Your Deepgram key (hidden). Leave blank if using Vosk. |
| **Your Names** | Variations of your name the teacher might say, comma separated. Example: `ahad, abdul ahad, muhammad abdul` |
| **Your Roll Number** | Your roll number in digits. Example: `2594`. PresentBot converts this automatically. |
| **Class Roll Numbers Sample** | A few roll numbers from your class list, comma separated. Example: `2500, 2506, 2512` |
| **Classmate Names** | First names of a few classmates, comma separated. Example: `hamza, saqib, hassan` |
| **Mode** | Alarm to wake you up, Say Present to respond automatically, or Both |
| **Sensitivity** | Controls detection strictness. Balanced is recommended to start. |
| **VB-Cable checkbox** | Check if you set up VB-Cable, uncheck for Stereo Mix |
| **Model** | Select Deepgram or Vosk |
| **Present Audio** | Click Browse to select your present.wav if not using the default |
| **Vosk Model Folder** | Only needed if using Vosk — Browse to your extracted model folder |

---

## Running PresentBot

1. Join your Google Meet class as usual
2. If using VB-Cable, make sure the Meet speaker is set to **CABLE Input**
3. Open **PresentBot.exe** and fill in your details
4. Click **Start** — PresentBot begins listening in the background
5. Minimize PresentBot — you can now sleep, do other tasks, or use your laptop quietly in the background

When your name is called, PresentBot will:
- Sound the alarm to wake you up (if Alarm or Both mode selected)
- Automatically switch to your Google Meet Chrome tab
- Unmute your microphone using Ctrl+D
- Play your present.wav recording through the microphone
- Mute your microphone again

---

## Tips for Best Results

- Before starting, make sure Google Meet is open in Chrome and your microphone is muted
- Keep your laptop plugged in so it does not go to sleep
- Disable Windows sleep/hibernate settings during class time
- If PresentBot misses attendance, try lowering the sensitivity slider
- If PresentBot triggers at wrong times, try raising the sensitivity slider
- Test the bot during a practice session before relying on it for real attendance

---

*PresentBot — built for students, by a student.*