from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)

# Home Route
@app.route('/')
def home():
    return "Book Management API is Running!"

# Get All Books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()

    result = []

    for book in books:
        result.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.year
        })

    return jsonify(result)

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json(silent=True)

    if not data :
        return jsonify({
            "message": "Title, author and year are required"
        }), 400

    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data['year']
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        "message": "Book added successfully"
    }), 201

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "message": "Book not found"
        }), 404

    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "year": book.year
    })

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "message": "Book not found"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Title, author and year are required"
        }), 400

    if not data.get('title') or not data.get('author') or not data.get('year'):
        return jsonify({
            "message": "Title, author and year are required"
        }), 400

    book.title = data['title']
    book.author = data['author']
    book.year = data['year']

    db.session.commit()

    return jsonify({
        "message": "Book updated successfully"
    })

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "message": "Book not found"
        }), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        "message": "Book deleted successfully"
    })

# Create Database Tables
with app.app_context():
    db.create_all()

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)








