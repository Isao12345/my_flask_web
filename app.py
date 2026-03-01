from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "devkey"


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

if __name__ == "__main__":
    app.run(debug=True)