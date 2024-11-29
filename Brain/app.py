#Define needed globals
global start_time
global char_name, char_persona, personality, world_scenario, char_greeting, example_dialogue

#needed imports
import os
import sys
import threading
import time
import json
import requests
import re
from datetime import datetime
import configparser
import sounddevice as sd
import numpy as np
import concurrent.futures

#custom imports
from module_engineTrainer import train_text_classifier
from module_btcontroller import *
from module_stt import *
from module_memory import *
from module_engine import *
from module_tts import *
from module_imagesummary import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Set the working directory to the base directory
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.append(os.getcwd())

config = configparser.ConfigParser()
config.read('config.ini')

# TTS Section
ttsurl = config['TTS']['ttsurl']
charvoice = config.getboolean('TTS', 'charvoice')
ttsoption = config['TTS']['ttsoption']
ttsclone = config['TTS']['ttsclone']
voiceonly = config.getboolean('TTS', 'voiceonly')

# TalkingHead Section
talkinghead_base_url = config['TALKINGHEAD']['talkinghead_base_url']
emotions = config.getboolean('TALKINGHEAD', 'emotions')
emotion_model = config['TALKINGHEAD']['emotion_model']
storepath = os.path.join(os.getcwd(), config['TALKINGHEAD']['storepath'])

# LLM Section
llm_backend = config['LLM']['backend']
base_url = config['LLM']['base_url']
api_key = config['LLM']['api_key']
contextsize = config.getint('LLM', 'contextsize')
max_tokens = config.getint('LLM', 'max_tokens')
temperature = config.getfloat('LLM', 'temperature')
top_p = config.getfloat('LLM', 'top_p')
seed_llm = config.getint('LLM', 'seed')
systemprompt = config['LLM']['systemprompt']
instructionprompt = config['LLM']['instructionprompt']

# CHAR Section
charactercard = config['CHAR']['charactercard']
user_name = config['CHAR']['user_name']
user_details = config['CHAR']['user_details']

# STT Section
uservoice = config.getboolean('STT', 'uservoice')

# Discord Section
TOKEN = config['DISCORD']['TOKEN']
channel_id = config['DISCORD']['channel_id']
discordenabled = config['DISCORD']['enabled'] 

# Global Variables (if needed)
global_source_image = None
global_result_image = None
global_reload = None
is_talking_override = False
is_talking = False
global_timer_paused = False
module_engine = None
start_time = time.time() #calc time
stop_event = threading.Event()
executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)

#TTS
def play_audio_stream(tts_stream, samplerate=22050, channels=1):
    """
    Play the audio stream through speakers using SoundDevice.
    """
    try:
        with sd.OutputStream(samplerate=samplerate, channels=channels, dtype='int16') as stream:
            for chunk in tts_stream:
                if chunk:
                    # Convert bytes to int16 using numpy
                    audio_data = np.frombuffer(chunk, dtype='int16')
                    stream.write(audio_data)
                else:
                    print("Received empty chunk.")        
            
            #print("Audio playback finished. Starting transcription...")
            transcribe_command()  # go back to listening for voice (non wake word)
    except Exception as e:
        print(f"Error during audio playback: {e}")

