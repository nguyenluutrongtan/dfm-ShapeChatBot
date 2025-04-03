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
    
    if not isinstance(response, dict):
        response = {
            "message": "Sorry, I encountered an issue processing your request.",
            "completed": False
        }
    
    conversation.append({
        "role": "assistant", 
        "content": json.dumps(response, ensure_ascii=False)
    })
    
    display_message = response.get('message', '')
    if response.get('completed', False) and response.get('shape'):
        shape = response.get('shape', '')
        params = response.get('params', {})
        if shape and params:
            params_text = ', '.join([
                f"{param}: {details['value']}{details.get('unit', '')}" 
                for param, details in params.items()
            ])
            
            # Nhận dạng ngôn ngữ
            def detect_vietnamese(text):
                vietnamese_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
                
                text = text.lower()
                
                vietnamese_char_count = sum(1 for c in text if c in vietnamese_chars)
                
                common_vn_words = ['toi', 'ban', 've', 'hinh', 'vuong', 'tron', 'tam', 'giac', 'xin', 'chao', 'muon']
                words = text.split()
                vn_word_matches = sum(1 for word in words if word in common_vn_words)
                
                if vietnamese_char_count > 0:
                    return True
                elif vn_word_matches >= 1 and len(words) <= 10:
                    return True
                elif 'cm' in text and any(w in text for w in ['hinh', 've', 'canh']):
                    return True
                else:
                    english_indicators = ['square', 'circle', 'triangle', 'rectangle', 'draw', 'side', 'length']
                    if any(word in text.lower() for word in english_indicators):
                        return False
                    return True
            
            is_vietnamese = detect_vietnamese(user_message)
            
            if is_vietnamese:
                display_message = f"Đã vẽ thành công hình {shape}, {params_text}"
            else:
                display_message = f"Successfully drawn {shape}, {params_text}"
    
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
    
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port) 