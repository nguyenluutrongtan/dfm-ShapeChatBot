from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SHAPE_REQUIREMENTS = {
    "vuông": ["cạnh"],
    "chữ nhật": ["chiều rộng", "chiều dài"],
    "tròn": ["bán kính"],
    "tam giác": ["cạnh a", "cạnh b", "cạnh c"],
    "thoi": ["cạnh", "góc nhọn"],
    "elip": ["bán trục lớn", "bán trục nhỏ"],
    "thang": ["đáy lớn", "đáy nhỏ", "chiều cao", "cạnh bên"],
    "bình hành": ["cạnh a", "cạnh b", "góc nhọn"],
    "ngũ giác đều": ["cạnh"],
    "lục giác đều": ["cạnh"],
    "bát giác đều": ["cạnh"]
}

def generate_system_prompt():
    shape_list = ", ".join(SHAPE_REQUIREMENTS.keys())
    return f"""Bạn tên là DFM-Chatbot, là chatbot trợ giúp vẽ hình học. Hỗ trợ các hình: {shape_list}.
NGÔN NGỮ:
- Tiếng Việt
- Tiếng Anh (English)
QUAN TRỌNG VỀ NGÔN NGỮ:
- Phát hiện ngôn ngữ mà người dùng sử dụng (tiếng Việt hoặc tiếng Anh)
- LUÔN trả lời bằng CÙNG ngôn ngữ mà người dùng đã sử dụng GẦN NHẤT
- Khi người dùng chuyển sang tiếng Anh, TẤT CẢ các trả lời tiếp theo phải bằng tiếng Anh
- Khi người dùng chuyển sang tiếng Việt, TẤT CẢ các trả lời tiếp theo phải bằng tiếng Việt

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
- Khi completed: true (chỉ khi vẽ hình thành công), bỏ qua trường message và dùng format cố định: 'Đã vẽ thành công hình X, tham_số1: giá_trị...'
- Trả lời thân thiện nhưng ngắn gọn
- Kiểm tra tính hợp lệ của tham số trước khi đánh dấu completed: true
- Nếu người dùng cung cấp thông tin không rõ ràng, hãy đặt câu hỏi cụ thể
- Khi người dùng không cung cấp đơn vị, tự động sử dụng đơn vị mặc định là "cm"
"""

def format_params(params):
    return ", ".join(
        f"{name}: {data['value']}{data['unit'] if data.get('unit') else ''}"
        for name, data in params.items()
    )

def call_gpt(messages):
    try:
        response = client.chat.completions.create(
            model="o3-mini",
            messages=messages,
            #temperature=0.2,
            max_completion_tokens=1024,
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

        if response.get("completed", False):
            print(f"Chatbot: Đã vẽ thành công hình {response['shape']}, {format_params(response['params'])}")
            messages = [messages[0]]
        else:
            print(f"Chatbot: {response['message']}")
        
        messages.append({
            "role": "assistant",
            "content": json.dumps(response, ensure_ascii=False)
        })

if __name__ == "__main__":
    shape_chatbot()