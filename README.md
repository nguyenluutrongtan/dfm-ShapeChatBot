# Chatbot Vẽ Hình Học

Ứng dụng web tích hợp chatbot vẽ hình học sử dụng OpenAI API.

## Cài đặt

1. Clone repo này về máy
2. Cài đặt các thư viện cần thiết:

```
pip install -r requirements.txt
```

3. Tạo file `.env` chứa API key của OpenAI:

```
OPENAI_API_KEY=your_openai_api_key
```

## Cách chạy

1. Chạy ứng dụng Flask:

```
python app.py
```

2. Mở trình duyệt và truy cập: http://localhost:5000

## Cách sử dụng

1. Khi trang web mở, bấm vào biểu tượng chatbot
2. Nhập yêu cầu vẽ hình muốn tạo (ví dụ: "vẽ hình vuông cạnh 5cm")
3. Chatbot sẽ hỏi thêm thông tin nếu cần và xác nhận khi đã đủ thông tin

## Các hình hỗ trợ

- Vuông
- Chữ nhật
- Tròn
- Tam giác
- Thoi
- Elip
- Thang
- Bình hành
- Ngũ giác đều
- Lục giác đều
- Bát giác đều
