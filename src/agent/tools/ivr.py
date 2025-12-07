import aiohttp
import asyncio
from typing import Optional

async def press_digit(params):
    """
    Presses digit(s) on the phone keypad.
    
    Args:
        params: FunctionCallParams containing arguments.
    """
    digits = params.arguments.get("digits")
    # Backwards compatibility if model predicts 'digit'
    if not digits:
        digits = params.arguments.get("digit")
        
    print(f"DEBUG: Agent triggering press_digit(digits={digits})")
    
    if not digits:
        return "No digits specified."

    results = []
    url = "http://localhost:8000/api/press"
    
    async with aiohttp.ClientSession() as session:
        for char in str(digits):
            if char not in "0123456789*#":
                continue
                
            try:
                # Add delay between presses for realism and to let UI update
                if len(results) > 0:
                    await asyncio.sleep(0.3)
                    
                async with session.post(url, json={"digit": char}) as response:
                    if response.status == 200:
                        results.append(char)
                    else:
                        print(f"Failed to press {char}. Status: {response.status}")
            except Exception as e:
                print(f"Failed to press {char}. Error: {e}")
                
    if results:
        return f"Pressed: {''.join(results)}"
    else:
        return "Failed to press digits."

async def think(params):
    """
    Logs a thought to the UI without speaking.
    """
    thought = params.arguments.get("thought")
    if not thought:
        return "Empty thought."
    
    print(f"DEBUG: Agent thinking: {thought}")
    
    # Send thought to UI server
    url = "http://localhost:8000/api/transcription"
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(url, json={"role": "thought", "text": thought})
        except Exception:
            pass
            
    return "Thought logged."

tools = [
    {
        "type": "function",
        "function": {
            "name": "press_digit",
            "description": "Press one or more digits on the phone keypad. You can pass a single digit (e.g. '1') or a sequence (e.g. '123').",
            "parameters": {
                "type": "object",
                "properties": {
                    "digits": {
                        "type": "string",
                        "description": "The digit or sequence of digits to press (0-9, *, #)",
                    }
                },
                "required": ["digits"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Use this tool to think out loud or plan your next step. This will be displayed in the UI but NOT spoken.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "The thought content.",
                    }
                },
                "required": ["thought"]
            }
        }
    }
]
