def load_config():
    """
    Load configuration settings from 'config.ini' and return them as a dictionary.
    """
    import os
    import sys
    import configparser

    # Set the working directory and adjust the system path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    sys.path.append(os.getcwd())

    # Parse the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Extract and return configuration variables
    return {
        "base_dir": base_dir,
        "ttsurl": config['TTS']['ttsurl'],
        "charvoice": config.getboolean('TTS', 'charvoice'),
        "ttsoption": config['TTS']['ttsoption'],
        "ttsclone": config['TTS']['ttsclone'],
        "voiceonly": config.getboolean('TTS', 'voiceonly'),
        "emotions": config.getboolean('EMOTION', 'enabled'),
        "emotion_model": config['EMOTION']['emotion_model'],
        "storepath": os.path.join(os.getcwd(), config['EMOTION']['storepath']),
        "llm_backend": config['LLM']['backend'],
        "base_url": config['LLM']['base_url'],
        "api_key": config['LLM']['api_key'],
        "contextsize": config.getint('LLM', 'contextsize'),
        "max_tokens": config.getint('LLM', 'max_tokens'),
        "temperature": config.getfloat('LLM', 'temperature'),
        "top_p": config.getfloat('LLM', 'top_p'),
        "seed_llm": config.getint('LLM', 'seed'),
        "systemprompt": config['LLM']['systemprompt'],
        "instructionprompt": config['LLM']['instructionprompt'],
        "charactercard": config['CHAR']['charactercard'],
        "user_name": config['CHAR']['user_name'],
        "user_details": config['CHAR']['user_details'],
        "TOKEN": config['DISCORD']['TOKEN'],
        "channel_id": config['DISCORD']['channel_id'],
        "discordenabled": config['DISCORD']['enabled'],
    }
