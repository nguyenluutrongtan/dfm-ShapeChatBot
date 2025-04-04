# DFM Shape Chatbot

A chatbot for drawing geometric shapes using natural language.

## Features

- Draw various geometric shapes using natural language commands
- Support for both English and Vietnamese
- Multiple AI model providers (OpenAI, Deepseek)
- Web interface for easy interaction
- Shape storage and retrieval

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dfm-shape-chatbot.git
cd dfm-shape-chatbot
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .
```

4. Create a `.env` file in the `config` directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_MODEL=o3-mini
DEEPSEEK_MODEL=deepseek-chat
PORT=5000
```

## Usage

1. Start the web server:

```bash
python -m src.core.app
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Start chatting with the bot to draw shapes!

## Project Structure

```
dfm-shape-chatbot/
├── config/             # Configuration files
│   └── .env           # Environment variables
├── data/              # Data files
│   └── shapes.json    # Stored shapes
├── docs/              # Documentation
│   └── README.md      # Project documentation
├── src/               # Source code
│   ├── api/           # API-related code
│   │   └── gpt_connector.py
│   ├── core/          # Core application code
│   │   ├── app.py
│   │   └── chatbot.py
│   ├── models/        # Data models
│   │   └── shape_storage.py
│   ├── utils/         # Utility functions
│   │   └── constants.py
│   └── __init__.py
├── static/            # Static files
├── templates/         # HTML templates
├── tests/             # Test files
├── .gitignore         # Git ignore file
├── requirements.txt   # Python dependencies
└── setup.py           # Package setup file
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
