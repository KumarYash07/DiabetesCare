from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import os
import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = "super_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ================= LOAD ML MODEL =================
model = None
accuracy = None

try:
    with open(MODEL_PATH, "rb") as file:
        model, accuracy = pickle.load(file)
    print(f"Model loaded successfully | Accuracy: {accuracy*100:.2f}%")
except Exception as e:
    print("Error loading model:", e)

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= HELPERS =================
def is_logged_in():
    return "user_id" in session

# ================= ROUTES =================

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        logged_in=True,
        accuracy=round(accuracy * 100, 2) if accuracy else None
    )

@app.route("/about")
def about():
    return render_template("about.html", logged_in=is_logged_in())

@app.route("/causes")
def causes():
    return render_template("causes.html", logged_in=is_logged_in())

@app.route("/prevention")
def prevention():
    return render_template("prevention.html", logged_in=is_logged_in())

# ---------------- AUTH ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Email already exists")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- PREDICTION ----------------

@app.route("/risk_test")
def risk_test():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("risk_test.html")

@app.route("/predict", methods=["POST"])
def predict():
    if not is_logged_in():
        return redirect(url_for("login"))

    if model is None:
        return render_template(
            "result.html",
            prediction_text="Model not loaded. Please contact admin.",
            logged_in=is_logged_in()
        )

    try:
        features = np.array([
            float(request.form["pregnancies"]),
            float(request.form["glucose"]),
            float(request.form["bloodpressure"]),
            float(request.form["skinthickness"]),
            float(request.form["insulin"]),
            float(request.form["bmi"]),
            float(request.form["dpf"]),
            float(request.form["age"])
        ]).reshape(1, -1)

        prediction = model.predict(features)[0]

        result_text = (
            "High risk of diabetes. Please consult a doctor."
            if prediction == 1
            else "Low risk of diabetes. Maintain a healthy lifestyle."
        )

        return render_template(
            "result.html",
            prediction_text=result_text,
            accuracy=round(accuracy * 100, 2),
            logged_in=is_logged_in()
        )

    except Exception as e:
        return render_template(
            "result.html",
            prediction_text=f"Error occurred: {e}",
            logged_in=is_logged_in()
        )

# ================= RUN =================
if __name__ == "__main__":
    os.chdir(BASE_DIR)
    app.run(debug=True)
