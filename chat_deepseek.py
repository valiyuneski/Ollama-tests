import requests
import json


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

#CommandLine run: ollama run qwen2.5-coder:7b
#CommandLine run: ollama serve --model deepseek-r1:8b
#CommandLine to kill ollama server: pgrep ollama | xargs kill -9
#CommandLine to open ollama models: open ~/.ollama/models

MODEL_DEEPSEEK = "deepseek-r1:8b"
MODEL_QWEN = "qwen2.5-coder:7b"

SYSTEM_PROMPT = (
            "You are a C++ expert in wxWidgets and Qt. "
            "Return a JSON with keys 'wxCode' and 'qtCode' containing clean, formatted C++ implementations only."
        )

REFERENCE_PROMPT = {
  "wx_reference": "#include <wx/wx.h>\nclass MyButtonFrame : public wxFrame{\n   public:\n    MyButtonFrame() : wxFrame(nullptr, wxID_ANY, \"Button Example\"){\n        auto sizer = new wxBoxSizer(wxHORIZONTAL);\n        auto btn = new wxButton(this, wxID_ANY, \"Click Me\");\n        btn->Bind(wxEVT_BUTTON, [=](wxCommandEvent&) {\n            wxMessageBox(\"Button Clicked!\", \"Info\", wxOK | wxICON_INFORMATION, this);\n        });\n        sizer->Add(btn, wxSizerFlags().Border().Centre());\n        SetSizerAndFit(sizer);\n        Show(true);\n    }\n};",
  "qt_reference": "#include <QPushButton>\n#include <QWidget>\n#include <QMessageBox>\nclass qtButton : public QPushButton {\n    Q_OBJECT\n    public:\n    explicit qtButton(QWidget* parent = Q_NULLPTR) : QPushButton(\"Click Me\", parent) {\n        connect(this, &QPushButton::clicked, this, [this]() {\n            QMessageBox::information(this, \"Info\", \"Button Clicked!\");\n        });\n    }\n};"
}

def systemprompt_with_reference_code():
    # Combined system prompt for both wxWidgets and Qt
    system_prompt = SYSTEM_PROMPT
    wx_reference_code = REFERENCE_PROMPT.get("wx_reference", "")
    qt_reference_code = REFERENCE_PROMPT.get("qt_reference", "")
    if wx_reference_code or qt_reference_code:
        system_prompt += "\n\nUse the following reference codes for structure, clarity, and layout:\n"
        if wx_reference_code:
            system_prompt += f"\nwxWidgets reference:\n{wx_reference_code}\n"
        if qt_reference_code:
            system_prompt += f"\nQt reference:\n{qt_reference_code}\n"
        system_prompt += (
            "\nFollow the same coding style, indentation (2 spaces), commenting "
            "style, and class structure patterns for each framework."
        )

@timecount
def chat_with_deepseek(prompt):
    """Simple client to chat with DeepSeek via Ollama"""
    
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": MODEL_QWEN,
        "messages": [
            {"role": "system", "content": systemprompt_with_reference_code()},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    return result["message"]["content"]

def get_user_prompt_as_chain_of_thought(query_text:str)->str:
    # Build user prompt as Chain Of Thought PROMPT
    user_prompt = f"""
        <user_input>
        {query_text}
        </user_input>
        <Instructions>
        And AVOID using sample class MyApp : public wxApp' or 'int main(int argc, char** argv)'.
        Provide a JSON object with 'wxCode' for wxWidgets C++ code and 'qtCode' for Qt C++ code implementations.
        Include ONLY the class that id requested from user.
        Return JSON with 'wxCode' and 'qtCode'.
        </Instructions>
    """
    return user_prompt

def main():
    # Send a message to DeepSeek
    #prompt = "Hello! Can you explain what you are in one sentence?"
    default_query_input = "Write a button class in wxWidgets and in Qt, use C++17 with lambda"
    prompt = get_user_prompt_as_chain_of_thought(default_query_input)
    print(f"User: {prompt}\n")
    
    response = chat_with_deepseek(prompt)
    print(f"DeepSeek: {response}")

if __name__ == "__main__":
    main()
