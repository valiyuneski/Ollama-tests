import requests
import json

from pathlib import Path

# Load history files as plain text so we can join them into the system context
WX_HISTORY_FILE = Path(__file__).parent / "wx_history.txt"
QT_HISTORY_FILE = Path(__file__).parent / "qt_history.txt"

def _load_history(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

MODEL_DEEPSEEK = "deepseek-r1:8b"
MODEL_QWEN = "qwen2.5-coder:7b"

SYSTEM_PROMPT = (
            "You are a C++ expert in wxWidgets and Qt. "
            "Return a JSON with keys 'wxCode' and 'qtCode' containing clean, formatted C++ implementations only."
        )

import time
from functools import wraps
from typing import Any, Tuple

def timecount(func):
    """Decorator to measure execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        diff = end - start
        print(f"[TIME] {func.__name__} executed in {diff:.6f} seconds")
        return result, diff
    return wrapper

@timecount
def chat_with_ollama_rag(prompt):
    """Simple client to chat with DeepSeek RAG via Ollama"""
    
    url = "http://localhost:11434/api/chat"
    
    # If context is provided, include it in the system message
    context = "\n\n".join([_load_history(WX_HISTORY_FILE), _load_history(QT_HISTORY_FILE)])
    messages = []
    if context:
        messages.append({
            "role": "system", 
            "content": f"Use the following context to answer questions:\n\n{context}"
        })
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL_QWEN,
        "messages": messages,
        "stream": False
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    return result["message"]["content"]

def main():
    # Ask a question
    prompt = "Write a button class in wxWidgets and in Qt, use C++17 with lambda"
    print(f"User: {prompt}\n")
    
    response = chat_with_ollama_rag(prompt)
    print(f"Ollama: {response}")

if __name__ == "__main__":
    main()