import tkinter as tk
from tkinter import messagebox
import random

# Define the question, correct answer, and distractors
question = "What is the Spanish word for 'house'?"
answers = [
    {"text": "la casa", "correct": True},
    {"text": "el coche", "correct": False},
    {"text": "la escuela", "correct": False},
    {"text": "el parque", "correct": False}
]

# Shuffle the answers
random.shuffle(answers)

# Function to check the selected answer
def check_answer(selected_index):
    if answers[selected_index]["correct"]:
        messagebox.showinfo("Correct!", "¡Excelente! Your answer is correct.")
        root.quit()  # Exit the GUI when the correct answer is selected
    else:
        messagebox.showerror("Incorrect", "Lo siento, that is incorrect. Try again!")

# Create the main window
root = tk.Tk()
root.title("Spanish Quiz")

# Display the question
question_label = tk.Label(root, text=question, font=("Arial", 14))
question_label.pack(pady=10)

# Create answer buttons
for i, answer in enumerate(answers):
    btn = tk.Button(root, text=answer["text"], font=("Arial", 12),
                    command=lambda i=i: check_answer(i))
    btn.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
