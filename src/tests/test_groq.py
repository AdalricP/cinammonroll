import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

print(os.getenv("GROQ_API_KEY", "").strip())

client = Groq(
    api_key=os.getenv("GROQ_API_KEY", "").strip(),
)

try:
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say the words or fuck you",
            }
        ],
        model="moonshotai/kimi-k2-instruct-0905",
    )
    print("Success!")
    print(chat_completion.choices[0].message.content[:100])
except Exception as e:
    print(f"Groq API Error: {e}")
