import psycopg2
import joblib
import json
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
from flask import send_file
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "ecopackai_secret"

CORS(app)

# --------------------------------
# LOAD ML MODELS
# --------------------------------

cost_model = joblib.load("models/cost_model.pkl")
co2_model = joblib.load("models/co2_model.pkl")

# --------------------------------
# DATABASE CONNECTION
# --------------------------------
conn = psycopg2.connect(
    database="ecopackai",
    user="postgres",
    password="amulya586",
    host="your_render_db_host",
    port="5432"
)

# --------------------------------
# PAGE ROUTES
# --------------------------------

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


# --------------------------------
# REGISTER USER
# --------------------------------

@app.route('/register', methods=['POST'])
def register():

    data = request.json

    name = data['name']
    email = data['email']
    password = data['password']

    cur = conn.cursor()

    try:

        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )

        conn.commit()
        cur.close()

        return jsonify({"message":"User Registered Successfully"})

    except Exception as e:

        conn.rollback()

        return jsonify({"message":"Registration failed"})


# --------------------------------
# LOGIN USER
# --------------------------------

@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']
    password = data['password']

    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM users WHERE email=%s AND password=%s",
        (email,password)
    )

    user = cur.fetchone()

    cur.close()

    if user:

        session['user'] = user[0]

        return jsonify({
            "success":True,
            "name":user[0]
        })

    else:

        return jsonify({
            "success":False,
            "message":"Invalid credentials"
        })


# --------------------------------
# CHECK LOGIN
# --------------------------------

@app.route('/check-login')
def check_login():

    if 'user' in session:

        return jsonify({
            "logged_in":True,
            "name":session['user']
        })

    else:

        return jsonify({
            "logged_in":False
        })


# --------------------------------
# LOGOUT
# --------------------------------

@app.route('/logout')
def logout():

    session.pop('user',None)

    return jsonify({"message":"Logged out"})


# --------------------------------
# AI PREDICTION + MATERIAL RANKING
# --------------------------------

@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:
        return jsonify({"error":"Please login first"})


    data = request.json

    weight = float(data['weight'])
    strength = float(data['strength'])
    capacity = float(data['capacity'])
    biodegradability = float(data['biodegradability'])
    recyclability = float(data['recyclability'])
    durability = float(data['durability'])


    input_features = [[
        weight,
        strength,
        capacity,
        biodegradability,
        recyclability,
        durability
    ]]


    predicted_cost = cost_model.predict(input_features)[0]
    predicted_co2 = co2_model.predict(input_features)[0]


    # --------------------------------
    # GET MATERIAL DATASET
    # --------------------------------

    cur = conn.cursor()

    cur.execute("""
        SELECT material_type,
               strength_mpa,
               weight_capacity_kg,
               biodegradability_score,
               co2_emission_score,
               recyclability_percent,
               cost_per_kg
        FROM materials_dataset
    """)

    rows = cur.fetchall()

    cur.close()


    materials = []

    for r in rows:

        material = r[0]
        strength_mpa = float(r[1])
        weight_capacity = float(r[2])
        bio_score = float(r[3])
        co2_score = float(r[4])
        recycle_score = float(r[5])
        cost = float(r[6])

        # Sustainability score
        score = (
            0.5 * co2_score +
            0.3 * cost -
            0.2 * bio_score
        )

        materials.append({

            "material":material,
            "cost":cost,
            "co2":co2_score,
            "score":score
        })


    # --------------------------------
    # RANK MATERIALS
    # --------------------------------

    ranking = sorted(materials, key=lambda x: x["score"])

    for i, m in enumerate(ranking):
        m["rank"] = i+1


    # --------------------------------
    # LOAD MODEL METRICS
    # --------------------------------

    with open("models/metrics.json") as f:
        metrics = json.load(f)


    return jsonify({

        "recommended_material":ranking[0]["material"],

        "predicted_cost":float(predicted_cost),

        "predicted_co2":float(predicted_co2),

        "ranking":ranking,

        "metrics":metrics

    })
@app.route('/download-report')
def download_report():

    if 'user' not in session:
        return jsonify({"error": "Login required"})

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("EcoPackAI Sustainability Report", styles['Title']))
    content.append(Paragraph(" ", styles['Normal']))

    content.append(Paragraph("This report contains AI-based packaging insights.", styles['Normal']))
    content.append(Paragraph("Generated from EcoPackAI Dashboard.", styles['Normal']))

    doc.build(content)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="EcoPackAI_Report.pdf", mimetype='application/pdf')

@app.route('/download-excel')
def download_excel():

    if 'user' not in session:
        return jsonify({"error": "Login required"})

    # Sample data (you can replace with real prediction data later)
    data = {
        "Material": ["Cardboard", "Plastic", "Glass"],
        "Cost": [120, 200, 150],
        "CO2": [80, 300, 150]
    }

    df = pd.DataFrame(data)

    file_path = "report.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)
# --------------------------------
# RUN SERVER
# --------------------------------

if __name__ == "__main__":

    app.run(debug=True)
