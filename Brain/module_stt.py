import os
import random
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pocketsphinx import LiveSpeech
from threading import Event
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.append(os.getcwd())

# List of TARS-style responses
tars_responses = [
    "Yes? What do you need?",
    "Ready and listening.",
    "At your service.",
    "Go ahead.",
    "What can I do for you?",
    "Listening. What's up?",
    "Here. What do you require?",
    "Yes? I'm here.",
    "Standing by.",
    "Online and awaiting your command."
]

# Constants
WAKE_PHRASE = "hey tar"
SAMPLE_RATE = 16000
DEBUG = False

# Debugging utility
def debug_print(message):
    if DEBUG:
        print(message)

# Initialize Vosk model for command transcription
VOSK_MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-en-us-0.15")
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError("Vosk model not found. Download from: https://alphacephei.com/vosk/models")
vosk_model = Model(VOSK_MODEL_PATH)

# Global running flag and callback
running = False
message_callback = None  # Callback to handle recognized messages
wakeword_callback = None  # Global variable to hold the reference


def detect_wake_word():
    """
    Continuously listens for the wake word using Pocketsphinx.
    """
  
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TARS: Idle...")
    

    speech = LiveSpeech(lm=False, keyphrase=WAKE_PHRASE, kws_threshold=1e-20)
    for phrase in speech:
        debug_print(f"Detected phrase: {phrase.hypothesis()}")
        if WAKE_PHRASE in phrase.hypothesis().lower():
            # Select a random response
            response = random.choice(tars_responses)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TARS: {response}")
            trigger_wakeword_function(response)
            return True

def set_wakewordtts_callback(callback_function):
    global wakeword_callback
    wakeword_callback = callback_function

def trigger_wakeword_function(response):
    if wakeword_callback:
        wakeword_callback(response)
    else:
        print("App callback is not set.")

def transcribe_command():
    """
    Listens for a command after the wake word is detected and transcribes it using Vosk.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TARS: Listening...")

    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        while True:
            try:
                data, _ = stream.read(4000)  # Read audio data
                data_bytes = data.tobytes()  # Convert to raw bytes
                if recognizer.AcceptWaveform(data_bytes):
                    result = recognizer.Result()
                    #print("Command recognized:", result)
                    
                    # Use the callback to send the result to the app

                    if result == "":
                        break

                    if message_callback:
                        message_callback(result)
                    else:
                        print("No callback defined to handle the message.")
                    break
            except Exception as e:
                print(f"Error processing audio stream: {e}")
                break

def start_stt(stop_event: Event = None):
    """
    Start the voice assistant. Listens for wake word and transcribes commands.
    """
    global running
    running = True

    try:
        while running:
            if stop_event and stop_event.is_set():  # Check for stop signal
                print("Stopping STT...")
                break

            if detect_wake_word():
                transcribe_command()
    except KeyboardInterrupt:
        print("\nSTT interrupted by user.")
    except Exception as e:
        print(f"Error in STT: {e}")
    finally:
        print("STT stopped.")

def stop_stt():
    """
    Stop the voice assistant.
    """
    global running
    running = False
    print("Voice assistant stopped.")

def set_message_callback(callback):
    """
    Set the callback function to handle recognized messages.
    """
    global message_callback
    #print("Setting message callback for STT.")
    message_callback = callback
