import tkinter as tk
from tkinter import messagebox, ttk
import random
import requests
import json
import time

class SpanishQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spanish Quiz")
        self.root.geometry("400x500")
        
        # Create a style for the buttons
        style = ttk.Style()
        style.configure("Quiz.TButton", padding=10, font=("Arial", 12))
        
        self.current_question = 0
        self.score = 0
        self.quiz_data = None
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create status label
        self.status_label = ttk.Label(self.main_frame, text="Status: Connecting to server...", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, pady=5)
        
        # Create score label
        self.score_label = ttk.Label(self.main_frame, text="Score: 0/0", font=("Arial", 12))
        self.score_label.grid(row=1, column=0, pady=5)
        
        # Create category label
        self.category_label = ttk.Label(self.main_frame, text="Category: ", font=("Arial", 12))
        self.category_label.grid(row=2, column=0, pady=5)
        
        # Create question label
        self.question_label = ttk.Label(self.main_frame, text="", font=("Arial", 14), wraplength=350)
        self.question_label.grid(row=3, column=0, pady=20)
        
        # Create frame for answer buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, pady=10)
        
        # Create answer buttons
        self.answer_buttons = []
        for i in range(4):
            btn = ttk.Button(self.button_frame, text="", style="Quiz.TButton",
                           command=lambda i=i: self.check_answer(i))
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            self.answer_buttons.append(btn)
            
        # Create next question button
        self.next_button = ttk.Button(self.main_frame, text="Next Question", 
                                    command=self.next_question, style="Quiz.TButton")
        self.next_button.grid(row=5, column=0, pady=20)
        self.next_button.grid_remove()  # Hide initially
        
        # Create new quiz button
        self.new_quiz_button = ttk.Button(self.main_frame, text="Start New Quiz",
                                        command=self.start_new_quiz, style="Quiz.TButton")
        self.new_quiz_button.grid(row=6, column=0, pady=10)
        
        # Create retry connection button
        self.retry_button = ttk.Button(self.main_frame, text="Retry Connection",
                                     command=self.start_new_quiz, style="Quiz.TButton")
        self.retry_button.grid(row=7, column=0, pady=10)
        self.retry_button.grid_remove()  # Hide initially
        
        # Create exit button
        exit_style = ttk.Style()
        exit_style.configure("Exit.TButton", padding=10, font=("Arial", 12), foreground="red")
        self.exit_button = ttk.Button(self.main_frame, text="Exit Quiz",
                                    command=self.exit_application, style="Exit.TButton")
        self.exit_button.grid(row=8, column=0, pady=10)
        
        # Start the first quiz after a short delay
        self.root.after(1000, self.start_new_quiz)
        
    def fetch_quiz_data(self):
        self.status_label.config(text="Status: Connecting to server...")
        try:
            print("Attempting to connect to server at http://127.0.0.1:5000/api/quiz/generate")
            response = requests.get('http://127.0.0.1:5000/api/quiz/generate', timeout=5)
            if response.status_code == 200:
                self.status_label.config(text="Status: Connected")
                self.retry_button.grid_remove()
                return response.json()['quiz']
            else:
                error_msg = f"Server error: {response.status_code}"
                print(error_msg)
                self.status_label.config(text=f"Status: {error_msg}")
                messagebox.showerror("Error", "Failed to fetch quiz data from the server")
                self.retry_button.grid()
                return None
        except requests.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            print(error_msg)
            self.status_label.config(text=f"Status: {error_msg}")
            messagebox.showerror("Error", "Failed to connect to the server. Is the backend running?")
            self.retry_button.grid()
            return None
    
    def start_new_quiz(self):
        self.quiz_data = self.fetch_quiz_data()
        if self.quiz_data:
            self.current_question = 0
            self.score = 0
            self.update_score_label()
            self.show_question()
            self.new_quiz_button.grid_remove()  # Hide new quiz button
        else:
            self.question_label.config(text="Error loading quiz. Please check if the backend server is running and click 'Retry Connection'.")
            for btn in self.answer_buttons:
                btn.config(state='disabled')
    
    def show_question(self):
        if not self.quiz_data or self.current_question >= len(self.quiz_data):
            return
        
        question_data = self.quiz_data[self.current_question]
        self.category_label.config(text=f"Category: {question_data['category'].title()}")
        self.question_label.config(text=question_data['question'])
        
        # Update answer buttons
        for i, answer in enumerate(question_data['answers']):
            self.answer_buttons[i].config(text=answer['text'], state='normal')
        
        self.next_button.grid_remove()  # Hide next button
    
    def check_answer(self, selected_index):
        question_data = self.quiz_data[self.current_question]
        correct = question_data['answers'][selected_index]['correct']
        
        # Disable all buttons to prevent multiple answers
        for btn in self.answer_buttons:
            btn.config(state='disabled')
        
        if correct:
            self.score += 1
            messagebox.showinfo("¡Correcto!", "¡Excelente! Your answer is correct.")
        else:
            correct_answer = next(ans['text'] for ans in question_data['answers'] if ans['correct'])
            messagebox.showerror("Incorrecto", f"Lo siento, that is incorrect.\nThe correct answer is: {correct_answer}")
        
        self.update_score_label()
        
        # Show next button or finish quiz
        if self.current_question < len(self.quiz_data) - 1:
            self.next_button.grid()
        else:
            self.finish_quiz()
    
    def next_question(self):
        self.current_question += 1
        self.show_question()
    
    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score}/{self.current_question + 1}")
    
    def finish_quiz(self):
        final_score = f"Final Score: {self.score}/{len(self.quiz_data)}"
        percentage = (self.score / len(self.quiz_data)) * 100
        message = f"{final_score}\n{percentage:.1f}%"
        
        if percentage >= 80:
            message += "\n¡Excelente! Great job!"
        elif percentage >= 60:
            message += "\n¡Bien! Keep practicing!"
        else:
            message += "\n¡Sigue practicando! Keep studying!"
        
        messagebox.showinfo("Quiz Complete", message)
        self.new_quiz_button.grid()  # Show new quiz button

    def exit_application(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the Spanish Quiz?"):
            self.root.quit()

if __name__ == "__main__":
    print("Starting Spanish Quiz Frontend...")
    print("Attempting to connect to backend at: http://127.0.0.1:5000")
    root = tk.Tk()
    app = SpanishQuizApp(root)
    root.mainloop()
