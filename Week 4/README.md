# Spanish Language Listening Comprehension App

A web application designed to help users practice and improve their Spanish listening comprehension skills. The app uses AWS Polly for text-to-speech conversion and Whisper for speech-to-text transcription.

## Features

- Text-to-Speech: Convert Spanish text to natural-sounding speech using AWS Polly's neural engine
- Speech-to-Text: Practice pronunciation by recording your voice and getting transcriptions
- Interactive Exercises: Pre-loaded Spanish language exercises with questions and answers
- Real-time Feedback: Compare your spoken responses with correct transcriptions

## Technical Requirements

- Python 3.8+
- Flask web framework
- AWS Polly for text-to-speech
- OpenAI Whisper for speech recognition
- FFmpeg for audio processing

## Setup

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Set up your AWS credentials in `.env`:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
```

3. Ensure FFmpeg is available in the project directory

## Running the App

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

1. Select an exercise from the provided Spanish language prompts
2. Listen to the Spanish audio using the "Play" button
3. Record your response using the microphone button
4. Submit your recording to see how well you did

## Note

This app requires a microphone for speech input and speakers/headphones for audio output.
