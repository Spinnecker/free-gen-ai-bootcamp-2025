import tkinter as tk
from tkinter import messagebox, ttk
import random
import requests
import json
import time
import threading
from gtts import gTTS
import os
import pygame
from pathlib import Path
import logging
from datetime import datetime
import sys
import webbrowser

class SpanishQuizLovableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("¡Aprende Español! - Spanish Learning Quiz")
        self.root.geometry("600x750")
        
        # Set up logging
        self.setup_logging()
        
        # Initialize pygame mixer for audio
        try:
            pygame.mixer.init()
        except pygame.error as e:
            logging.error(f"Failed to initialize audio: {e}")
            self.show_error("Audio System Error", 
                          "Failed to initialize audio system. The quiz will continue without audio.")
        
        # Create audio directory if it doesn't exist
        self.audio_dir = Path("audio_files")
        self.audio_dir.mkdir(exist_ok=True)
        
        # Create and configure styles
        self.setup_styles()
        
        # Initialize state variables
        self.current_question = 0
        self.score = 0
        self.quiz_data = None
        self.auto_advance_time = 8  # Increased time for better accessibility
        self.audio_queue = []
        self.is_narrating = False
        self.high_score = self.load_high_score()
        
        # Create UI components
        self.create_ui()
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Start the first quiz after a short delay
        self.root.after(1000, self.start_new_quiz)
        
        # Setup auto-save
        self.setup_autosave()
    
    def setup_logging(self):
        """Configure application logging with rotation"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / f"quiz_log_{datetime.now().strftime('%Y%m%d')}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def setup_styles(self):
        """Configure ttk styles with lovable design principles"""
        style = ttk.Style()
        
        # Configure modern button styles
        style.configure(
            "Quiz.TButton",
            padding=10,
            font=("Arial", 12),
            background="#4CAF50",
            relief="raised"
        )
        
        style.configure(
            "Audio.TButton",
            padding=10,
            font=("Arial", 12),
            foreground="#2196F3"
        )
        
        style.configure(
            "Exit.TButton",
            padding=10,
            font=("Arial", 12),
            foreground="#f44336"
        )
        
        # Configure label styles
        style.configure(
            "Title.TLabel",
            font=("Arial", 16, "bold"),
            padding=10
        )
        
        style.configure(
            "Score.TLabel",
            font=("Arial", 14),
            padding=5
        )
    
    def create_ui(self):
        """Create the user interface with accessibility in mind"""
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create title
        self.title_label = ttk.Label(
            self.main_frame,
            text="Spanish Learning Quiz",
            style="Title.TLabel"
        )
        self.title_label.grid(row=0, column=0, pady=10)
        
        # Create status section
        self.create_status_section()
        
        # Create quiz section
        self.create_quiz_section()
        
        # Create control section
        self.create_control_section()
        
        # Create help section
        self.create_help_section()
    
    def create_status_section(self):
        """Create the status section of the UI"""
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Status: Ready",
            font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0, pady=5)
        
        self.score_label = ttk.Label(
            status_frame,
            text="Score: 0/0",
            style="Score.TLabel"
        )
        self.score_label.grid(row=1, column=0, pady=5)
        
        self.high_score_label = ttk.Label(
            status_frame,
            text=f"High Score: {self.high_score}",
            style="Score.TLabel"
        )
        self.high_score_label.grid(row=1, column=1, pady=5, padx=10)
        
        self.timer_label = ttk.Label(
            status_frame,
            text="",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.timer_label.grid(row=2, column=0, columnspan=2, pady=5)
    
    def create_quiz_section(self):
        """Create the quiz section of the UI"""
        quiz_frame = ttk.LabelFrame(self.main_frame, text="Question", padding="10")
        quiz_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.question_label = ttk.Label(
            quiz_frame,
            text="",
            font=("Arial", 14),
            wraplength=500
        )
        self.question_label.grid(row=0, column=0, pady=10)
        
        self.speaking_label = ttk.Label(
            quiz_frame,
            text="",
            font=("Arial", 10, "italic"),
            foreground="blue"
        )
        self.speaking_label.grid(row=1, column=0, pady=5)
        
        # Create answer buttons
        self.button_frame = ttk.Frame(quiz_frame)
        self.button_frame.grid(row=2, column=0, pady=10)
        
        self.answer_buttons = []
        for i in range(4):
            btn = ttk.Button(
                self.button_frame,
                text="",
                style="Quiz.TButton",
                command=lambda i=i: self.check_answer(i)
            )
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            self.answer_buttons.append(btn)
            
            # Add tooltip
            self.create_tooltip(btn, f"Press {i+1} to select this answer")
    
    def create_control_section(self):
        """Create the control section of the UI"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.replay_button = ttk.Button(
            control_frame,
            text="🔊 Replay Question & Options (R)",
            command=self.replay_audio,
            style="Audio.TButton"
        )
        self.replay_button.grid(row=0, column=0, pady=5, padx=5)
        
        self.new_quiz_button = ttk.Button(
            control_frame,
            text="Start New Quiz (N)",
            command=self.start_new_quiz,
            style="Quiz.TButton"
        )
        self.new_quiz_button.grid(row=0, column=1, pady=5, padx=5)
        
        self.exit_button = ttk.Button(
            control_frame,
            text="Exit Quiz (Esc)",
            command=self.exit_application,
            style="Exit.TButton"
        )
        self.exit_button.grid(row=0, column=2, pady=5, padx=5)
    
    def create_help_section(self):
        """Create the help section with keyboard shortcuts"""
        help_frame = ttk.LabelFrame(self.main_frame, text="Help", padding="10")
        help_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        shortcuts_text = """
        Keyboard Shortcuts:
        • 1-4: Select answers
        • R: Replay audio
        • N: New quiz
        • Esc: Exit quiz
        • Space: Pause/Resume auto-advance
        """
        
        help_label = ttk.Label(
            help_frame,
            text=shortcuts_text,
            justify=tk.LEFT,
            font=("Arial", 10)
        )
        help_label.grid(row=0, column=0, sticky=tk.W)
        
        # Add lovable.dev link
        link_label = ttk.Label(
            help_frame,
            text="Built with ❤️ using lovable.dev principles",
            font=("Arial", 10, "italic"),
            foreground="blue",
            cursor="hand2"
        )
        link_label.grid(row=1, column=0, pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://lovable.dev"))
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better accessibility"""
        self.root.bind("<Key-1>", lambda e: self.check_answer(0))
        self.root.bind("<Key-2>", lambda e: self.check_answer(1))
        self.root.bind("<Key-3>", lambda e: self.check_answer(2))
        self.root.bind("<Key-4>", lambda e: self.check_answer(3))
        self.root.bind("<Key-r>", lambda e: self.replay_audio())
        self.root.bind("<Key-n>", lambda e: self.start_new_quiz())
        self.root.bind("<Escape>", lambda e: self.exit_application())
        self.root.bind("<space>", lambda e: self.toggle_auto_advance())
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind("<Leave>", lambda e: hide_tooltip())
        
        widget.bind("<Enter>", show_tooltip)
    
    def show_error(self, title, message):
        """Show error message with logging"""
        logging.error(f"{title}: {message}")
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """Show info message with logging"""
        logging.info(f"{title}: {message}")
        messagebox.showinfo(title, message)
    
    def toggle_auto_advance(self):
        """Toggle auto-advance feature"""
        if hasattr(self, 'auto_advance_timer'):
            self.root.after_cancel(self.auto_advance_timer)
            del self.auto_advance_timer
            self.timer_label.config(text="Auto-advance paused")
        else:
            self.start_timer()
            self.timer_label.config(text="Auto-advance resumed")
    
    def load_high_score(self):
        """Load high score from file"""
        try:
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except FileNotFoundError:
            return 0
        except json.JSONDecodeError:
            logging.error("Failed to load high score file")
            return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except Exception as e:
            logging.error(f"Failed to save high score: {e}")
    
    def setup_autosave(self):
        """Setup periodic autosave"""
        self.save_high_score()
        self.root.after(60000, self.setup_autosave)  # Autosave every minute
    
    def update_high_score(self):
        """Update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_label.config(text=f"High Score: {self.high_score}")
            self.save_high_score()
            self.show_info("New High Score!", f"Congratulations! New high score: {self.high_score}")

    def start_new_quiz(self):
        """Start a new quiz by fetching questions from the backend"""
        try:
            response = requests.get('http://127.0.0.1:5000/get_questions')
            if response.status_code == 200:
                self.quiz_data = response.json()
                self.current_question = 0
                self.score = 0
                self.score_label.config(text="Score: 0/0")
                self.display_question()
                self.status_label.config(text="Status: Quiz started")
            else:
                self.show_error("Backend Error", 
                              f"Failed to fetch questions: {response.status_code}")
        except requests.RequestException as e:
            self.show_error("Connection Error",
                          "Failed to connect to backend. Is the server running?")
            logging.error(f"Backend connection error: {e}")

    def display_question(self):
        """Display the current question and options"""
        if not self.quiz_data or self.current_question >= len(self.quiz_data):
            self.show_info("Quiz Complete", 
                         f"Quiz finished! Final score: {self.score}/{len(self.quiz_data)}")
            self.update_high_score()
            return

        question = self.quiz_data[self.current_question]
        self.question_label.config(text=question['question'])
        
        # Update options
        options = question['options']
        for i, (btn, option) in enumerate(zip(self.answer_buttons, options)):
            btn.config(text=f"{i+1}. {option}")
        
        # Generate and play audio for question
        self.generate_and_play_audio(question['question'])
        
        # Start auto-advance timer
        self.start_timer()

    def check_answer(self, choice_index):
        """Check if the selected answer is correct"""
        if not self.quiz_data or self.current_question >= len(self.quiz_data):
            return

        question = self.quiz_data[self.current_question]
        correct_answer = question['correct_answer']
        
        if choice_index == correct_answer:
            self.score += 1
            self.show_info("Correct!", "¡Muy bien! (Very good!)")
        else:
            correct_text = question['options'][correct_answer]
            self.show_info("Incorrect", 
                         f"The correct answer was: {correct_text}")
        
        self.score_label.config(
            text=f"Score: {self.score}/{self.current_question + 1}"
        )
        
        # Move to next question
        self.current_question += 1
        if self.current_question < len(self.quiz_data):
            self.display_question()
        else:
            self.show_info("Quiz Complete", 
                         f"Quiz finished! Final score: {self.score}/{len(self.quiz_data)}")
            self.update_high_score()

    def generate_and_play_audio(self, text):
        """Generate and play audio for the given text"""
        try:
            # Generate unique filename based on text
            filename = self.audio_dir / f"{hash(text)}.mp3"
            
            if not filename.exists():
                self.speaking_label.config(text="Generating audio...")
                tts = gTTS(text=text, lang='es', slow=False)
                tts.save(str(filename))
            
            # Play the audio
            self.speaking_label.config(text="Playing audio...")
            pygame.mixer.music.load(str(filename))
            pygame.mixer.music.play()
            
            # Clear speaking label after audio finishes
            def clear_speaking_label():
                if not pygame.mixer.music.get_busy():
                    self.speaking_label.config(text="")
                else:
                    self.root.after(100, clear_speaking_label)
            
            self.root.after(100, clear_speaking_label)
            
        except Exception as e:
            logging.error(f"Audio generation/playback error: {e}")
            self.speaking_label.config(text="Audio error")

    def replay_audio(self):
        """Replay the current question's audio"""
        if self.quiz_data and self.current_question < len(self.quiz_data):
            question = self.quiz_data[self.current_question]
            self.generate_and_play_audio(question['question'])

    def start_timer(self):
        """Start the auto-advance timer"""
        if hasattr(self, 'auto_advance_timer'):
            self.root.after_cancel(self.auto_advance_timer)
        
        self.remaining_time = self.auto_advance_time
        
        def update_timer():
            if self.remaining_time > 0:
                self.timer_label.config(
                    text=f"Next question in: {self.remaining_time} seconds"
                )
                self.remaining_time -= 1
                self.auto_advance_timer = self.root.after(1000, update_timer)
            else:
                self.timer_label.config(text="Time's up!")
                self.check_answer(-1)  # -1 indicates timeout
        
        update_timer()

    def exit_application(self):
        """Clean exit of the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to quit?"):
            self.save_high_score()
            self.root.quit()

if __name__ == "__main__":
    print("Starting Lovable Spanish Quiz...")
    print("Attempting to connect to backend at: http://127.0.0.1:5000")
    
    try:
        root = tk.Tk()
        app = SpanishQuizLovableApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application crashed: {e}")
        messagebox.showerror("Critical Error", 
                           "The application has encountered a critical error and needs to close.")
        sys.exit(1)
