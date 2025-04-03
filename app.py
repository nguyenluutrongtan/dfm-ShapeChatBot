from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from chatbot import SHAPE_REQUIREMENTS, generate_system_prompt, call_gpt
from shape_storage import shape_storage

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
    
    if not response:
        response = "Xin lỗi, tôi gặp vấn đề khi xử lý yêu cầu. Hãy thử lại."
    
    conversation.append({
        "role": "assistant", 
        "content": response
    })

    shape_storage.process_and_save_shape(response)
    
    return jsonify({
        'message': response,
        'conversation': conversation
    })

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    new_conversation = [{"role": "system", "content": generate_system_prompt()}]
    
    welcome_message = "Xin chào! Tôi có thể giúp bạn vẽ các hình học. Hãy cho tôi biết bạn muốn vẽ hình nào?"
    
    return jsonify({
        'message': welcome_message,
        'conversation': new_conversation
    })

@app.route('/api/shapes', methods=['GET'])
def get_shapes():
    return jsonify({
        'shapes': shape_storage.get_all_shapes()
    })

@app.route('/api/shapes/<shape_name>', methods=['GET'])
def get_shapes_by_name(shape_name):
    return jsonify({
        'shapes': shape_storage.get_shapes_by_name(shape_name)
    })

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    if os.path.exists('index.html') and not os.path.exists('templates/index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
    
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port) 