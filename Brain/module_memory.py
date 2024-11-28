import os
from transformers import pipeline
import json
from typing import List
from datetime import datetime
import re
from hyperdb import *
from memory.hyperdb import *
from app import token_count
import json

global hyper_db
global memory_db_path
longMEM_Use = True

#MEMORY FUNCTIONS
def remember(query):
    global hyper_db

    # Get a dictionary representation of the memories
    lst = hyper_db.dict()

    # Get the highest likelihood memory
    results = hyper_db.query(query, top_k=1, return_similarities=False)

    if results:
        # Get the highest likelihood memory
        memory = results[0]

        # Find the index of the highest likelihood memory in the list
        start_index = next((i for i, d in enumerate(lst) if d['document'] == memory), None)

        if start_index is not None:
            prev_count = 1
            post_count = 1

            # Calculate the start and end indices for retrieving context memories
            start = max(start_index - prev_count, 0)
            end = min(start_index + post_count + 1, len(lst))

            # Retrieve the context memories
            result = [lst[i]['document'] for i in range(start, end)]

            return result
        else:
            return f"Something went wrong. Could not find memory in the memory database. {memory}"
    else:
        return "No memories found for the given query."
            
def remember_shortterm(int) -> List[str]:
    global hyper_db
    MAX_ENTRIES = int
    memory_dict = hyper_db.dict()
    last_entries = memory_dict[-MAX_ENTRIES:]
    result = [entry['document'] for entry in last_entries]
    return result

def longtermMEMPast(user_input):
    global hyper_db
    try:
        if longMEM_Use:
            past = f'{remember(user_input)}'
        else:
            past = 'None'
        return(past)
    
    except Exception as e:
        print(f'Error: {e}')

def longMEM_thread(userinput, bot_response):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = {
        "timestamp": current_time,
        "user_input": userinput,
        "bot_response": bot_response
    }
    hyper_db.add_document(document)
    hyper_db.save(memory_db_path)

def remember_shortterm_tokenlim(short_term_tokens) -> str:
    memory_dict = hyper_db.dict()

    accumulated_documents = []  # Accumulate (user_input, bot_response) tuples
    accumulated_length = 0

    # Process entries in reverse to start with the most recent
    for entry in reversed(memory_dict):
        user_input = entry['document'].get('user_input', "")
        bot_response = entry['document'].get('bot_response', "")

        # Skip if user_input or bot_response is empty
        if not user_input or not bot_response:
            continue
        
        # Prepare text for token counting
        text_str = f"user_input: {user_input}\nbot_response: {bot_response}"
        text_length = token_count(text_str)['length']

        # Check if adding this entry would exceed the token limit
        if accumulated_length + text_length > short_term_tokens:
            # If so, since we are iterating in reverse, stop adding newer entries
            continue
        
        # Accumulate entry if it doesn't exceed the token limit
        accumulated_documents.append((user_input, bot_response))
        accumulated_length += text_length

    # Since we processed entries in reverse, reverse the accumulated list to maintain the original order in output
    #formatted_output = '\n'.join([f"user_input: {ui}\nbot_response: {br}" for ui, br in reversed(accumulated_documents)])
    formatted_output = '\n'.join([f"{{user}}: {ui}\n{{char}}: {br}" for ui, br in reversed(accumulated_documents)])




    return formatted_output

def longMEM_tool(toolused):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    document = {
        "timestamp": current_time,
        "bot_response": toolused
    }
    hyper_db.add_document(document)
    hyper_db.save(memory_db_path)

def load_and_inject_memories(json_file_path):
  

    #check if json_file_path exists or it breaks
    if os.path.exists(json_file_path):
        print("Injecting Memories.")

        # Load memories from the JSON file
        with open(json_file_path, 'r') as file:
            memories = json.load(file)

        # Inject memories into the database
        for memory in memories:
            time = memory.get("time", "")
            userinput = memory.get("userinput", "")
            botresponse = memory.get("botresponse", "")

            # Check if "time" is not provided in the JSON and generate the current time
            if not time:
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check if "botresponse" is not provided in the JSON
            if not botresponse:
                botresponse = ""  # Or provide a default value if needed

            # Call the function to add the memory to the database
            longMEM_thread(userinput, botresponse)

        # Rename the JSON file with the ".loaded" extension
        new_file_path = os.path.splitext(json_file_path)[0] + ".loaded"
        os.rename(json_file_path, new_file_path)
        print(f"Memory Loaded: {new_file_path}")

