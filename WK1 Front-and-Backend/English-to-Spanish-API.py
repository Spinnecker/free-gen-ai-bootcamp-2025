from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import random

app = Flask(__name__)
# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vocab.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Vocabulary model
class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), nullable=False)
    spanish = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'english': self.english,
            'spanish': self.spanish
        }

# Create tables
with app.app_context():
    db.create_all()
    
    # Add some initial vocabulary if the database is empty
    if not Vocabulary.query.first():
        initial_vocab = [
            {'english': 'hello', 'spanish': 'hola'},
            {'english': 'goodbye', 'spanish': 'adiós'},
            {'english': 'thank you', 'spanish': 'gracias'},
            {'english': 'please', 'spanish': 'por favor'},
            {'english': 'water', 'spanish': 'agua'}
        ]
        for vocab in initial_vocab:
            db.session.add(Vocabulary(**vocab))
        db.session.commit()

@app.route('/vocab', methods=['GET'])
def get_all_vocab():
    vocab = Vocabulary.query.all()
    return jsonify([v.to_dict() for v in vocab])

@app.route('/vocab', methods=['POST'])
def add_vocab():
    data = request.get_json()
    if not data or 'english' not in data or 'spanish' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_vocab = Vocabulary(english=data['english'], spanish=data['spanish'])
    db.session.add(new_vocab)
    db.session.commit()
    return jsonify(new_vocab.to_dict()), 201

@app.route('/quiz', methods=['GET'])
def generate_quiz():
    count = request.args.get('count', default=5, type=int)
    vocab = Vocabulary.query.all()
    
    if len(vocab) < count:
        count = len(vocab)
    
    quiz_items = random.sample(vocab, count)
    quiz = [{'english': item.english, 'id': item.id} for item in quiz_items]
    return jsonify(quiz)

@app.route('/check/<int:vocab_id>', methods=['POST'])
def check_answer(vocab_id):
    data = request.get_json()
    if not data or 'answer' not in data:
        return jsonify({'error': 'No answer provided'}), 400
    
    vocab = Vocabulary.query.get_or_404(vocab_id)
    is_correct = data['answer'].lower().strip() == vocab.spanish.lower()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': vocab.spanish
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
