from flask import session, Flask, request, redirect, url_for, render_template
from models import Expense, User, db, Income, Category
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

# make current_user available in all templates
@app.context_processor
def inject_user():
    if "user_id" in session:
        return {"current_user": User.query.get(session["user_id"])}
    return {}


# ROUTES
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/expenses")
@login_required
def expenses():
    uid = session["user_id"]
    expenses = Expense.query.filter_by(user_id=uid).all()
    return render_template("expenses.html", expenses=expenses)


@app.route("/income")
@login_required
def income():
    uid = session["user_id"]
    incomes = Income.query.filter_by(user_id=uid).all()
    return render_template("income.html", incomes=incomes)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    uid = session["user_id"]
    error = None
    if request.method == "POST":
        name = request.form["name"].strip()
        ctype = request.form.get("type")
        if not name or ctype not in ("income", "expense"):
            error = "Invalid category data"
        else:
            # avoid duplicates for same user/type
            if Category.query.filter_by(user_id=uid, name=name, type=ctype).first():
                error = "Category already exists"
            else:
                cat = Category(name=name, type=ctype, user_id=uid)
                db.session.add(cat)
                db.session.commit()
                return redirect(url_for("categories"))

    cats = Category.query.filter_by(user_id=uid).all()
    return render_template("categories.html", categories=cats, error=error)

@app.route("/categories/delete/<int:cat_id>", methods=["POST"])
@login_required
def delete_category(cat_id):
    uid = session["user_id"]
    cat = Category.query.get(cat_id)
    if cat and cat.user_id == uid:
        db.session.delete(cat)
        db.session.commit()
    return redirect(url_for("categories"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect already-logged-in users straight to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # ตรวจซ้ำ (กัน username/email ซ้ำ)
        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            error = "Username or email already taken"
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)


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
    uid = session["user_id"]
    # load expense categories for dropdown
    cats = Category.query.filter_by(user_id=uid, type="expense").all()
    if request.method == "POST":
        category_id = request.form.get("category_id")
        expense = Expense(
            title=request.form["title"],
            amount=float(request.form["amount"]),
            user_id=uid,
            **({"category_id": int(category_id)} if category_id else {})
        )
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for("transactions"))

    return render_template("add_expense.html", categories=cats)


@app.route("/income/add", methods=["GET", "POST"])
@login_required
def add_income():
    uid = session["user_id"]
    cats = Category.query.filter_by(user_id=uid, type="income").all()
    if request.method == "POST":
        category_id = request.form.get("category_id")
        income = Income(
            title=request.form["title"],
            amount=float(request.form["amount"]),
            user_id=uid,
            **({"category_id": int(category_id)} if category_id else {})
        )
        db.session.add(income)
        db.session.commit()
        return redirect(url_for("transactions"))

    return render_template("add_income.html", categories=cats)

# 👉 CREATE TABLES (วางตรงนี้)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)