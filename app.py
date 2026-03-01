from flask import session, Flask, request, redirect, url_for, render_template
from models import Expense, User, db, Income
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "devkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# INIT DB (สำคัญ)
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ROUTES
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
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # ตรวจซ้ำ (กัน username/email ซ้ำ)
        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            return "User already exists"

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html", error="User already exists")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/transactions")
@login_required
def transactions():
    uid = session["user_id"]

    expenses = Expense.query.filter_by(user_id=uid).all()
    incomes = Income.query.filter_by(user_id=uid).all()

    return render_template(
        "transactions.html",
        expenses=expenses,
        incomes=incomes
    )


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        expense = Expense(
            title=request.form["title"],
            amount=float(request.form["amount"]),
            user_id=session["user_id"]
        )
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for("transactions"))

    return render_template("add_expense.html")


@app.route("/income/add", methods=["GET", "POST"])
@login_required
def add_income():
    if request.method == "POST":
        income = Income(
            title=request.form["title"],
            amount=float(request.form["amount"]),
            user_id=session["user_id"]
        )
        db.session.add(income)
        db.session.commit()
        return redirect(url_for("transactions"))

    return render_template("add_income.html")

# 👉 CREATE TABLES (วางตรงนี้)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)