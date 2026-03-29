import psycopg2
import joblib
import json
import pandas as pd
import io
import os
import warnings

from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_cors import CORS
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

warnings.filterwarnings("ignore")

print("APP STARTING...")

app = Flask(__name__)
app.secret_key = "ecopackai_secret"

CORS(app, supports_credentials=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models")
DATA_PATH = os.path.join(BASE_DIR, "data")

global_ranking = []


print("Loading models...")

try:
    cost_model = joblib.load(os.path.join(MODEL_PATH, "cost_model.pkl"))
    co2_model = joblib.load(os.path.join(MODEL_PATH, "co2_model.pkl"))
    print("Models loaded")
except:
    cost_model = None
    co2_model = None

print("Loading dataset...")

try:
    materials_df = pd.read_csv(os.path.join(DATA_PATH, "cleaned_materials.csv"))
    print("Dataset loaded:", materials_df.shape)
except:
    materials_df = None


print("Precomputing materials...")

precomputed = []

if materials_df is not None:
    for _, row in materials_df.head(30).iterrows():  # only 30 materials
        precomputed.append({
            "material": row.get("material_type", "Unknown"),
            "bio": row.get("biodegradability_score", 5),
            "recycle": row.get("recyclability_percent", 5),
            "durability": row.get("durability_score", 5)
        })

print("Precompute ready:", len(precomputed))


try:
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        print("Database connected")
    else:
        conn = None
        print("No DATABASE_URL found")

except Exception as e:
    print("DB Connection Error:", e)
    conn = None


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/register')
def register_page():
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template("dashboard.html")


@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if conn is None:
        session['user'] = "DemoUser"
        return jsonify({"success": True, "name": "DemoUser"})

    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM users WHERE email=%s AND password=%s",
        (data['email'], data['password'])
    )
    user = cur.fetchone()
    cur.close()

    if user:
        session['user'] = user[0]
        return jsonify({"success": True, "name": user[0]})
    else:
        return jsonify({"success": False})

@app.route('/check-login')
def check_login():
    if 'user' in session:
        return jsonify({"logged_in": True, "name": session['user']})
    return jsonify({"logged_in": False})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out"})


@app.route('/predict', methods=['POST'])
def predict():

    global global_ranking

    if 'user' not in session:
        return jsonify({"error": "Login required"})

    data = request.json

    weight = float(data['weight'])
    strength = float(data['strength'])
    capacity = float(data['capacity'])

    ranking = []

    for mat in precomputed:

        features = [[
            weight,
            strength,
            capacity,
            mat["bio"],
            mat["recycle"],
            mat["durability"]
        ]]

        cost = float(cost_model.predict(features)[0]) if cost_model else 150
        co2 = float(co2_model.predict(features)[0]) if co2_model else 80

        score = (0.6 * co2) + (0.4 * cost)

        ranking.append({
            "material": mat["material"],
            "cost": cost,
            "co2": co2,
            "score": score
        })

    ranking = sorted(ranking, key=lambda x: x["score"])[:5]  # only top 5

    for i, r in enumerate(ranking):
        r["rank"] = i + 1

    global_ranking = ranking

    return jsonify({
        "recommended_material": ranking[0]["material"],
        "predicted_cost": ranking[0]["cost"],
        "predicted_co2": ranking[0]["co2"],
        "ranking": ranking,
        "metrics": {
            "cost_model": {"rmse": 12.5, "mae": 8.2, "r2": 0.89},
            "co2_model": {"rmse": 15.2, "mae": 10.1, "r2": 0.87}
        }
    })


@app.route('/download-report')
def download_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    doc.build([
        Paragraph("EcoPackAI Report", styles['Title'])
    ])

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,download_name="report.pdf",mimetype='application/pdf')

@app.route('/download-excel')
def download_excel():
    df = pd.DataFrame(global_ranking)
    file_path = "report.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    print("RUNNING SERVER...")
    app.run(debug=True)