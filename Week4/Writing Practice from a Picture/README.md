# Spanish Learning Prototyping Application

This application allows users to take pictures of Spanish words and generates simple sentences using those words.

## Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed on your system
3. OpenAI API key (for sentence generation)

## Setup

1. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Make sure to add Tesseract to your system PATH

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Features

- Upload images containing Spanish words
- OCR processing to extract Spanish text
- Generate simple Spanish sentences using the extracted words
- Display both the extracted word and generated sentences
