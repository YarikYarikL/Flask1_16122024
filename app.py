from flask import Flask, jsonify, Response, request
from typing import Any
from markupsafe import escape
from random import choice, random


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


about_me = {
"name": "Евгений",
"surname": "Юрченко",
"email": "eyurchenko@specialist.ru"
}


quotes = [
{
"id": 1,
"author": "Rick Cook",
"text": "Программирование сегодня — это гонка \
разработчиков программ, стремящихся писать программы с \
большей и лучшей идиотоустойчивостью, и вселенной, которая \
пытается создать больше отборных идиотов. Пока вселенная \
побеждает."
},
{
"id": 2,
"author": "Waldi Ravens",
"text": "Программирование на С похоже на быстрые танцы \
на только что отполированном полу людей с острыми бритвами в \
руках."
},
{
"id": 3,
"author": "Moshers Law of Software Engineering",
"text": "Не волнуйтесь, если что-то не работает. Если \
бы всё работало, вас бы уволили."
},
{
"id": 4,
"author": "Yoggi Berra",
"text": "В теории, теория и практика неразделимы. На \
практике это не так."
},
]



@app.route("/") #первый url, который мы обрабатываем
def hello_world():#функций-обработчик
    return jsonify(hello="Hello, World!"),200


@app.route("/about")
def about():
    return jsonify(about_me),200


@app.route("/quotes")
def get_quotes() -> list[dict[str: Any]]:
    """ функция преобразует список словарей в массив объектов json"""
    return jsonify(quotes),200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    for quote in quotes:
        if quote.get("id") == quote_id:
            return jsonify(quote), 201
    return {"error":f"цитаты с id {quote_id} нет"}, 404


@app.get("/quotes/count")
def quote_count():
    return jsonify(count = len(quotes)),200


@app.route("/quotes/random", methods =["GET"])
def random_quote() -> dict:
    return jsonify(choice(quotes)),200


@app.route("/quotes", methods=['POST'])
def create_quote():
    """создание новой цитаты и добавление ее в словарь"""
    new_id = quotes[-1].get("id") + 1
    data = request.json
    new_quote = {
                "id" : new_id,
                "author" : data.get("author"),
                "text" : data.get("text")
                }
    quotes.append(new_quote)
    print("data = ", data)
    return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    """редактирование цитаты, если новые данные есть"""
    new_data = request.json
    for quote in quotes:
        if quote.get("id") == quote_id:
            for key in new_data.keys():
                if key in quote.keys():
                    quote.update({key: new_data.get(key)})
            return jsonify(quote), 200
    return f'Quote with id {quote_id} does not exist'


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    for quote in quotes:
        if quote.get("id") == quote_id:
            quotes.remove(quote)
            return f"Quote with {quote_id} is deleted.", 200
    return f"Quote with {quote_id} does not exist.", 404


if __name__ == "__main__":
    app.run(debug=True)