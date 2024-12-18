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


@app.route("/quotes", methods=['POST'])
def create_quote():
    if not request.json or 'author' not in request.json or 'text' not in request.json:
        return jsonify(error="Missing required fields: author and text"), 400
    quote_db = QuoteModel(author=request.json.get("author"),text=request.json.get("text"))
    db.session.add(quote_db)
    db.session.commit()
    return jsonify(new_quote = request.json),200



@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    quote_for_delete = db.get_or_404(QuoteModel, quote_id)
    if quote_for_delete:
        db.session.delete(quote_for_delete)
        db.session.commit()
        return jsonify(message = f"Quote with {quote_id} is deleted."), 200
    abort(404, f"Error - no quote with id {quote_id}.")


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json

    allowed_keys = {"author", "text", "rating"}
    if not set(new_data.keys()).issubset(allowed_keys):
        return jsonify(error="Invalid fields for update"), 400
    
    quote_db = db.get_or_404(QuoteModel, quote_id)
    if new_data.get("text"):
        quote_db.text = new_data.get("text")
    if new_data.get("author"):
        quote_db.author = new_data.get("author")
    db.session.commit()
    return f"Quote with id {quote_id} is changed"





@app.route("/quotes/random", methods =["GET"])
def random_quote() -> dict:
    return jsonify(choice(quotes)), 200


if __name__ == "__main__":
    app.run(debug=True)