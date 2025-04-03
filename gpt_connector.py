from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

class ChatGPTConnector:
    def __init__(self, api_key=None, model="gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def call_model(self, messages, temperature=0.2, max_tokens=1024):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                json_pattern = r'(\{.*\})'
                match = re.search(json_pattern, content, re.DOTALL)
                
                if match:
                    try:
                        return json.loads(match.group(0))
                    except json.JSONDecodeError:
                        pass
                        
                print("Không thể trích xuất JSON từ phản hồi")
                return {
                    "shape": None,
                    "params": {},
                    "message": "Xin lỗi, tôi gặp vấn đề khi xử lý yêu cầu. Hãy thử lại.",
                    "completed": False
                }
                
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
            return None

gpt_model = ChatGPTConnector() 