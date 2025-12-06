import os
from dotenv import load_dotenv

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    print(f"GROQ_API_KEY found. Length: {len(groq_key)}")
    print(f"Prefix: {groq_key[:4]}...")
    print(f"Suffix: ...{groq_key[-4:]}")
else:
    print("GROQ_API_KEY not found in environment.")

# Check file existence
if os.path.exists(".env"):
    print(".env file exists.")
else:
    print(".env file NOT found.")
