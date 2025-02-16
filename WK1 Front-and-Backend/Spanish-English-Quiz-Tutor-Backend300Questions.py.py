import json
import random

# Extended list of Spanish words (English -> Spanish)
word_pairs = [
    ("house", "la casa"), ("apple", "la manzana"), ("dog", "el perro"), ("car", "el coche"),
    ("school", "la escuela"), ("park", "el parque"), ("banana", "el plátano"), ("bird", "el pájaro"),
    ("fish", "el pez"), ("table", "la mesa"), ("computer", "la computadora"), ("chair", "la silla"),
    ("water", "el agua"), ("cat", "el gato"), ("window", "la ventana"), ("door", "la puerta"),
    ("tree", "el árbol"), ("sun", "el sol"), ("moon", "la luna"), ("star", "la estrella"),
    ("ocean", "el océano"), ("river", "el río"), ("mountain", "la montaña"), ("flower", "la flor"),
    ("food", "la comida"), ("book", "el libro"), ("pencil", "el lápiz"), ("paper", "el papel"),
    ("bed", "la cama"), ("shirt", "la camisa"), ("pants", "los pantalones"), ("shoes", "los zapatos"),
    ("hat", "el sombrero"), ("clock", "el reloj"), ("bottle", "la botella"), ("music", "la música"),
    ("doctor", "el doctor"), ("teacher", "el maestro"), ("student", "el estudiante"), ("friend", "el amigo"),
    ("family", "la familia"), ("city", "la ciudad"), ("country", "el país"), ("street", "la calle"),
    ("market", "el mercado"), ("hospital", "el hospital"), ("bank", "el banco"), ("hotel", "el hotel"),
    ("airport", "el aeropuerto"), ("restaurant", "el restaurante"), ("kitchen", "la cocina"),
    ("bathroom", "el baño"), ("bedroom", "el dormitorio"), ("living room", "la sala"),
    ("garden", "el jardín"), ("bus", "el autobús"), ("train", "el tren"), ("plane", "el avión"),
    ("bike", "la bicicleta"), ("boat", "el barco"), ("job", "el trabajo"), ("money", "el dinero"),
    ("fire", "el fuego"), ("ice", "el hielo"), ("wind", "el viento"), ("rain", "la lluvia"),
    ("snow", "la nieve"), ("cloud", "la nube"), ("salt", "la sal"), ("sugar", "el azúcar"),
    ("milk", "la leche"), ("coffee", "el café"), ("tea", "el té"), ("juice", "el jugo"),
    ("beer", "la cerveza"), ("wine", "el vino"), ("chicken", "el pollo"), ("beef", "la carne de res"),
    ("fish (food)", "el pescado"), ("vegetable", "la verdura"), ("fruit", "la fruta"),
    ("bread", "el pan"), ("cheese", "el queso"), ("egg", "el huevo"), ("butter", "la mantequilla")
]

# Function to generate distractors (incorrect answers)
def generate_distractors(correct_answer, all_answers, num_distractors=3):
    distractors = random.sample([word for word in all_answers if word != correct_answer], num_distractors)
    return distractors

# Function to auto-generate quiz questions
def generate_quiz(num_questions=300):
    quiz_data = []
    
    for _ in range(num_questions):
        english_word, correct_answer = random.choice(word_pairs)
        distractors = generate_distractors(correct_answer, [pair[1] for pair in word_pairs])
        
        question = f"What is the Spanish word for '{english_word}'?"
        answers = [
            {"text": correct_answer, "correct": True}
        ] + [{"text": d, "correct": False} for d in distractors]
        
        random.shuffle(answers)  # Shuffle answer order

        quiz_data.append({"question": question, "answers": answers})

    return quiz_data

# Generate 300 questions and save them to a JSON file
quiz_questions = generate_quiz(300)
with open("quiz_questions.json", "w") as f:
    json.dump(quiz_questions, f, indent=4)

print("300 quiz questions have been generated and saved to quiz_questions.json!")