#LLM
def build_prompt(user_prompt):
    global char_name, char_persona, personality, world_scenario, char_greeting, example_dialogue, voiceonly, systemprompt, instructionprompt
    now = datetime.now()
    date = now.strftime("%m/%d/%Y")
    time = now.strftime("%H:%M:%S")

    #VOICEMODE SHIT
    if "voice only mode on" in user_prompt:
        voiceonly = True

    if "voice only mode off" in user_prompt:
        voiceonly = False

 
    module_engine = check_for_module(user_prompt, char_name, talkinghead_base_url)
    
    if module_engine != "No_Tool":
        #if "*User is leaving the chat politely*" in module_engine:
            #stop_idle() #StopAFK mssages

        if "Sends a picture***" in module_engine:
            global latest_text_to_read
            sdpicture = module_engine.split('***', 1)[-1]
            #module_engine = f"*Sends a picture*. You will inform user that this is the image as requested, do not describe the image."
            
            pattern = r'data:image\/[a-zA-Z]+;base64,([^"]+)'
            match = re.search(pattern, sdpicture)
            if match:
                base64_data = match.group(1)
                module_engine = f"*Sends a picture of: {get_image_caption_from_base64(base64_data)}*"
            else:
                module_engine = f"*Cannot send a picture something went wrong, inform user*"

            #socketio.emit('bot_message', {'message': sdpicture})
       
            #dont save tool info to memory
            #threading.Thread(target=longMEM_tool, args=(module_engine,)).start()  

    #PROMPT SHIT
    charactercard = f"\nPersona: {char_persona}\n\nWorld Scenario: {world_scenario}\n\nDialog:\n{example_dialogue}\n"
    dtg = f"Current Date: {date}\nCurrent Time: {time}\n"
    past = longtermMEMPast(user_prompt)

    # Correct the order and logic of replacements clean up memories and past json crap
    past = past.replace("\\\\", "\\")  # Reduce double backslashes to single
    past = past.replace("\\n", "\n")   # Replace escaped newline characters with actual newlines
    past = past.replace("\\'", "'")    # Replace escaped single quotes with actual single quotes
    past = past.replace("\'", "'")    # Replace escaped single quotes with actual single quotes

    history = ""
    userInput = user_prompt  # Simulating user input to avoid hanging


    if module_engine != "No_Tool":
        module_engine = module_engine + "\n"
    else:
        module_engine = ""

    promptsize = (
        f"System: {systemprompt}\n\n"
        f"### Instruction: {instructionprompt}\n"
        f"{dtg}\n"
        f"User is: {user_details}\n\n"
        f"{charactercard}\n"
        f"Past Memories which may be helpfull to answer {char_name}: {past}\n\n"
        f"{history}\n"
        #f"{module_engine}"
        f"Respond to {user_name}'s message of: {userInput}\n"
        f"{module_engine}"
        f"### Response: {char_name}: "
    )

    #Calc how much space is avail for chat history
    remaining = token_count(promptsize).get('length', 0)
    memallocation = int(contextsize - remaining)
    history = remember_shortterm_tokenlim(memallocation)

    prompt = (
        f"System: {systemprompt}\n\n"
        f"### Instruction: {instructionprompt}\n"
        f"{dtg}\n"
        f"User is: {user_details}\n\n"
        f"{charactercard}\n"
        f"Past Memories which may be helpfull to answer {char_name}: {past}\n\n"
        f"{history}\n"
        f"Respond to {user_name}'s message of: {userInput}\n"
        f"{module_engine}"
        f"### Response: {char_name}: "
    )

    prompt = prompt.replace("{user}", user_name) 
    prompt = prompt.replace("{char}", char_name)
    prompt = prompt.replace("\\\\", "\\") 
    prompt = prompt.replace("\\n", "\n") 
    prompt = prompt.replace("\\'", "'")    
    prompt = prompt.replace("\'", "'")    
    prompt = prompt.replace('\\"', '"')
    prompt = prompt.replace('\"', '"')
    prompt = prompt.replace('<END>', '') 

    #print(prompt)
    return prompt

def get_completion(prompt, istext):
    global char_name, char_persona, personality, world_scenario, char_greeting, example_dialogue
       
    if istext == "True":
        prompt = build_prompt(prompt)

    url = f"{base_url}/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "seed": seed_llm
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if istext == "False":
        text_to_read = extract_text(response.json(), True)
    else:
        text_to_read = extract_text(response.json(), False)

    text_to_read = text_to_read.replace('<END>', '') #without this if may continue on forever (max token)
    return(text_to_read)

