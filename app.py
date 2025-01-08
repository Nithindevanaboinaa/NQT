from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# MongoDB Connection
app.secret_key = 'your_secret_key'

MONGO_URI = "mongodb+srv://nithind:nithind@cluster0.zhl2w.mongodb.net/progress_tracker?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database('progress_tracker')

@app.route('/')
def home():
  return render_template('home.html')
@app.route('/array')
def array():
  return render_template('array.html')
@app.route('/admin')
def admin():
  return render_template('adminpage.html')
@app.route('/string')
def string():
  return render_template('string.html')
@app.route('/numbers')
def numbers():
  return render_template('numbers.html')
@app.route('/numbersystem')
def numbersystem():
  return render_template('numbersystem.html')
@app.route('/sorting')
def sorting():
  return render_template('sorting.html')

@app.route('/add_question', methods=['POST'])
def add_question():
    """Add a question to a specific section."""
    data = request.json
    page = data['page']
    question = {
        "question": data['question'],
        "url": data['url'],
        "done": False
    }
    db[page].insert_one(question)
    return jsonify({"message": "Question added successfully!"}), 201

@app.route('/get_questions/<page>', methods=['GET'])
def get_questions(page):
    """Retrieve all questions for a specific section."""
    questions = list(db[page].find({}, {"_id": 0}))
    return jsonify(questions), 200

@app.route('/update_done', methods=['POST'])
def update_done():
    """Update the completion status of a specific question."""
    data = request.json
    page = data['page']
    question = data['question']
    done = data['done']
    result = db[page].update_one({"question": question}, {"$set": {"done": done}})
    if result.matched_count == 0:
        return jsonify({"message": f"Question '{question}' not found in {page}."}), 404
    return jsonify({"message": "Progress updated!"}), 200

@app.route('/reset_progress/<page>', methods=['POST'])
def reset_progress(page):
    """Reset the completion status of all questions in a section."""
    db[page].update_many({}, {"$set": {"done": False}})
    return jsonify({"message": f"Progress reset for {page}!"}), 200

@app.route('/get_progress', methods=['GET'])
def get_progress():
    """Calculate the overall progress for all sections."""
    sections = ["Arrays", "Strings", "NumberSystem", "Numbers", "Sorting"]
    progress = {}

    for section in sections:
        tasks = list(db[section].find({}))
        if not tasks:
            progress[section.lower()] = 0
        else:
            completed = sum(1 for task in tasks if task.get("done", False))
            progress[section.lower()] = round((completed / len(tasks)) * 100)

    return jsonify(progress), 200

@app.route('/delete_question', methods=['POST'])
def delete_question():
    """Delete a specific question from a section."""
    data = request.json
    page = data['page']
    question_name = data['question']
    result = db[page].delete_one({"question": question_name})
    if result.deleted_count == 0:
        return jsonify({"message": f"Question '{question_name}' not found in {page}."}), 404
    return jsonify({"message": f"Question '{question_name}' deleted from {page}!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
