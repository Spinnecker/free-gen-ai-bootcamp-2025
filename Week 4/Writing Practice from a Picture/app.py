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

# Load environment variables
load_dotenv()

# Configure paths
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)

# Configure OpenAI with organization
openai.api_key = os.getenv('OPENAI_API_KEY')

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    max_retries: int = 3
):
    """Retry decorator with exponential backoff."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
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
    """Generate sentences with retry logic."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key is not set")
        return "Error: OpenAI API key is not configured. Please check your .env file."
    
    print(f"Using API key (first 8 chars): {api_key[:8]}...")
    print(f"Generating sentences for word: {word}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Spanish language teacher."},
                {"role": "user", "content": f"Generate 3 simple Spanish sentences using the word '{word}'. Each sentence should be suitable for beginners learning Spanish. Format: 1. [sentence]\n2. [sentence]\n3. [sentence]"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        result = response.choices[0].message['content']
        print(f"Generated sentences successfully")
        return result
        
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        raise

def generate_sentences(word):
    """Generate simple Spanish sentences using the extracted word."""
    try:
        return generate_sentences_with_retry(word)
    except Exception as e:
        error_msg = f"Error generating sentences: {str(e)}"
        print(f"Final error in sentence generation: {str(e)}")
        return error_msg

def extract_text_from_image(image_data):
    """Extract text from image using basic OCR approach."""
    try:
        image = Image.open(io.BytesIO(image_data))
        # Convert image to grayscale
        image = image.convert('L')
        # Save temporarily
        temp_path = os.path.abspath("temp_image.png")
        image.save(temp_path)
        
        try:
            # First check if tesseract is available
            version_check = subprocess.run([TESSERACT_PATH, '--version'], 
                                        capture_output=True, text=True)
            print("Tesseract version:", version_check.stdout)
        except Exception as e:
            print(f"Error checking Tesseract version: {str(e)}")
            return None
            
        # Use tesseract command with full path
        result = subprocess.run([TESSERACT_PATH, temp_path, 'stdout', '-l', 'spa'], 
                              capture_output=True, text=True)
        
        # Print any error output
        if result.stderr:
            print("Tesseract stderr:", result.stderr)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
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
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
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
