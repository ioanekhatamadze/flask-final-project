from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, migrate, login_manager
from models import User, Post

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret-key-change"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"].strip().lower()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "User already exists"

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("home"))

    return render_template("register.html")


from flask import flash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid username or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        content = request.form["content"]

        post = Post(content=content, user_id=current_user.id)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("create_post.html")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)

    post.views += 1
    db.session.commit()

    return render_template("post.html", post=post)


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)

    posts = Post.query.filter_by(user_id=user.id).all()

    return render_template(
        "profile.html",
        user=user,
        posts=posts,
        posts_count=len(posts)
    )


@app.route("/me")
@login_required
def me():
    posts = Post.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "profile.html",
        user=current_user,
        posts=posts,
        posts_count=len(posts)
    )


if __name__ == "__main__":
    app.run(debug=True)