from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import os
import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "diabetescare_dev_key_2026")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ================= LOAD ML MODEL =================
model = None
accuracy = None

try:
    with open(MODEL_PATH, "rb") as file:
        model, accuracy = pickle.load(file)

    print(f"Model loaded successfully | Accuracy: {accuracy * 100:.2f}%")

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
        accuracy=round(accuracy * 100, 2) if accuracy is not None else None
    )

@app.route("/about")
def about():
    return render_template(
        "about.html",
        logged_in=is_logged_in()
    )

@app.route("/causes")
def causes():
    return render_template(
        "causes.html",
        logged_in=is_logged_in()
    )

@app.route("/prevention")
def prevention():
    return render_template(
        "prevention.html",
        logged_in=is_logged_in()
    )

# ================= AUTH =================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"]
        )

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
            return render_template(
                "register.html",
                error="Email already exists",
                logged_in=is_logged_in()
            )

    return render_template(
        "register.html",
        logged_in=is_logged_in()
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("index"))

        return render_template(
            "login.html",
            error="Invalid email or password",
            logged_in=False
        )

    return render_template(
        "login.html",
        logged_in=False
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= PREDICTION =================

@app.route("/risk_test")
def risk_test():

    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template(
        "risk_test.html",
        logged_in=is_logged_in()
    )

@app.route("/predict", methods=["POST"])
def predict():

    if not is_logged_in():
        return redirect(url_for("login"))

    if model is None:
        return render_template(
            "result.html",
            prediction_text="Prediction model is not loaded.",
            logged_in=is_logged_in()
        )

    try:

        pregnancies = float(request.form["pregnancies"])
        glucose = float(request.form["glucose"])
        bloodpressure = float(request.form["bloodpressure"])
        skinthickness = float(request.form["skinthickness"])
        insulin = float(request.form["insulin"])
        bmi = float(request.form["bmi"])
        dpf = float(request.form["dpf"])
        age = float(request.form["age"])

        # ===== INPUT VALIDATION =====

        if age < 1 or age > 120:
            raise ValueError("Age must be between 1 and 120.")

        if glucose < 0 or glucose > 500:
            raise ValueError("Invalid glucose value.")

        if bloodpressure < 0 or bloodpressure > 250:
            raise ValueError("Invalid blood pressure value.")

        if bmi < 0 or bmi > 100:
            raise ValueError("Invalid BMI value.")

        features = np.array([
            pregnancies,
            glucose,
            bloodpressure,
            skinthickness,
            insulin,
            bmi,
            dpf,
            age
        ]).reshape(1, -1)

        prediction = model.predict(features)[0]

        if prediction == 1:
            result_text = (
                "High risk of diabetes. "
                "Please consult a doctor."
            )
        else:
            result_text = (
                "Low risk of diabetes. "
                "Maintain a healthy lifestyle."
            )

        return render_template(
            "result.html",
            prediction_text=result_text,
            accuracy=round(accuracy * 100, 2) if accuracy is not None else None,
            logged_in=is_logged_in()
        )

    except Exception as e:

        return render_template(
            "result.html",
            prediction_text=f"Error: {e}",
            logged_in=is_logged_in()
        )

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=False)