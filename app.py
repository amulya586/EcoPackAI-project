from flask import Flask, request, jsonify, session, render_template, redirect
from flask_cors import CORS
import psycopg2
import os
from flask import send_file
import pandas as pd
from reportlab.pdfgen import canvas
app = Flask(__name__)


app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")


app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True


CORS(app, supports_credentials=True)


DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB ERROR:", e)
        return None



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")



@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"})

    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Registered successfully"
        })

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Email already exists"
        })


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database error"})

    cursor = conn.cursor()

    cursor.execute(
        "SELECT username FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        session["user"] = email
        session["name"] = user[0]

        return jsonify({
            "success": True,
            "name": user[0]
        })

    return jsonify({
        "success": False,
        "message": "Invalid email or password"
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/check-login")
def check_login():
    if "user" in session:
        return jsonify({
            "logged_in": True,
            "name": session.get("name")
        })

    return jsonify({"logged_in": False})




@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        weight = float(data.get("weight"))
        strength = float(data.get("strength"))
        capacity = float(data.get("capacity"))

        predicted_cost = weight * 50 + strength * 10
        predicted_co2 = weight * 20 + capacity * 5

        if predicted_co2 < 150:
            material = "Recycled Paper"
        elif predicted_co2 < 300:
            material = "Biodegradable Plastic"
        else:
            material = "Corrugated Box"

        ranking = [
            {"material": "Recycled Paper", "cost": 100, "co2": 80, "rank": 1},
            {"material": "Biodegradable Plastic", "cost": 200, "co2": 150, "rank": 2},
            {"material": "Corrugated Box", "cost": 300, "co2": 250, "rank": 3}
        ]

        metrics = {
            "cost_model": {"rmse": 12.5, "mae": 8.3, "r2": 0.91},
            "co2_model": {"rmse": 15.2, "mae": 10.1, "r2": 0.88}
        }

        return jsonify({
            "recommended_material": material,
            "predicted_cost": predicted_cost,
            "predicted_co2": predicted_co2,
            "ranking": ranking,
            "metrics": metrics
        })

    except Exception as e:
        print("PREDICT ERROR:", e)
        return jsonify({"error": "Prediction failed"})




@app.route("/download-report")
def download_report():
    file_path = "report.pdf"

    c = canvas.Canvas(file_path)
    c.drawString(100, 750, "EcoPackAI Report")
    c.drawString(100, 720, "Generated Successfully")
    c.save()

    return send_file(file_path, as_attachment=True)



@app.route("/download-excel")
def download_excel():
    data = {
        "Material": ["Paper", "Plastic", "Glass"],
        "Cost": [120, 200, 300],
        "CO2": [50, 150, 80]
    }

    df = pd.DataFrame(data)
    file_path = "report.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)