import os

llm_config = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": os.environ['OPENAI_API_KEY'],
        },
        {
            "model": "dolphin-mistral:latest",  # Ollama model with 30k context
            "base_url": "http://localhost:11434",
            "api_key": "NotRequired",
            "price": [0, 0],
        },
        {
            "model": "llama3.1:8b",  # Fallback Ollama model
            "base_url": "http://localhost:11434",
            "api_key": "NotRequired",
            "price": [0, 0],
        }
    ],
    "cache_seed": None,
}