from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import os
from werkzeug.security import generate_password_hash, check_password_hash


# FlaskでAPIを書くときのおまじない
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    body = db.Column(db.String(140), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash("このページにアクセスするにはログインが必要です")
    return redirect(url_for("login"))  # ログインページのエンドポイントを指定


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        # POSTメソッドの時の処理。
        title = request.form.get("title")
        body = request.form.get("body")
        post = Post(title=title, body=body, user_id=current_user.id)  # ログイン中のユーザーのIDを取得
        # DBに値を送り保存する
        db.session.add(post)
        db.session.commit()
        return redirect("/")
    else:
        # GETメソッドの時の処理
        return render_template("new.html")


@app.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        if post.user_id == current_user.id:
            return render_template("edit.html", post=post)
        else:
            flash("投稿者のみ編集できます")
            return redirect("/")
    else:
        post.title = request.form.get("title")
        post.body = request.form.get("body")
        db.session.commit()
        return redirect("/")


@app.route("/<int:id>/show", methods=["GET"])
@login_required
def show(id):
    post = Post.query.get(id)
    return render_template("show.html", post=post)


@app.route("/<int:id>/delete", methods=["GET"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    # ログインユーザーと投稿作成者を比較
    if post.user_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash("投稿を削除しました")
    else:
        flash("他のユーザーの投稿は削除できません")
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Userのインスタンスを作成
        user = User(
            username=username,
            password=generate_password_hash(password, method="sha256"),
        )
        db.session.add(user)
        db.session.commit()
        return redirect("login")
    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Userテーブルからusernameに一致するユーザを取得
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        else:
            flash("ユーザ名またはパスワードが正しくありません")
            return redirect("/login")
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("login")


if __name__ == "__main__":
    app.run(debug=True)