def load_longMem(memory_db_path):
    global hyper_db, char_name
    hyper_db = HyperDB()
    
    print('Initializing memory...')
    if os.path.exists(memory_db_path):
        print(f'Found existing memory db, loading: {memory_db_path}')
        loaded_successfully = hyper_db.load(memory_db_path)

        if loaded_successfully and hyper_db.vectors is not None:
            print('Memory loaded successfully')
            #print(f'Documents: {hyper_db.documents}')
            #print(f'Vectors shape: {hyper_db.vectors.shape}')
        else:
            print('Memory loading failed or empty')
            hyper_db.vectors = np.empty((0, 0), dtype=np.float32)  # Initialize vectors to an empty array

    else:
        print(f'No memory db path specified, could not find any existing memory db, creating new one: {memory_db_path}')
        hyper_db.add_document({"text": f'{char_name}: {char_greeting}'})  # Use add_document instead of memorize
        hyper_db.save(memory_db_path)
    return

def summarize_text(article, max_len=250, min_len=0, do_sample=False):
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    summary = summarizer(article, max_length=max_len, min_length=min_len, do_sample=do_sample)
    return summary
    #prompt = shortMEM + "\n" + "\n" + str(last_six_lines) + str(new_line) + f'\n{{"role": "TARS.", "date": "{date}", "time": "{time}", "content": "'
    #prompt = str(prompt)

def read_character_content(charactercard):
    global char_name, char_persona, personality, world_scenario, char_greeting, example_dialogue

    try:
        with open(charactercard, "r") as file:
            content = file.read()

            char_name_match = re.search(r'("char_name"|"name"):\s*"([^"]*)"', content)
            char_name = char_name_match.group(2) if char_name_match else ''

            char_persona_match = re.search(r'("char_persona"|"description"):\s*"([^"]*)"', content)
            char_persona = char_persona_match.group(2) if char_persona_match else ''

            personality_match = re.search(r'"personality":\s*"([^"]*)"', content)
            personality = personality_match.group(1) if personality_match else ''

            world_scenario_match = re.search(r'("world_scenario"|"scenario"):\s*"([^"]*)"', content)
            world_scenario = world_scenario_match.group(2) if world_scenario_match else ''

            char_greeting_match = re.search(r'("char_greeting"|"first_mes"):\s*"([^"]*)"', content)
            char_greeting = char_greeting_match.group(2) if char_greeting_match else ''

            example_dialogue_match = re.search(r'("example_dialogue"|"mes_example"):\s*"([^"]*)"', content)
            example_dialogue = example_dialogue_match.group(2) if example_dialogue_match else ''

            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini')
            # Populate the global variables
            global user_name
            user_name = config['CHAR']['user_name']

            char_greeting = char_greeting.replace("{{user}}", user_name)
            char_greeting = char_greeting.replace("{{char}}", char_name)
            char_greeting = char_greeting.replace("{{time}}", datetime.now().strftime("%Y-%m-%d %H:%M"))

            #print("Character Variables:")
            print(f"Loading the character {char_name} ... DONE!!!")
            #print(f"char_persona: {char_persona}")
            #print(f"personality: {personality}")
            #print(f"world_scenario: {world_scenario}")
            #print(f"char_greeting: {char_greeting}")
            #print(f"example_dialogue: {example_dialogue}")

    except FileNotFoundError:
        print(f"Character file '{charactercard}' not found.")
    except Exception as e:
        print(f"Error: {e}")

read_character_content("character/TARS.json")     
#LOAD
memory_db_path = os.path.abspath("memory/TARS.pickle.gz")
load_longMem(memory_db_path)

#inject any memories needed
load_memories = os.path.abspath("memory/load_memories.json")
load_and_inject_memories(load_memories)