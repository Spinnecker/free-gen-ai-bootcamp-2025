from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Spanish words organized by categories
spanish_words = {
    "household": [
        {"english": "house", "spanish": "la casa"},
        {"english": "table", "spanish": "la mesa"},
        {"english": "computer", "spanish": "la computadora"},
        {"english": "chair", "spanish": "la silla"},
        {"english": "window", "spanish": "la ventana"},
        {"english": "door", "spanish": "la puerta"},
        {"english": "bed", "spanish": "la cama"},
        {"english": "kitchen", "spanish": "la cocina"},
        {"english": "bathroom", "spanish": "el baño"},
        {"english": "bedroom", "spanish": "el dormitorio"}
    ],
    "food": [
        {"english": "apple", "spanish": "la manzana"},
        {"english": "banana", "spanish": "el plátano"},
        {"english": "food", "spanish": "la comida"},
        {"english": "salt", "spanish": "la sal"},
        {"english": "sugar", "spanish": "el azúcar"},
        {"english": "milk", "spanish": "la leche"},
        {"english": "coffee", "spanish": "el café"},
        {"english": "chicken", "spanish": "el pollo"},
        {"english": "bread", "spanish": "el pan"},
        {"english": "cheese", "spanish": "el queso"}
    ],
    "animals": [
        {"english": "dog", "spanish": "el perro"},
        {"english": "bird", "spanish": "el pájaro"},
        {"english": "fish", "spanish": "el pez"},
        {"english": "cat", "spanish": "el gato"}
    ],
    "transportation": [
        {"english": "car", "spanish": "el coche"},
        {"english": "bus", "spanish": "el autobús"},
        {"english": "train", "spanish": "el tren"},
        {"english": "plane", "spanish": "el avión"},
        {"english": "bike", "spanish": "la bicicleta"},
        {"english": "boat", "spanish": "el barco"}
    ],
    "nature": [
        {"english": "tree", "spanish": "el árbol"},
        {"english": "sun", "spanish": "el sol"},
        {"english": "moon", "spanish": "la luna"},
        {"english": "star", "spanish": "la estrella"},
        {"english": "ocean", "spanish": "el océano"},
        {"english": "mountain", "spanish": "la montaña"},
        {"english": "flower", "spanish": "la flor"}
    ]
}

# Create a list of all words for tracking usage
all_words = [(cat, word) for cat, words in spanish_words.items() for word in words]
used_words = deque(maxlen=200)  # Keep track of last 200 used words

def get_unused_word():
    """Get a word that hasn't been used in the last 200 questions"""
    available_words = [(cat, word) for cat, word in all_words if (cat, word) not in used_words]
    
    # If all words have been used, return a random word
    if not available_words:
        return random.choice(all_words)
    
    # Return a random unused word
    return random.choice(available_words)

@app.route('/api/words/random', methods=['GET'])
def get_random_word():
    category, word = get_unused_word()
    used_words.append((category, word))
    return jsonify({
        "category": category,
        "english": word["english"],
        "spanish": word["spanish"]
    })

@app.route('/api/words/category/<category>', methods=['GET'])
def get_words_by_category(category):
    if category in spanish_words:
        return jsonify({
            "category": category,
            "words": spanish_words[category]
        })
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({
        "categories": list(spanish_words.keys())
    })

@app.route('/api/quiz/generate', methods=['GET'])
def generate_quiz():
    logging.info("Received request for quiz generation")  # Debug log
    try:
        questions = []
        # Generate 5 random questions
        for _ in range(5):
            # Get an unused word
            category, correct_word = get_unused_word()
            used_words.append((category, correct_word))
            
            # Get distractors from any category, avoiding the correct answer
            all_spanish_words = [word["spanish"] for cat, words in spanish_words.items() for word in words]
            all_options = [w for w in all_spanish_words if w != correct_word["spanish"]]
            # Get 3 random distractors
            distractors = random.sample(all_options, 3)
            
            # Create options list and randomly insert the correct answer
            options = distractors.copy()
            correct_position = random.randint(0, 3)
            options.insert(correct_position, correct_word["spanish"])
            
            questions.append({
                "question": f"What is the Spanish word for '{correct_word['english']}'?",
                "options": options,
                "correct_answer": correct_position
            })
        
        response = {"questions": questions}
        logging.info(f"Generated quiz with {len(questions)} questions")  # Debug log
        return jsonify(response)
    except Exception as e:
        error_msg = f"Error generating quiz: {str(e)}"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "endpoints": [
            "/api/quiz/generate",
            "/api/words/random",
            "/api/words/category/<category>",
            "/api/categories"
        ]
    })

# Print all registered routes on startup
def list_routes():
    logging.info("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        logging.info(f"{rule.endpoint}: {rule.methods} {rule.rule}")

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server will be available at: http://127.0.0.1:5000")
    print(f"Total number of words available: {len(all_words)}")
    list_routes()  # Print registered routes
    app.run(host='127.0.0.1', port=5000, debug=True)
