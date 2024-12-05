import time
import requests
import configparser
import os 

config = configparser.ConfigParser()
config.read('config.ini')

charvoice = config.getboolean('TTS', 'charvoice')
ttsoption = config['TTS']['ttsoption']
ttsclone = config['TTS']['ttsclone']
ttsurl = config['TTS']['ttsurl']
voiceonly = config.getboolean('TTS', 'voiceonly')

start_time = time.time()

def get_tts_stream(text_to_read, ttsurl, ttsclone):
    try:
        chunk_size = 1024

        if charvoice and ttsoption == "local":
            command = f'espeak-ng -s 180 -p 40 -v en-us+m3 "{text_to_read}" --stdout | aplay'
            os.system(command)

        elif charvoice and ttsoption == "xttsv2":
            full_url = f"{ttsurl}/tts_stream"
            params = {
                'text': text_to_read,
                'speaker_wav': ttsclone,
                'language': "en"
            }
            headers = {'accept': 'audio/x-wav'}

            response = requests.get(full_url, params=params, headers=headers, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=chunk_size):
                yield chunk

    except Exception as e:
        print(f"Text-to-speech generation failed: {e}")

def talking(switch, start_time, talkinghead_base_url):
    switchep = f"{switch}_talking"
    if switch == "start":
        # requests.get(f"{talkinghead_base_url}/api/talkinghead/{switchep}")
        start_time = time.time()

    if switch == "stop":
        # requests.get(f"{talkinghead_base_url}/api/talkinghead/{switchep}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Processing Time: {elapsed_time}")
