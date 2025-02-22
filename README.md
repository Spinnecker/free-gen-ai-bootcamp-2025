# Spanish Learning Quiz Application

An interactive application for learning Spanish words with audio pronunciation.

## Features

- Multiple-choice Spanish word quizzes
- Audio pronunciation of Spanish words
- Score tracking with high score system
- Auto-advance timer
- Keyboard shortcuts for accessibility

## Requirements

- Python 3.8 or higher
- Internet connection (for text-to-speech)
- Audio output device

## Quick Start

1. Run the application:
   ```
   python start_app.py
   ```

The launcher will:
- Check and install required dependencies
- Start the backend server
- Launch the frontend application

## Manual Setup (if needed)

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start backend server:
   ```
   python Backend.py
   ```

3. Start frontend application:
   ```
   python FrontEndAudio4.py
   ```

## Keyboard Shortcuts

- 1-4: Select answers
- R: Replay audio
- N: New quiz
- Esc: Exit quiz
- Space: Pause/Resume auto-advance

## Troubleshooting

1. If you see connection errors:
   - Ensure no other application is using port 5000
   - Check if your firewall is blocking localhost connections

2. If you have audio issues:
   - Verify your audio output device is working
   - Check if your system has the required audio codecs

## Files

- `start_app.py`: Application launcher
- `Backend.py`: Flask backend server
- `FrontEndAudio4.py`: Tkinter frontend application
- `requirements.txt`: Python package dependencies
