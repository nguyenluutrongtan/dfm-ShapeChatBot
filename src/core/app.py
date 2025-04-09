from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv

# Load environment variables from config directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', '.env'))

from src.utils.constants import SHAPE_REQUIREMENTS
from src.core.chatbot import generate_system_prompt, call_model
from src.models.shape_storage import shape_storage
from src.api.model_connector import ModelConnector

# Initialize with OpenAI as default
model_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
model_name = os.getenv("OPENAI_MODEL")
if not model_name:
    raise ValueError("OPENAI_MODEL environment variable is required")
model_connector = ModelConnector(provider=model_provider, model=model_name)

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')

app = Flask(__name__, 
            template_folder=templates_dir,
            static_folder=static_dir)

@app.route('/')
def index():
    openai_model = os.getenv("OPENAI_MODEL", "")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "")
    return render_template('index.html', openai_model=openai_model, deepseek_model=deepseek_model)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    conversation = data.get('conversation', [])
    
    if not conversation:
        conversation = [{"role": "system", "content": generate_system_prompt()}]
    
    conversation.append({"role": "user", "content": user_message})
    
    response = call_model(conversation, model_connector)
    
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

@app.route('/api/change_model', methods=['POST'])
def change_model():
    global model_connector, model_provider, model_name
    
    data = request.json
    provider = data.get('provider', 'openai')
    
    if provider == 'openai':
        model = data.get('model', os.getenv("OPENAI_MODEL"))
        model_name_env = os.getenv("OPENAI_MODEL_NAME", f"OpenAI ({model})")
        if not model:
            return jsonify({
                'success': False,
                'message': "OPENAI_MODEL environment variable is required"
            }), 400
    elif provider == 'deepseek':
        model = data.get('model', os.getenv("DEEPSEEK_MODEL"))
        model_name_env = os.getenv("DEEPSEEK_MODEL_NAME", f"Deepseek ({model})")
        if not model:
            return jsonify({
                'success': False,
                'message': "DEEPSEEK_MODEL environment variable is required"
            }), 400
    else:
        return jsonify({
            'success': False,
            'message': "Nhà cung cấp không được hỗ trợ"
        }), 400
    
    model_provider = provider
    model_name = model
    model_connector = ModelConnector(provider=provider, model=model)
    
    return jsonify({
        'success': True,
        'provider': provider,
        'model': model,
        'model_name': model_name_env
    })

@app.route('/api/get_model', methods=['GET'])
def get_model():
    provider = model_provider
    model = model_name
    
    if provider == 'openai':
        model_name_env = os.getenv("OPENAI_MODEL_NAME", f"OpenAI ({model})")
    elif provider == 'deepseek':
        model_name_env = os.getenv("DEEPSEEK_MODEL_NAME", f"Deepseek ({model})")
    else:
        model_name_env = f"{provider.capitalize()} ({model})"
        
    return jsonify({
        'provider': provider,
        'model': model,
        'model_name': model_name_env
    })

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    new_conversation = [{"role": "system", "content": generate_system_prompt()}]
    
    # Get current model name
    provider = model_provider
    model = model_name
    
    if provider == 'openai':
        model_name_env = os.getenv("OPENAI_MODEL_NAME", f"OpenAI ({model})")
    elif provider == 'deepseek':
        model_name_env = os.getenv("DEEPSEEK_MODEL_NAME", f"Deepseek ({model})")
    else:
        model_name_env = f"{provider.capitalize()} ({model})"
    
    welcome_message = f"Xin chào! Tôi là {model_name_env}. Tôi có thể giúp bạn vẽ các hình học. Hãy cho tôi biết bạn muốn vẽ hình nào?"
    
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

@app.route('/api/shapes/<int:shape_index>', methods=['DELETE'])
def delete_shape(shape_index):
    success = shape_storage.delete_shape(shape_index)
    return jsonify({
        'success': success
    })

if __name__ == '__main__':
    # Ensure templates directory exists
    os.makedirs(templates_dir, exist_ok=True)
    
    # Copy index.html to templates directory if it doesn't exist
    index_src = os.path.join(project_root, 'index.html')
    index_dst = os.path.join(templates_dir, 'index.html')
    
    if os.path.exists(index_src) and not os.path.exists(index_dst):
        with open(index_src, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(index_dst, 'w', encoding='utf-8') as f:
            f.write(content)
    
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port) 