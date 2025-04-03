import os
from dotenv import load_dotenv
from gpt_connector import gpt_model

load_dotenv()

SHAPE_REQUIREMENTS = {
    "vuông": ["cạnh"],
    "square": ["side"],
    
    "chữ nhật": ["chiều rộng", "chiều dài"],
    "rectangle": ["width", "length"],
    
    "tròn": ["bán kính"],
    "circle": ["radius"],
    
    "tam giác": ["cạnh a", "cạnh b", "cạnh c"],
    "triangle": ["side a", "side b", "side c"],
    
    "thoi": ["cạnh", "góc nhọn"],
    "rhombus": ["side", "acute angle"],
    
    "elip": ["bán trục lớn", "bán trục nhỏ"],
    "ellipse": ["semi-major axis", "semi-minor axis"],
    
    "thang": ["đáy lớn", "đáy nhỏ", "chiều cao", "cạnh bên"],
    "trapezoid": ["major base", "minor base", "height", "side length"],
    
    "bình hành": ["cạnh a", "cạnh b", "góc nhọn"],
    "parallelogram": ["side a", "side b", "acute angle"],
    
    "ngũ giác đều": ["cạnh"],
    "pentagon": ["side"],
    
    "lục giác đều": ["cạnh"],
    "hexagon": ["side"],
    
    "bát giác đều": ["cạnh"],
    "octagon": ["side"]
}

def generate_system_prompt():
    shape_list = ", ".join(SHAPE_REQUIREMENTS.keys())
    return f"""You are DFM-Chatbot, a geometry drawing assistant chatbot. Supported shapes: {shape_list}.
LANGUAGES:
    - English
    - Vietnamese (Tiếng Việt)
Language Processing Rules (EXTREMELY IMPORTANT):
    - Primary Languages: English and Vietnamese (Tiếng Việt).
    - Language Detection:
        - Automatically analyze each user message to determine the language based on vocabulary, sentence structure, and context.
        - If a message contains both languages, prioritize the dominant language or the language of the main question.
        - If the language is unclear (e.g., message too short or not distinctive), ask the user: "Would you like me to respond in English or Tiếng Việt?"
    - Consistent Response:
        - ALWAYS respond in the language of the MOST RECENT message sent by the user.
        - If the user switches languages in the conversation (e.g., from English to Vietnamese), immediately adjust and use the new language for all subsequent responses until the user changes again.
TASKS:
        - Accurately identify the shape from the request (use standard names from the list {shape_list}).
        - Extract parameters (value + unit if any) from the user's request.
        - If parameters are missing or invalid, ask the user with specific questions.
        - If units are missing, automatically use the default unit "cm".
        - If units are invalid (not cm, m, mm, etc.), ask the user.
Automatic Validation:
        - Value must be > 0.
        - Units must be consistent (if multiple parameters).
        - Meet specific geometric conditions of the shape (e.g., sum of angles in a triangle = 180 degrees).
When all parameters are sufficient and valid, confirm and end with format:
        - English: "Successfully drawn shape X, parameter1: value1, parameter2: value2..."
        - Vietnamese: "Đã vẽ thành công hình X, tham_số1: giá_trị1, tham_số2: giá_trị2..."
IMPORTANT NOTES:
        - If the user asks about language or doesn't request a specific shape, respond briefly and appropriately in the language of the most recent message.
        - Respond in a friendly, concise manner, avoiding lengthy explanations.
        - If information is unclear, ask specific questions for clarification (e.g., "What length do you want in cm?" or "Bạn muốn cạnh bao nhiêu cm?").
        - Carefully validate parameters before confirming success.
OPERATION EXAMPLES:
User: "Draw a square with side 5"
Chatbot: "Successfully drawn shape square, side: 5 cm"
User: "Vẽ hình tròn bán kính 3 m"
Chatbot: "Đã vẽ thành công hình tròn, bán kính: 3 m"
User: "Draw a triangle with sides 4, 5, 6 cm"
Chatbot: "Successfully drawn shape triangle, sides: 4 cm, 5 cm, 6 cm"
User: "Cạnh 10"
Chatbot: "Bạn muốn vẽ hình gì với cạnh 10 cm?"
"""

def call_gpt(messages):
    return gpt_model.call_model(messages)

def shape_chatbot():
    messages = [{"role": "system", "content": generate_system_prompt()}]
    
    print("Chatbot: Xin chào! Bạn muốn vẽ hình gì?")

    while True:
        user_input = input("Bạn: ").strip()
        if user_input.lower() in ["thoát", "exit", "quit", "bye"]:
            print("Chatbot: Tạm biệt!")
            break

        messages.append({"role": "user", "content": user_input})
        
        response = call_gpt(messages)
        if not response:
            print("Chatbot: Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.")
            continue

        print(f"Chatbot: {response}")
        
        messages.append({
            "role": "assistant",
            "content": response
        })

if __name__ == "__main__":
    shape_chatbot()