from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from config directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', '.env'))

class ModelConnector:
    def __init__(self, api_key=None, model=None, provider="openai"):
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL")
            if not self.model:
                raise ValueError("OPENAI_MODEL environment variable is required")
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "deepseek":
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.model = model or os.getenv("DEEPSEEK_MODEL")
            if not self.model:
                raise ValueError("DEEPSEEK_MODEL environment variable is required")
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def call_model(self, messages, temperature=0.2, max_tokens=1024):
        """
        Call the AI model with the given messages
        """
        try:
            response_params = {
                "model": self.model,
                "messages": messages,
                #"temperature": temperature
            }
            
            # Handle provider-specific parameters
            if self.provider == "OpenAI":
                response_params["max_completion_tokens"] = max_tokens
                response_params["reasoning_effort"] = "low"
            elif self.provider == "Deepseek":
                response_params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**response_params)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return None

# Create a default connector instance for easy import
default_connector = ModelConnector()

# Example usage
if __name__ == "__main__":
    # Initialize connectors
    openai_connector = ModelConnector(provider="OpenAI")
    deepseek_connector = ModelConnector(provider="Deepseek")
    
    # Example OpenAI call
    openai_response = openai_connector.call_model(
        messages=[{"role": "user", "content": "Hello GPT!"}]
    )
    print(f"OpenAI response: {openai_response}")
    
    # Example Deepseek call
    deepseek_response = deepseek_connector.call_model(
        messages=[{"role": "user", "content": "Hello Deepseek!"}]
    )
    print(f"Deepseek response: {deepseek_response}")