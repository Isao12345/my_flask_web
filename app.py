from flask import Flask, render_template 
from flask_sqlalchemy import SQLAlchemy   

app = Flask(__name__)
app.config["SECRET_KEY"] = "devkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/expenses")
def expenses():
    return render_template("expenses.html")


@app.route("/income")
def income():
    return render_template("income.html")


@app.route("/categories")
def categories():
    return render_template("categories.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True)