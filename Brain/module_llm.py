import httpx
from src.config import load_config

config = load_config()

async def process_completion(prompt: str) -> str:
    url = f"{config['LLM']['base_url']}/v1/completions"
    headers = {"Authorization": f"Bearer {config['LLM']['api_key']}"}
    payload = {
        "prompt": prompt,
        "max_tokens": config['LLM'].getint('max_tokens'),
        "temperature": config['LLM'].getfloat('temperature'),
        "top_p": config['LLM'].getfloat('top_p'),
        "seed": config['LLM'].getint('seed'),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response_data = response.json()
    return extract_text(response_data)

def extract_text(response_data) -> str:
    try:
        return response_data["choices"][0]["text"].strip()
    except KeyError:
        return "Error: Could not process response."
