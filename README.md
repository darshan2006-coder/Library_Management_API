# Book Management API

A simple RESTful API built using Flask and SQLite for managing books.

## Technologies Used

* Python
* Flask
* Flask-SQLAlchemy
* SQLite
* Postman

## Features

* Get all books
* Get a book by ID
* Add a new book
* Update a book
* Delete a book
* Validation and error handling

## API Endpoints

### Get All Books

GET /books

### Get Book By ID

GET /books/<id>

### Add Book

POST /books

### Update Book

PUT /books/<id>

### Delete Book

DELETE /books/<id>

## Run Project

Create virtual environment:

python -m venv venv

Activate environment:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run application:

python app.py

Server:

http://127.0.0.1:5000
