from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key"
API_URL = os.getenv("API_URL", "http://api:8000")

# --- AUTH ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        password_hash = generate_password_hash(password)
        requests.post(f"{API_URL}/users", json={"username": username, "password_hash": password_hash, "role": role})
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        r = requests.get(f"{API_URL}/users/{username}")
        if r.status_code == 200:
            user = r.json()
            if check_password_hash(user["password_hash"], password):
                session["username"] = username
                session["role"] = user["role"]
                return redirect(url_for("index"))
        return "Неверный логин или пароль", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Декораторы ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return "Доступ запрещён", 403
        return f(*args, **kwargs)
    return wrapper

def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "user":
            return "Доступ запрещён", 403
        return f(*args, **kwargs)
    return wrapper

# --- USER ROUTES ---
@app.route("/user/vessels")
@login_required
@user_required
def user_vessels():
    vessels = requests.get(f"{API_URL}/vessels").json()
    return render_template("user/vessels.html", vessels=vessels)

@app.route("/user/vessels/add", methods=["POST"])
@login_required
@user_required
def user_add_vessel():
    data = {"name": request.form["name"], "type": request.form.get("type"), "displacement": request.form.get("displacement"), "build_date": request.form.get("build_date")}
    requests.post(f"{API_URL}/vessels", json=data)
    return redirect(url_for("user_vessels"))

@app.route("/user/voyages")
@login_required
@user_required
def user_voyages():
    voyages = requests.get(f"{API_URL}/voyages").json()
    return render_template("user/voyages.html", voyages=voyages)

@app.route("/user/voyages/add", methods=["POST"])
@login_required
@user_required
def user_add_voyage():
    data = {
        "vessel_id": request.form["vessel_id"],
        "depart_date": request.form["depart_date"],
        "return_date": request.form.get("return_date")
    }
    requests.post(f"{API_URL}/voyages", json=data)
    return redirect(url_for("user_voyages"))

@app.route("/user/visits")
@login_required
@user_required
def user_visits():
    visits = requests.get(f"{API_URL}/visits").json()
    return render_template("user/visits.html", visits=visits)

@app.route("/user/visits/add", methods=["POST"])
@login_required
@user_required
def user_add_visit():
    data = {
        "voyage_id": request.form["voyage_id"],
        "bank_id": request.form["bank_id"],
        "arrival_date": request.form["arrival_date"],
        "departure_date": request.form.get("departure_date"),
        "quality": request.form["quality"]
    }
    requests.post(f"{API_URL}/visits", json=data)
    return redirect(url_for("user_visits"))

@app.route("/user/catches")
@login_required
@user_required
def user_catches():
    catches = requests.get(f"{API_URL}/catches").json()
    return render_template("user/catches.html", catches=catches)

@app.route("/user/catches/add", methods=["POST"])
@login_required
@user_required
def user_add_catch():
    data = {
        "visit_id": request.form["visit_id"],
        "species": request.form["species"],
        "weight": request.form["weight"]
    }
    requests.post(f"{API_URL}/catches", json=data)
    return redirect(url_for("user_catches"))

# --- ADMIN ROUTES ---
@app.route("/admin/vessels")
@login_required
@admin_required
def admin_vessels():
    vessels = requests.get(f"{API_URL}/vessels").json()
    return render_template("admin/vessels.html", vessels=vessels)

@app.route("/admin/reports")
@login_required
@admin_required
def admin_reports():
    reports = requests.get(f"{API_URL}/reports/top-vessels").json()
    return render_template("admin/reports.html", reports=reports)

@app.route("/admin/banks")
@login_required
@admin_required
def admin_banks():
    banks = requests.get(f"{API_URL}/banks").json()
    return render_template("admin/banks.html", banks=banks)

@app.route("/admin/banks/add", methods=["POST"])
@login_required
@admin_required
def admin_add_bank():
    data = {
        "name": request.form["name"],
        "location": request.form.get("location")
    }
    requests.post(f"{API_URL}/banks", json=data)
    return redirect(url_for("admin_banks"))

@app.route("/admin/reports/top_vessels_period", methods=["GET", "POST"])
@login_required
@admin_required
def top_vessels_period():
    reports = []
    if request.method == "POST":
        species = request.form.get("species")
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        params = {"species": species, "date_from": date_from, "date_to": date_to}
        reports = requests.get(f"{API_URL}/reports/top-vessels", params=params).json()
    return render_template("admin/top_vessels_period.html", reports=reports)

@app.route("/admin/reports/bank_avg", methods=["GET", "POST"])
@login_required
@admin_required
def bank_avg():
    reports = []
    if request.method == "POST":
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        params = {"date_from": date_from, "date_to": date_to}
        reports = requests.get(f"{API_URL}/reports/avg-catch-per-bank", params=params).json()
    return render_template("admin/bank_avg.html", reports=reports)

@app.route("/admin/reports/above_avg/<int:bank_id>")
@login_required
@admin_required
def above_avg(bank_id):
    reports = requests.get(f"{API_URL}/reports/above-average/{bank_id}").json()
    return render_template("admin/above_avg.html", reports=reports, bank_id=bank_id)

@app.route("/admin/reports/species_bank", methods=["GET", "POST"])
@login_required
@admin_required
def species_bank():
    reports = []
    if request.method == "POST":
        species = request.form.get("species")
        bank_id = request.form.get("bank_id")
        params = {"species": species, "bank_id": bank_id}
        reports = requests.get(f"{API_URL}/reports/species-bank", params=params).json()
    return render_template("admin/species_bank.html", reports=reports)

@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