def extract_text(json_response, picture):
    global char_name
    
    if picture == False:
        try:
            cleaned_text = re.sub(r"\s{2,}", " ", json_response['choices'][0]['text'].strip())  # Collapse multiple spaces.
            cleaned_text = re.sub(r"<\|.*?\|>", "", cleaned_text, flags=re.DOTALL)  # Remove <| and |> tags.
            cleaned_text = re.sub(rf"{re.escape(char_name)}:\s*", "", cleaned_text)  # Remove lines with character's name followed by a colon.
            cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text).strip()  # Remove empty lines.
            return cleaned_text
        except (KeyError, IndexError, TypeError) as error:
            return f"Text content could not be found. Error: {str(error)}"
    else:
        try:
            cleaned_text = re.sub(r"\s{2,}", " ", json_response['choices'][0]['text'].strip())  # Collapse multiple spaces.
            cleaned_text = re.sub(r"<\|.*?\|>", "", cleaned_text, flags=re.DOTALL)  # Remove <| and |> tags.
            return cleaned_text
        except (KeyError, IndexError, TypeError) as error:
            return f"Text content could not be found. Error: {str(error)}"

def stop_generation():
    global base_url, api_key
    url = f"{base_url}/v1/internal/stop-generation"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
    print("Stop generation request successful.")

def token_count(text):
    if llm_backend == "ooba":
        url = f"{base_url}/v1/internal/token-count"

    if llm_backend == "tabby":
        url = f"{base_url}/v1/token/encode"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "text": text
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

def chat_completions_with_character(messages, mode, character):
    url = f"{base_url}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": messages,
        "mode": mode,
        "character": character
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def process_completion(text):
    # Use the executor directly without 'with' statement
    future = executor.submit(get_completion, text, "True")
    botres = future.result()
    reply = llm_process(text, botres)
    return reply

def extract_after_target(character_response, target_strings):
    """
    Extracts text after the first occurrence of any target string in the list items.
    
    :param character_response: List of dictionaries with text content.
    :param target_strings: List of target strings to search for.
    :return: Extracted text after the first found target string, with the last two characters removed, or None if not found.
    """
    for target_string in target_strings:
        for item in character_response:
            text_content = item.get('text', '')
            position = text_content.find(target_string)
            if position != -1:
                # Extract everything after the target string and remove the last two characters
                extrtext = text_content[position + len(target_string):-1]
                finalextrtext = extrtext[1:-1] if extrtext.startswith('"') and extrtext.endswith('"') else extrtext.strip('"')
                return finalextrtext
    return None

#TTS
def handle_stt_message(message):
    """
    Process the recognized message from module_stt and stream audio response to speakers.
    """
    try:
        # Parse the user message
        message_dict = json.loads(message)
        if not message_dict.get('text'):  # Handles cases where text is "" or missing
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TARS: Going Idle...")
            return
        
        #Print the response
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] USER: {message_dict['text']}")

        # Check for shutdown command
        if "shutdown pc" in message_dict['text'].lower():
            print("Shutting down the PC...")
            os.system('shutdown /s /t 0')
            return  # Exit function after issuing shutdown command
        
        # Process the message using process_completion
        global start_time, latest_text_to_read
        start_time = time.time()  # Record the start time for tracking
        reply = process_completion(message_dict['text'])  # Process the message
        latest_text_to_read = reply  # Store the reply for later use
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TARS: {reply}")

        # Stream TTS audio to speakers
        #print("Fetching TTS audio...")
        tts_stream = get_tts_stream(reply, ttsurl, ttsclone)  # Send reply text to TTS
        
        # Play the audio stream
        #print("Playing TTS audio...")
        play_audio_stream(tts_stream)

    except json.JSONDecodeError:
        print("Invalid JSON format. Could not process user message.")
    except Exception as e:
        print(f"Error processing message: {e}")

def wake_word_tts(data):
    tts_stream = get_tts_stream(data, ttsurl, ttsclone)
    play_audio_stream(tts_stream)

#THREADS
def start_stt_thread():
    """
    Wrapper to start the STT functionality in a thread.
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Starting STT thread...")
        while not stop_event.is_set():
            start_stt()
    except Exception as e:
        print(f"Error in STT thread: {e}")

def start_bt_controller_thread():
    """
    Wrapper to start the BT Controller functionality in a thread.
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Starting BT Controller thread...")
        while not stop_event.is_set():
            start_controls()
    except Exception as e:
        print(f"Error in BT Controller thread: {e}")

