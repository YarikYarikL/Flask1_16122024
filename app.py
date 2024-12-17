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
побеждает.",
"rating": 4
},
{
"id": 2,
"author": "Waldi Ravens",
"text": "Программирование на С похоже на быстрые танцы \
на только что отполированном полу людей с острыми бритвами в \
руках.",
"rating": 1
},
{
"id": 3,
"author": "Moshers Law of Software Engineering",
"text": "Не волнуйтесь, если что-то не работает. Если \
бы всё работало, вас бы уволили.",
"rating": 5
},
{
"id": 4,
"author": "Yoggi Berra",
"text": "В теории, теория и практика неразделимы. На \
практике это не так.",
"rating": 2
},
]



@app.route("/") #первый url, который мы обрабатываем
def hello_world():#функций-обработчик
    return jsonify(hello="Hello, World!"), 200


@app.route("/about")
def about():
    return jsonify(about_me), 200


@app.route("/quotes")
def get_quotes() -> list[dict[str: Any]]:
    """ функция преобразует список словарей в массив объектов json"""
    return jsonify(quotes), 200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    for quote in quotes:
        if quote.get("id") == quote_id:
            return jsonify(quote), 201
    return {"error":f"цитаты с id {quote_id} нет"}, 404


@app.get("/quotes/count")
def quote_count():
    return jsonify(count = len(quotes)), 200


@app.route("/quotes/random", methods =["GET"])
def random_quote() -> dict:
    return jsonify(choice(quotes)), 200


@app.route("/quotes", methods=['POST'])
def create_quote():
    """ Function creates new quote and adds it in the list. """
    new_quote = request.json # На выходе мы получим словарь с данными
    new_quote["id"] = quotes[-1].get("id") + 1 # Новый id
    #проверяем наличие ключа рейтинга <rating> и его валидность
    rating = new_quote.get("rating")
    if rating is None or rating not in range(1,6):
        new_quote["rating"] =1
    quotes.append(new_quote)
    return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int):
    new_data = request.json
    if not set(new_data.keys()) - set(("author", "text", "rating")):
        for quote in quotes:
            if quote.get("id") == quote_id:
                if "rating" in new_data and new_data["rating"] not in range(1,6):
                    new_data.pop("rating")
                quote.update(new_data)
                return jsonify(quote), 200
    else:
        return jsonify(error="Send bad data to update."), 400
    return jsonify(error=f"Quote with id={quote_id} doesn't exist."), 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id: int):
    assert type(quote_id) is int, f"Bad type of <quote_id>: {type(quote_id)}"
    for quote in quotes:
        if quote.get("id") == quote_id:
            quotes.remove(quote)
            return f"Quote with {quote_id} has deleted.", 200
    return f"Quote with {quote_id} not found.", 404


@app.route("/quotes/filter")
def filter_quotes():
    filtered_quotes = quotes.copy()
    #request.args хранит данные, полученные из query parameters
    for key, value in request.args.items():
        result = []
        if key not in ("author", "text", "rating"):
            return jsonify(error=f"Invalid param = {key}"), 400
        if key == "rating":
            value =int(value)
        for quote in filtered_quotes:
            if quote[key] == value:
                result.append(quote)
        filtered_quotes = result.copy()
    return jsonify(filtered_quotes), 200


if __name__ == "__main__":
    app.run(debug=True)