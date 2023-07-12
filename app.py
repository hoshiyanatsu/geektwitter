from flask import Flask, render_template, request, redirect

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# FlaskでAPIを書くときのおまじない
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    body = db.Column(db.String(140), nullable=False)


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # POSTメソッドの時の処理。
        title = request.form.get("title")
        body = request.form.get("body")

        post = Post(title=title, body=body)
        # DBに値を送り保存する
        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else:
        # GETメソッドの時の処理
        return render_template("new.html")


if __name__ == "__main__":
    app.run(debug=True)
