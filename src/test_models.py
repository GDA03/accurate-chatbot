import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv('../.env')
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

models = [
    'gemini-flash-lite-latest',
    'gemini-3.5-flash-lite',
    'gemini-2.5-flash-lite'
]

for m in models:
    try:
        print(f'Testing {m}...')
        res = genai.GenerativeModel(m).generate_content('Test')
        print(f'Success! Response: {res.text}')
    except Exception as e:
        print(f'Failed: {e}')
