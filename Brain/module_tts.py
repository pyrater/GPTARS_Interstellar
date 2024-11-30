import pyttsx3
import time
import requests
import configparser
from io import BytesIO
import tempfile

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
            # Initialize the text-to-speech engine
            engine = pyttsx3.init()
            # Set the desired properties for the TTS voice
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)  # Choose the desired voice
            engine.setProperty('rate', 200)  # Adjust the speaking rate
            engine.setProperty('volume', 1.0)  # Adjust the volume

            # Create a temporary file for TTS output
            with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
                temp_filename = temp_audio.name
                engine.save_to_file(text_to_read, temp_filename)
                engine.runAndWait()

                # Read the temporary file into a BytesIO buffer
                with open(temp_filename, 'rb') as audio_file:
                    audio_buffer = BytesIO(audio_file.read())

                # Rewind the buffer and yield chunks
                audio_buffer.seek(0)
                while True:
                    chunk = audio_buffer.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

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
