# Spanish Vocabulary Generator (Week 3 - FastAPI + OpenAI LLM)

A web-based Spanish vocabulary learning tool that uses OpenAI's GPT-3.5 to generate contextually relevant vocabulary words based on user-selected topics.

## Features

- Generate Spanish vocabulary words by topic
- Configurable word count (6, 8, or 10 words)
- OpenAI GPT-3.5 integration for dynamic vocabulary generation
- Web-based interface
- Fallback to sample data if no API key is present

## Technical Stack

- Backend: Flask
- AI Integration: OpenAI API (GPT-3.5-turbo)
- Frontend: HTML/JavaScript
- Python Version: 3.13

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
   - Copy `.env.template` to `.env`
   - Add your OpenAI API key to `.env`

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://127.0.0.1:8000`

## Usage

1. Enter a topic (e.g., "food", "travel", "technology")
2. Select the number of words to generate (6, 8, or 10)
3. Click "Generate" to get vocabulary words
4. Each word includes:
   - Spanish word
   - English translation
   - Example sentence in Spanish

## Note

If no OpenAI API key is provided, the application will fall back to using sample vocabulary data.
