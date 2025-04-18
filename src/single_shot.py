from openai import OpenAI

from colors import *
from env import GEMINI_API_KEY, GEMINI_MODEL


client = client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

def get_users_intent(query: str) -> str:        
        
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            # tools=TOOLS_DATA_RETRIEVAL,
            # tool_choice='required',
            max_completion_tokens=2100,
            messages=[
            {"role": "system", "content": "ТЫ ЮСТАФ"},
            {"role": "user", "content": f"""
    расскажи теорию относительности
    """}
            ]
        )
        print(response)
        intent = response.choices[0].message.content
        # Check if function was called
        print(f"{GREEN}RESponse: {intent}{RESET}")
       
        return intent
    
    
get_users_intent('asd')