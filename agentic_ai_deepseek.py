import requests
import json
from datetime import datetime

MODEL_DEEPSEEK = "deepseek-r1:8b"
MODEL_QWEN = "qwen2.5-coder:7b"

# Define available tools
TOOLS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "parameters": {}
    },
    {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {
            "expression": "string - mathematical expression to evaluate (e.g., '2 + 2')"
        }
    },
    {
        "name": "search_web",
        "description": "Search for information on the web",
        "parameters": {
            "query": "string - search query"
        }
    }
]

# Tool implementations
def get_current_time():
    """Returns current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression):
    """Safely evaluates a mathematical expression"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def search_web(query):
    """Simulated web search (replace with actual API)"""
    return f"Simulated search results for: {query}"

# Tool registry
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_web": search_web
}

def call_ollama(messages):
    """Call Ollama API"""
    url = "http://localhost:11434/api/chat"
    data = {
        "model": MODEL_QWEN,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["message"]["content"]

def parse_tool_call(response):
    """Parse tool call from LLM response"""
    # Simple parsing - looks for tool call patterns
    if "TOOL_CALL:" in response:
        lines = response.split("\n")
        for line in lines:
            if line.startswith("TOOL_CALL:"):
                parts = line.replace("TOOL_CALL:", "").strip().split("(", 1)
                tool_name = parts[0].strip()
                args = {}
                if len(parts) > 1:
                    args_str = parts[1].rstrip(")")
                    if args_str:
                        # Parse simple key=value arguments
                        for arg in args_str.split(","):
                            if "=" in arg:
                                key, val = arg.split("=", 1)
                                args[key.strip()] = val.strip().strip('"').strip("'")
                return tool_name, args
    return None, None

def agent_loop(user_input, max_iterations=5):
    """Main agentic loop"""
    
    # Create system message with tool descriptions
    tools_desc = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in TOOLS
    ])
    
    system_message = f"""You are an AI agent with access to tools. When you need to use a tool, respond with:
TOOL_CALL: tool_name(arg1=value1, arg2=value2)

Available tools:
{tools_desc}

Think step by step and use tools when needed. After using a tool, you'll receive the result and can continue reasoning."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]
    
    print(f"User: {user_input}\n")
    
    for iteration in range(max_iterations):
        # Get LLM response
        response = call_ollama(messages)
        print(f"Agent (iteration {iteration + 1}): {response}\n")
        
        # Check if tool call is needed
        tool_name, args = parse_tool_call(response)
        
        if tool_name and tool_name in TOOL_FUNCTIONS:
            # Execute tool
            print(f"🔧 Executing tool: {tool_name}({args})")
            tool_result = TOOL_FUNCTIONS[tool_name](**args)
            print(f"📊 Tool result: {tool_result}\n")
            
            # Add tool result to conversation
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user", 
                "content": f"Tool result from {tool_name}: {tool_result}"
            })
        else:
            # No tool call, agent is done
            return response
    
    return "Max iterations reached"

def main():
    # Example queries
    queries = [
        "What time is it right now?",
        "Calculate 123 * 456",
        "What is 50 + 25, and then multiply that by 2?"
    ]
    
    # Run agent with first query
    agent_loop(queries[0])

if __name__ == "__main__":
    main()