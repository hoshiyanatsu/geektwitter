import os
from flask import Flask, request, render_template
from model import predict

# FlaskでAPIを書くときのおまじない
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
