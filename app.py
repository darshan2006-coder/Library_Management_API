from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from datetime import date, timedelta

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)


# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    returned = db.Column(db.Boolean, default=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', backref='borrow_records')


# Home Route
@app.route('/')
def home():
    return jsonify({
        "success": True,
        "message": "Book Management API is Running!"
    })


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
            "year": book.year,
            "genre": book.genre,
            "isbn": book.isbn,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies
        })

    return jsonify({
    "success": True,
    "count" : len(result),
    "books": result
    }
), 200


# Add Book
@app.route('/books', methods=['POST'])
def add_book():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    title = data.get("title")
    author = data.get("author")
    genre = data.get("genre")
    isbn = data.get("isbn")
    year = data.get("year")
    total_copies = data.get("total_copies")

    if not all([title, author, genre, isbn]):
        return jsonify({
            "success": False,
            "message": "Title, author, genre and ISBN are required"
        }), 400

    if year is None or total_copies is None:
        return jsonify({
            "success": False,
            "message": "Year and Total Copies are required"
        }), 400

    if not isinstance(year, int):
        return jsonify({
            "success": False,
            "message": "Year must be an integer"
        }), 400

    if not isinstance(total_copies, int):
        return jsonify({
            "success": False,
            "message": "Total Copies must be an integer"
        }), 400

    if year <= 0:
        return jsonify({
            "success": False,
            "message": "Invalid year"
        }), 400

    if total_copies <= 0:
        return jsonify({
            "success": False,
            "message": "Total Copies must be greater than 0"
        }), 400

    existing_book = Book.query.filter_by(isbn=isbn).first()

    if existing_book:
        return jsonify({
            "success": False,
            "message": "Book with this ISBN already exists"
        }), 409

    new_book = Book(
        title=title,
        author=author,
        genre=genre,
        isbn=isbn,
        year=year,
        total_copies=total_copies,
        available_copies=total_copies
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book added successfully",
        "book": {
            "id": new_book.id,
            "title": new_book.title,
            "author": new_book.author,
            "genre": new_book.genre,
            "isbn": new_book.isbn,
            "year": new_book.year,
            "total_copies": new_book.total_copies,
            "available_copies": new_book.available_copies
        }
    }), 201

@app.route('/borrow', methods=['POST'])
def borrow_book():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    borrower_name = data.get("borrower_name")
    borrower_email = data.get("borrower_email")
    book_id = data.get("book_id")

    if not borrower_name or not borrower_email or not book_id:
        return jsonify({
            "success": False,
            "message": "Borrower Name, Borrower Email and Book ID are required"
        }), 400

    book = Book.query.get(book_id)

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    if book.available_copies <= 0:
        return jsonify({
            "success": False,
            "message": "Book is currently unavailable"
        }), 400

    borrow = BorrowRecord(
        borrower_name=borrower_name,
        borrower_email=borrower_email,
        borrow_date=date.today(),
        due_date=date.today() + timedelta(days=14),
        book_id=book.id
    )

    book.available_copies -= 1

    db.session.add(borrow)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book borrowed successfully",
        "borrow": {
            "borrow_id": borrow.id,
            "book": book.title,
            "borrower_name": borrow.borrower_name,
            "borrower_email": borrow.borrower_email,
            "borrow_date": str(borrow.borrow_date),
            "due_date": str(borrow.due_date)
        }
    }), 201

@app.route('/return/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):

    borrow = BorrowRecord.query.get(borrow_id)

    if not borrow:
        return jsonify({
            "success": False,
            "message": "Borrow record not found"
        }), 404

    if borrow.returned:
        return jsonify({
            "success": False,
            "message": "Book already returned"
        }), 400

    book = Book.query.get(borrow.book_id)

    borrow.returned = True
    borrow.return_date = date.today()

    book.available_copies += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book returned successfully",
        "return": {
            "borrow_id": borrow.id,
            "book": book.title,
            "returned_on": str(borrow.return_date),
            "available_copies": book.available_copies
        }
    }), 200

