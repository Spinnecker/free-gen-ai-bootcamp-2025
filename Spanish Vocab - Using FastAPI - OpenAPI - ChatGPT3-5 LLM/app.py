from flask import Flask, request, jsonify, send_from_directory
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='static')

SAMPLE_VOCABULARY = {
    "food": [
        {"spanish": "manzana", "english": "apple", "example": "Me gusta comer manzanas."},
        {"spanish": "pan", "english": "bread", "example": "El pan está fresco."}
    ],
    "animals": [
        {"spanish": "perro", "english": "dog", "example": "El perro es amigable."},
        {"spanish": "gato", "english": "cat", "example": "El gato duerme mucho."}
    ]
}

def generate_vocabulary(topic, word_count):
    try:
        if not openai.api_key:
            # Return sample data if no API key
            sample = SAMPLE_VOCABULARY.get(topic.lower(), SAMPLE_VOCABULARY["food"])
            return sample[:word_count]

        # Ensure we request more words than needed to account for parsing issues
        request_count = max(word_count + 2, 6)
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """You are a Spanish language teacher. You must generate vocabulary words that are STRICTLY and DIRECTLY related to the given topic.

                Rules:
                1. EVERY word must be clearly and directly related to the topic
                2. NO general or unrelated words
                3. Use common, practical words that beginners would need
                4. Format each word exactly as shown below, with no deviations:

                Spanish: [specific word]
                English: [direct translation]
                Example: [simple sentence using the word]

                For example, if topic is "food":
                - Include: foods, ingredients, cooking verbs, kitchen items
                - Exclude: general verbs, time words, or unrelated nouns"""
            }, {
                "role": "user",
                "content": f"""Generate exactly {request_count} Spanish vocabulary words that are SPECIFICALLY about: {topic}.
                
                Requirements:
                1. Every word MUST be directly related to '{topic}'
                2. Use beginner-friendly, common words
                3. Follow the exact format:
                Spanish: [word]
                English: [translation]
                Example: [sentence]"""
            }],
            temperature=0.7,
            max_tokens=800  # Increased to ensure we get full response
        )

        # Parse the response
        content = response.choices[0].message['content']
        lines = content.strip().split("\n")
        words = []

        current_word = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "Spanish:" in line:
                if current_word:
                    words.append(current_word)
                    current_word = {}
                current_word["spanish"] = line.split("Spanish:")[1].strip()
            elif "English:" in line:
                current_word["english"] = line.split("English:")[1].strip()
            elif "Example:" in line:
                current_word["example"] = line.split("Example:")[1].strip()

        if current_word:
            words.append(current_word)

        return words[:word_count]

    except Exception as e:
        print(f"Error generating vocabulary: {str(e)}")
        # Return sample data as fallback
        sample = SAMPLE_VOCABULARY.get(topic.lower(), SAMPLE_VOCABULARY["food"])
        return sample[:word_count]

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/generate', methods=['POST'])
def generate_vocabulary_words():
    data = request.get_json()
    topic = data.get('topic')
    word_count = data.get('word_count', 5)

    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    if not isinstance(word_count, int) or word_count < 1 or word_count > 10:
        return jsonify({"error": "Word count must be between 1 and 10"}), 400

    words = generate_vocabulary(topic, word_count)
    return jsonify({"words": words})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
