"""
Spanish Sentence Generator from Images
-----------------------------------
This application allows users to upload images containing Spanish words and generates
simple Spanish sentences using those words. It combines OCR (Optical Character Recognition)
for text extraction and OpenAI's GPT-3.5 for sentence generation.

Main Components:
1. Image Processing - Uses Tesseract OCR to extract Spanish text from images
2. Sentence Generation - Uses OpenAI's GPT-3.5 to create contextual Spanish sentences
3. Web Interface - Flask-based web application for user interaction
"""

from flask import Flask, request, render_template, jsonify
from PIL import Image
import os
import openai
from dotenv import load_dotenv
import io
import base64
import subprocess
import time
from functools import wraps

# Load environment variables from .env file (contains API keys and configurations)
load_dotenv()

# Configure paths for external tools
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize Flask application
app = Flask(__name__)

# Configure OpenAI with API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    max_retries: int = 3
):
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        func: The function to retry
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        max_retries: Maximum number of retry attempts
    
    This is particularly useful for handling rate limits and temporary failures
    in API calls by implementing progressive delays between retry attempts.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if the error is related to rate limiting
                if "rate_limit" in str(e).lower() or "rate limit" in str(e).lower():
                    if num_retries >= max_retries:
                        raise e
                    print(f"Rate limit hit. Waiting {delay} seconds...")
                    time.sleep(delay)
                    num_retries += 1
                    delay *= exponential_base
                else:
                    raise e
                
    return wrapper

@retry_with_exponential_backoff
def generate_sentences_with_retry(word):
    """
    Generate Spanish sentences using OpenAI's GPT-3.5 model with retry logic.
    
    Args:
        word: The Spanish word to use in sentence generation
    
    Returns:
        str: Generated sentences or error message
    
    This function includes retry logic for handling API rate limits and
    provides detailed logging for debugging purposes.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key is not set")
        return "Error: OpenAI API key is not configured. Please check your .env file."
    
    print(f"Using API key (first 8 chars): {api_key[:8]}...")
    print(f"Generating sentences for word: {word}")
    
    try:
        # Make API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Spanish language teacher."},
                {"role": "user", "content": f"Generate 3 simple Spanish sentences using the word '{word}'. Each sentence should be suitable for beginners learning Spanish. Format: 1. [sentence]\n2. [sentence]\n3. [sentence]"}
            ],
            temperature=0.7,  # Controls randomness: lower is more focused
            max_tokens=150    # Limits response length
        )
        
        result = response.choices[0].message['content']
        print(f"Generated sentences successfully")
        return result
        
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        raise

def generate_sentences(word):
    """
    Wrapper function for sentence generation that handles all error cases.
    
    Args:
        word: The Spanish word to use in sentence generation
    
    Returns:
        str: Generated sentences or error message
    """
    try:
        return generate_sentences_with_retry(word)
    except Exception as e:
        error_msg = f"Error generating sentences: {str(e)}"
        print(f"Final error in sentence generation: {str(e)}")
        return error_msg

def extract_text_from_image(image_data):
    """
    Extract Spanish text from an image using Tesseract OCR.
    
    Args:
        image_data: Binary image data to process
    
    Returns:
        str: Extracted text or None if extraction failed
    
    This function handles image preprocessing (converting to grayscale)
    and uses Tesseract OCR with Spanish language support for text extraction.
    """
    try:
        # Open and preprocess image
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('L')  # Convert to grayscale
        
        # Save image temporarily for Tesseract processing
        temp_path = os.path.abspath("temp_image.png")
        image.save(temp_path)
        
        try:
            # Verify Tesseract installation
            version_check = subprocess.run([TESSERACT_PATH, '--version'], 
                                        capture_output=True, text=True)
            print("Tesseract version:", version_check.stdout)
        except Exception as e:
            print(f"Error checking Tesseract version: {str(e)}")
            return None
            
        # Process image with Tesseract
        result = subprocess.run([TESSERACT_PATH, temp_path, 'stdout', '-l', 'spa'], 
                              capture_output=True, text=True)
        
        # Log any errors
        if result.stderr:
            print("Tesseract stderr:", result.stderr)
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Check for empty result
        if not result.stdout.strip():
            print("Warning: Tesseract returned empty result")
            return None
            
        return result.stdout.strip()
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None

@app.route('/')
def home():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    """
    Handle image upload and processing.
    
    This endpoint:
    1. Receives the uploaded image
    2. Extracts text using OCR
    3. Generates Spanish sentences using the extracted word
    4. Returns the results as JSON
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    image_data = image_file.read()
    
    # Extract text from image
    extracted_text = extract_text_from_image(image_data)
    if not extracted_text:
        return jsonify({'error': 'Could not extract text from image'}), 400
    
    # Generate sentences
    sentences = generate_sentences(extracted_text)
    
    return jsonify({
        'word': extracted_text,
        'sentences': sentences
    })

if __name__ == '__main__':
    app.run(debug=True)
