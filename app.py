from flask import Flask

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


about_me = {
"name": "Евгений",
"surname": "Юрченко",
"email": "eyurchenko@specialist.ru"
}


@app.route("/") #первый url, который мы обрабатываем
def hello_world():#функций-обработчик
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


if __name__ == "__main__":
    app.run(debug=True)