def llm_process(userinput, botresponse):
    threading.Thread(target=longMEM_thread, args=(userinput, botresponse)).start()
    
    if emotions == True: #set emotion
        threading.Thread(target=set_emotion, args=(botresponse,)).start()

    return botresponse

#MISC
def set_emotion(text_to_read):
    from transformers import pipeline
    
    sizecheck = token_count(text_to_read)
    if 'length' in sizecheck:
        value_to_convert = sizecheck['length']
    
    if isinstance(value_to_convert, (int, float)):
        if value_to_convert <= 511:
            classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
            model_outputs = classifier(text_to_read)
            emotion = max(model_outputs[0], key=lambda x: x['score'])['label']
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Emotion {emotion}")
      
        #else:
            #print("Not Setting Emotion")

def read_character_content(charactercard):
    global char_name, char_persona, personality, world_scenario, char_greeting, example_dialogue

    try:
        with open(charactercard, "r") as file:
            data = json.load(file)

            now = datetime.now()
            date = now.strftime("%m/%d/%Y")
            time = now.strftime("%H:%M:%S")
            dtg = f"Current Date: {date}\nCurrent Time: {time}\n"
            dtg2 = f"{date} at {time}\n"

            placeholders = {
                "{{user}}": user_name,
                "{{char}}": char_name,
                "{{time}}": dtg2
            }

            # Replace placeholders in strings within the dictionary
            for key, value in data.items():
                if isinstance(value, str):
                    for placeholder, replacement in placeholders.items():
                        data[key] = value.replace(placeholder, replacement)


            char_name = data.get("char_name", char_name) or data.get("name", "")
            char_persona = data.get("char_persona", char_persona) or data.get("description", "")
            personality = data.get("personality", personality)
            world_scenario = data.get("world_scenario", world_scenario) or data.get("scenario", "")
            char_greeting = data.get("char_greeting", char_greeting) or data.get("first_mes", "")
            example_dialogue = data.get("example_dialogue", example_dialogue) or data.get("mes_example", "")

    except FileNotFoundError:
        print(f"Character file '{charactercard}' not found.")
    except Exception as e:
        print(f"Error: {e}")

def initial_msg():
    global char_greeting

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DEBUG: initial_msg() called")
    

    read_character_content(charactercard)
    train_text_classifier()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Script running from: {BASE_DIR}")

    #Load Char card
    

    #Try to set inital settings for TTS Cloning
    try:
        url = f"{ttsurl}/set_tts_settings"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            "stream_chunk_size": 100,
            "temperature": 0.65,
            "speed": 1.4,
            "length_penalty": 1,
            "repetition_penalty": 2,
            "top_p": 0.65,
            "top_k": 50,
            "enable_text_splitting": True
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: TTS Settings updated successfully.")
        else:
            print(f'Failed to update settings. Status code: {response.status_code}')
            print('Response:', response.text)
    except Exception as e:
        print(f"Error: {e}")

#Trigger once
initial_msg()

#MAIN
if __name__ == "__main__":
    # Set the STT message callback
    set_message_callback(handle_stt_message)
    set_wakewordtts_callback(wake_word_tts)

    # Start threads
    stt_thread = threading.Thread(target=start_stt_thread, name="STTThread", daemon=True)
    bt_controller_thread = threading.Thread(target=start_bt_controller_thread, name="BTControllerThread", daemon=True)

    stt_thread.start()
    bt_controller_thread.start()

    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Main program running. Press Ctrl+C to stop.")
        while True:
            pass  # Keep the main program running
    except KeyboardInterrupt:
        print("\nStopping all threads and shutting down executor...")
        stop_event.set()  # Signal threads to stop

        # Shut down the executor
        executor.shutdown(wait=True)

        # Join threads
        stt_thread.join()
        bt_controller_thread.join()
        print("All threads and executor stopped gracefully.")