@app.route('/borrow-history', methods=['GET'])
def borrow_history():

    records = BorrowRecord.query.all()

    history = []

    for record in records:

        history.append({
            "borrow_id": record.id,
            "book": record.book.title,
            "borrower_name": record.borrower_name,
            "borrower_email": record.borrower_email,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date),
            "returned": record.returned,
            "return_date": str(record.return_date) if record.return_date else None
        })

    return jsonify({
        "success": True,
        "count": len(history),
        "history": history
    }), 200

@app.route('/overdue', methods=['GET'])
def overdue_books():

    today = date.today()

    overdue = BorrowRecord.query.filter(
        BorrowRecord.returned == False,
        BorrowRecord.due_date < today
    ).all()

    books = []

    for record in overdue:

        books.append({
            "borrow_id": record.id,
            "book": record.book.title,
            "borrower_name": record.borrower_name,
            "borrower_email": record.borrower_email,
            "borrow_date": str(record.borrow_date),
            "due_date": str(record.due_date)
        })

    return jsonify({
        "success": True,
        "count": len(books),
        "overdue_books": books
    }), 200

@app.route('/fine/<int:borrow_id>', methods=['GET'])
def calculate_fine(borrow_id):

    borrow = BorrowRecord.query.get(borrow_id)

    if not borrow:
        return jsonify({
            "success": False,
            "message": "Borrow record not found"
        }), 404

    if borrow.returned:
        return jsonify({
            "success": True,
            "message": "Book already returned",
            "fine": 0
        }), 200

    today = date.today()

    if today <= borrow.due_date:
        return jsonify({
            "success": True,
            "late_days": 0,
            "fine": 0
        }), 200

    late_days = (today - borrow.due_date).days

    fine = late_days * 10

    return jsonify({
        "success": True,
        "borrow_id": borrow.id,
        "book": borrow.book.title,
        "borrower": borrow.borrower_name,
        "late_days": late_days,
        "fine": fine
    }), 200

# Get Single Book
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    return jsonify({
        "success": True,
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.year,
        }
    }), 200


# Update Book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    title = data.get("title")
    author = data.get("author")
    genre = data.get("genre")
    isbn = data.get("isbn")
    year = data.get("year")
    total_copies = data.get("total_copies")

    if not all([title, author, genre, isbn]):
        return jsonify({
            "success": False,
            "message": "Title, Author, Genre and ISBN are required"
        }), 400

    if year is None or total_copies is None:
        return jsonify({
            "success": False,
            "message": "Year and Total Copies are required"
        }), 400

    if not isinstance(year, int):
        return jsonify({
            "success": False,
            "message": "Year must be an integer"
        }), 400

    if not isinstance(total_copies, int):
        return jsonify({
            "success": False,
            "message": "Total Copies must be an integer"
        }), 400

    if total_copies <= 0:
        return jsonify({
            "success": False,
            "message": "Total Copies must be greater than 0"
        }), 400

    existing_book = Book.query.filter(
        Book.isbn == isbn,
        Book.id != id
    ).first()

    if existing_book:
        return jsonify({
            "success": False,
            "message": "Another book with this ISBN already exists"
        }), 409

    borrowed = book.total_copies - book.available_copies

    if total_copies < borrowed:
        return jsonify({
            "success": False,
            "message": f"Cannot reduce total copies below borrowed copies ({borrowed})"
        }), 400

    book.title = title
    book.author = author
    book.genre = genre
    book.isbn = isbn
    book.year = year
    book.total_copies = total_copies
    book.available_copies = total_copies - borrowed

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book updated successfully",
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "isbn": book.isbn,
            "year": book.year,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies
        }
    }), 200


# Delete Book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):

    book = Book.query.get(id)

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book deleted successfully"
    }), 200


# Create Database Tables
with app.app_context():
    db.create_all()


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)