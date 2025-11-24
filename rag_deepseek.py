import requests
import json

MODEL_DEEPSEEK = "deepseek-r1:8b"
MODEL_QWEN = "qwen2.5-coder:7b"

def chat_with_deepseek_rag(prompt, context=""):
    """Simple client to chat with DeepSeek RAG via Ollama"""
    
    url = "http://localhost:11434/api/chat"
    
    # If context is provided, include it in the system message
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
    # Example RAG context (your documents/knowledge base)
    context = """
    Python is a high-level programming language created by Guido van Rossum.
    It was first released in 1991.
    Python emphasizes code readability and uses significant indentation.
    """
    
    # Ask a question
    prompt = "Who created Python and when was it released?"
    #prompt = "What time is it in New York City right now?"
    print(f"User: {prompt}\n")
    
    response = chat_with_deepseek_rag(prompt, context)
    print(f"DeepSeek: {response}")

if __name__ == "__main__":
    main()