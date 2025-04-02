from flask import Flask, request, jsonify, render_template
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from chatbot import SHAPE_REQUIREMENTS, generate_system_prompt, call_gpt

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    conversation = data.get('conversation', [])
    
    if not conversation:
        conversation = [{"role": "system", "content": generate_system_prompt()}]
    
    conversation.append({"role": "user", "content": user_message})
    
    response = call_gpt(conversation)
    
    conversation.append({
        "role": "assistant", 
        "content": json.dumps(response, ensure_ascii=False)
    })
    
    display_message = response.get('message', '')
    if response.get('completed', False):
        shape = response.get('shape', '')
        params_text = ', '.join([
            f"{param}: {details['value']}{details.get('unit', '')}" 
            for param, details in response.get('params', {}).items()
        ])
        display_message = f"Đã vẽ thành công hình {shape}, {params_text}"
    
    return jsonify({
        'message': display_message,
        'conversation': conversation,
        'completed': response.get('completed', False)
    })

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    new_conversation = [{"role": "system", "content": generate_system_prompt()}]
    
    welcome_message = "Xin chào! Tôi có thể giúp bạn vẽ các hình học. Hãy cho tôi biết bạn muốn vẽ hình nào?"
    
    return jsonify({
        'message': welcome_message,
        'conversation': new_conversation,
        'completed': False
    })

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    if os.path.exists('index.html') and not os.path.exists('templates/index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
    
    app.run(debug=True) 