from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ChatGPTConnector:
    def __init__(self, api_key=None, model="o3-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def call_model(self, messages, temperature=0.2, max_tokens=1024):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=max_tokens,
                reasoning_effort="low"
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
            return None

gpt_model = ChatGPTConnector() 