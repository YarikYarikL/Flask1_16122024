from flask import Flask, abort, g, jsonify, Response, request
from typing import Any
from markupsafe import escape
from random import choice, random
from pathlib import Path
from werkzeug.exceptions import HTTPException
import sqlite3

#import from SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = False


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text):
        self.author = author
        self.text  = text

    def __repr__(self):
        return f"QuoteModel({self.id, self.author})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
        }

@app.errorhandler(HTTPException)
def handle_exeption(e):
    """функция для перехвата HTTP ошибок и возврата в виде JSON"""
    return jsonify({"error": str(e)}), e.code


@app.route("/quotes")
def get_quotes() -> list[dict[str: Any]]:
    """ функция преобразует список словарей в массив объектов json"""
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    quote_db = db.get_or_404(QuoteModel, quote_id)
    return jsonify(quote_db.to_dict()), 200


@app.get("/quotes/count")
def quote_count():
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count=count),200



@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    delete_sql = "DELETE FROM quotes WHERE id = ?"
    params = (quote_id,)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(delete_sql, params)
    rows = cursor.rowcount
    if rows:
        connection.commit()
        return jsonify(message = f"Quote with {quote_id} is deleted."), 200
    abort(404, f"Error - no quote with id {quote_id}.")



@app.route("/quotes", methods=['POST'])
def create_quote():
    """ Create a new quote in the database """
    new_quote = request.json
    if not new_quote or 'author' not in new_quote or 'text' not in new_quote:
        return jsonify(error="Missing required fields: author and text"), 400

    rating = new_quote.get("rating", 1)
    if rating not in range(1, 6):
        rating = 1
    new_quote["rating"] = rating

    insert_quote = "INSERT INTO quotes (author, text, rating) VALUES (?, ?, ?)"
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(insert_quote, tuple(new_quote.values()))
    new_quote_id = cursor.lastrowid
    try:
        connection.commit()
        cursor.close()
    except Exception as e:
        abort(503,f"error: {str(e)}")
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201



@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json

    allowed_keys = {"author", "text", "rating"}
    if not set(new_data.keys()).issubset(allowed_keys):
        return jsonify(error="Invalid fields for update"), 400
   
    if "rating" in new_data and new_data["rating"] not in range(1, 6):
        return jsonify(error="Rating must be between 1 and 5"), 400

    connection = get_db()
    cursor = connection.cursor()
  
    update_values = list(new_data.values())
    update_fields = [f"{key} =?" for key in new_data]
    
    if not update_fields:
        return jsonify(error="No valid update fields provided"), 400

    update_values.append(quote_id)
    update_query = f"UPDATE quotes SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(update_query, update_values)
    connection.commit()
 
    if cursor.rowcount == 0:
        return jsonify(error=f"Quote with id={quote_id} not found"), 404
    
    responce, status_code = get_quote(quote_id)
    if status_code == 200:
        return responce, 200
    abort(404, f"Quote with id ={quote_id} not found.")




# #homework
# @app.route("/quotes/filter")
# def filter_quotes():
#     new_data = request.args.items()



@app.route("/quotes/random", methods =["GET"])
def random_quote() -> dict:
    return jsonify(choice(quotes)), 200


if __name__ == "__main__":
    app.run(debug=True)