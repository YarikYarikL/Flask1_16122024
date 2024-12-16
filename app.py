from flask import Flask, jsonify, Response

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


about_me = {
"name": "Евгений",
"surname": "Юрченко",
"email": "eyurchenko@specialist.ru"
}


@app.route("/") #первый url, который мы обрабатываем
def hello_world():#функций-обработчик
    return jsonify(hello="Hello, World!"),200


@app.route("/about")
def about():
    return jsonify(about_me),200


if __name__ == "__main__":
    app.run(debug=True)