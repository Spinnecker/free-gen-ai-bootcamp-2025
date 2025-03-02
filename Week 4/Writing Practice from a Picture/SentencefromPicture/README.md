# Spanish Sentence Generator from Images

This application helps users learn Spanish by generating simple sentences from Spanish words captured in images. It combines Optical Character Recognition (OCR) technology with AI-powered sentence generation to create a interactive learning experience.

## Features

- Upload or take pictures containing Spanish words
- Extract text from images using Tesseract OCR
- Generate contextual Spanish sentences using OpenAI's GPT-3.5
- Modern, responsive web interface
- Error handling and retry logic for API calls

## Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed on your system
3. OpenAI API key with active billing

## Installation

1. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Make sure to add Tesseract to your system PATH
   - During installation, select "Spanish" in the additional language data

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual OpenAI API key

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Click "Take/Upload Picture" to either:
   - Take a picture using your device's camera
   - Upload an existing image file

4. The application will:
   - Extract the Spanish word from the image
   - Generate three simple Spanish sentences using that word
   - Display both the extracted word and the generated sentences

## Code Structure

- `app.py`: Main application file containing:
  - Flask web server setup
  - Image processing logic
  - OpenAI integration
  - Error handling and retry logic

- `templates/index.html`: Frontend interface with:
  - Image upload functionality
  - Result display
  - Responsive styling

## Error Handling

The application includes robust error handling for:
- Image processing failures
- OCR text extraction issues
- API rate limits
- Network connectivity problems
- Invalid API keys

## Limitations

1. Requires clear, well-lit images of Spanish text
2. Depends on OpenAI API availability and quotas
3. Requires internet connection for sentence generation

## Future Improvements

1. Add support for multiple languages
2. Implement offline mode with pre-generated sentences
3. Add pronunciation guides
4. Include translation of generated sentences
5. Add ability to save favorite sentences

## Contributing

Feel free to submit issues and enhancement requests!
