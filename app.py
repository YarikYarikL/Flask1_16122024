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
    data = request.json
   
    try:
        quote = QuoteModel(**data)
        db.session.add(quote)
        db.session.commit()

    except TypeError:
        return jsonify(error=(
                       "Invalid data. Required author & text"
                       f"Received: {', '.join(data.keys())}"
                      )),400
    except Exception as e:
        abort(503, f"database error {str(e)}")

    return jsonify(quote.to_dict()), 201




@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    quote = db.get_or_404(QuoteModel, quote_id)
    db.session.delete(quote)
    try:
        db.session.commit()
        return jsonify(success = f"Quote with {quote_id} is deleted."), 200
    except Exception as e:
        db.session.rollback()
        abort(503, f"database error {str(e)}")



@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json

    allowed_keys = {"author", "text"}
    if not set(new_data.keys()).issubset(allowed_keys):
        return jsonify(error=f"Invalid fields for update: {', '.join(set(new_data.keys())-allowed_keys)}"), 400
    
    quote_db = db.get_or_404(QuoteModel, quote_id)
    try:
        for key, value in new_data.items():
            if not hasattr(quote_db, key):
                raise Exception(f"Invalid {key = }.")
            setattr(quote_db,key,value)
        db.session.commit()
        return jsonify(quote_db.to_dict()),200
    except Exception as e:
        abort(400,f"error: {str(e)}")


@app.route("/quotes/filter")
def filter_quote():
    
    return jsonify(choice(quotes)), 200





@app.route("/quotes/random", methods =["GET"])
def random_quote() -> dict:
    return jsonify(choice(quotes)), 200


if __name__ == "__main__":
    app.run(debug=True)