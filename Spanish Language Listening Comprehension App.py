"""
Spanish Language Listening Comprehension Application
------------------------------------------------
This application helps users practice Spanish listening comprehension through
interactive exercises. It uses AWS Polly for text-to-speech conversion and
OpenAI's Whisper model for speech recognition.

Main Components:
- AWS Polly: Neural text-to-speech engine for natural Spanish pronunciation
- Whisper: State-of-the-art speech recognition model
- Flask: Web framework for handling HTTP requests
- FFmpeg: Audio processing for format conversion
"""

from flask import Flask, render_template, request, jsonify, send_file
import boto3
import whisper
import os
from dotenv import load_dotenv
import tempfile
from pydub import AudioSegment
import io
import shutil

# Load environment variables from .env file
load_dotenv()

# Debug print for environment variables (masked for security)
print("AWS Environment Variables:")
print(f"AWS_ACCESS_KEY_ID: {'*' * len(os.getenv('AWS_ACCESS_KEY_ID', ''))} (length: {len(os.getenv('AWS_ACCESS_KEY_ID', ''))})")
print(f"AWS_SECRET_ACCESS_KEY: {'*' * len(os.getenv('AWS_SECRET_ACCESS_KEY', ''))} (length: {len(os.getenv('AWS_SECRET_ACCESS_KEY', ''))})")
print(f"AWS_REGION: {os.getenv('AWS_REGION')}")

# Initialize Flask application
app = Flask(__name__)

# Configure pydub paths for audio processing
current_dir = os.getcwd()
AudioSegment.converter = os.path.join(current_dir, "ffmpeg.exe")
AudioSegment.ffmpeg = os.path.join(current_dir, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(current_dir, "ffmpeg.exe")

print(f"FFmpeg path set to: {AudioSegment.converter}")
print(f"FFmpeg exists: {os.path.exists(AudioSegment.converter)}")

# Initialize AWS Polly client for text-to-speech
polly_client = boto3.client(
    'polly',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# Initialize Whisper model for speech recognition
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully")

# Sample Spanish exercises with questions and answers
EXERCISES = [
    {
        "text": "¿Cómo estás? Me llamo Juan y soy de España.",
        "question": "What is the speaker's name and where are they from?",
        "answer": "His name is Juan and he is from Spain"
    },
    {
        "text": "Me gusta mucho viajar y conocer nuevas culturas.",
        "question": "What does the speaker like to do?",
        "answer": "They like to travel and learn about new cultures"
    }
]

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    Convert Spanish text to speech using AWS Polly
    
    Endpoint: POST /synthesize
    Request body: JSON with 'text' field containing Spanish text
    Returns: Audio file (MP3) of synthesized speech
    """
    text = request.json.get('text')
    
    try:
        print(f"Attempting to synthesize speech for text: {text}")
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Lupe',  # Mexican Spanish female voice with neural engine support
            Engine='neural'  # Using the neural engine for better quality
        )
        
        if "AudioStream" in response:
            print("Successfully generated audio stream")
            return send_file(
                io.BytesIO(response['AudioStream'].read()),
                mimetype='audio/mp3'
            )
        else:
            print("No AudioStream in response")
            return jsonify({'error': 'No audio stream generated'}), 500
    except Exception as e:
        print(f"Error in synthesize_speech: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe spoken Spanish audio using Whisper model
    
    Endpoint: POST /transcribe
    Request body: Multipart form with 'audio' file (WebM format)
    Returns: JSON with transcribed text and detected language
    
    Process:
    1. Save uploaded audio file
    2. Convert audio to WAV format using FFmpeg
    3. Transcribe using Whisper model
    4. Clean up temporary files
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    print(f"Received audio file of type: {audio_file.content_type}")
    
    try:
        # Save the original audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_webm:
            audio_file.save(temp_webm.name)
            print(f"Saved original audio file to: {temp_webm.name}")
            print(f"File exists: {os.path.exists(temp_webm.name)}")
            print(f"File size: {os.path.getsize(temp_webm.name)} bytes")
            
            try:
                print("Attempting audio conversion...")
                # Convert audio to format compatible with Whisper
                audio = AudioSegment.from_file(temp_webm.name, format='webm')
                print("Successfully loaded audio file")
                
                # Set audio properties for optimal speech recognition
                audio = audio.set_frame_rate(16000).set_channels(1)
                print("Set audio properties")
                
                # Export to WAV format
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                    wav_path = temp_wav.name
                    print(f"Exporting to WAV: {wav_path}")
                    audio.export(wav_path, format='wav', parameters=["-ac", "1", "-ar", "16000"])
                    print("Successfully exported to WAV")
                    
                    # Perform transcription
                    result = model.transcribe(wav_path)
                    print("Transcription complete")
                    
                    # Clean up temporary files
                    os.unlink(temp_webm.name)
                    os.unlink(wav_path)
                    
                    return jsonify({
                        'text': result['text'],
                        'language': result.get('language', 'unknown')
                    })
            except Exception as e:
                print(f"Detailed conversion error: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                return jsonify({'error': f'Audio conversion failed: {str(e)}'}), 500
    except Exception as e:
        print(f"Outer error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/exercises', methods=['GET'])
def get_exercises():
    """Return the list of Spanish language exercises"""
    return jsonify(EXERCISES)

if __name__ == '__main__':
    app.run(debug=True)
