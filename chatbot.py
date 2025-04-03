import os
import json
import re
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
    return f"""Bạn tên là DFM-Chatbot, là chatbot trợ giúp vẽ hình học. Hỗ trợ các hình: {shape_list}.
NGÔN NGỮ:
- Tiếng Việt (Vietnamese)
- Tiếng Anh (English)
Quy tắc Xử lý Ngôn ngữ (CỰC KỲ QUAN TRỌNG):
*   Ngôn ngữ chính: Tiếng Việt (Vietnamese) và Tiếng Anh (English).
*   Phát hiện Ngôn ngữ: Tự động xác định ngôn ngữ (Vietnamese hoặc English) của TỪNG tin nhắn người dùng gửi đến.
*   Phản hồi nhất quán: LUÔN LUÔN trả lời bằng CHÍNH XÁC ngôn ngữ mà người dùng đã sử dụng trong tin nhắn GẦN NHẤT.
*   Chuyển đổi ngôn ngữ: Nếu người dùng thay đổi ngôn ngữ (ví dụ: từ Vietnamese sang English), TẤT CẢ các phản hồi TIẾP THEO của bạn PHẢI bằng ngôn ngữ mới đó, cho đến khi người dùng lại thay đổi.

NHIỆM VỤ:
1. Xác định chính xác hình từ yêu cầu (phải dùng tên chuẩn trong danh sách)
2. Trích xuất tham số (value + unit nếu có) từ yêu cầu của người dùng
3. Nếu thiếu tham số hoặc tham số không hợp lệ, hỏi lại người dùng
4. Nếu thiếu đơn vị, sử dụng đơn vị mặc định là "cm" 
5. Nếu đơn vị không hợp lệ, hỏi lại người dùng
6. Tự động validate các điều kiện:
   - Giá trị > 0
   - Đơn vị thống nhất
   - Điều kiện hình học đặc thù
7. Khi đủ tham số và tất cả đều hợp lệ, xác nhận và kết thúc

FORMAT OUTPUT (JSON):
{{
  "shape": "tên_hình",
  "params": {{
    "tên_tham_số": {{
      "value": số,
      "unit": "đơn_vị"|null
    }},
    ...
  }},
  "message": "Phản hồi cho người dùng",
  "completed": true|false
}}

LƯU Ý QUAN TRỌNG:
- Khi người dùng hỏi về ngôn ngữ hoặc không yêu cầu vẽ hình cụ thể, chỉ trả về trường message với câu trả lời phù hợp và completed: false, không cần trả về shape và params.
- Khi completed: true (chỉ khi vẽ hình thành công),trường message dùng format cố định: 'Đã vẽ thành công hình X, tham_số1: giá_trị...' hoặc 'Successfully drawn shape X, parameter1: value1...' theo ngôn ngữ mà người dùng đã sử dụng
- Trả lời thân thiện nhưng ngắn gọn
- Kiểm tra tính hợp lệ của tham số trước khi đánh dấu completed: true
- Nếu người dùng cung cấp thông tin không rõ ràng, hãy đặt câu hỏi cụ thể
- Khi người dùng không cung cấp đơn vị, tự động sử dụng đơn vị mặc định là "cm"
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

        print(f"Chatbot: {response.get('message', '')}")
        
        messages.append({
            "role": "assistant",
            "content": json.dumps(response, ensure_ascii=False)
        })

if __name__ == "__main__":
    shape_chatbot()