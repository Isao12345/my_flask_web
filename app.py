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


if __name__ == "__main__":
    app.run(debug=True)