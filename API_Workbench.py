from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from functools import wraps

app = Flask(__name__)
CORS(app)  # 🔥 REQUIRED FOR FRONTEND

# ---------------- CONFIG ----------------
SECRET_KEY = "healthsync_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ---------------- DATABASE UTILS ----------------
def get_db():
    return psycopg2.connect(
        host="localhost",
        database="patient",
        user="postgres",
        password="Shahil@6125",
        port="5432"
    )

# ---------------- JWT UTILS ----------------
def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = data.copy()
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token missing"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.user = payload
        except JWTError:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    return decorated

# ---------------- ADD PATIENT ----------------
@app.route("/patients/add", methods=["POST"])
def add_patient():
    data = request.json

    required = ["patient_id", "full_name", "date_of_birth"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO patient_details
            (patient_id, full_name, gender, date_of_birth, blood_group,
             phone_number, email, address, city, state, country, height_cm, weight_kg)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data["patient_id"],
            data["full_name"],
            data.get("gender"),
            data["date_of_birth"],
            data.get("blood_group"),
            data.get("phone_number"),
            data.get("email"),
            data.get("address"),
            data.get("city"),
            data.get("state"),
            data.get("country", "India"),
            data.get("height_cm"),
            data.get("weight_kg")
        ))

        conn.commit()
        return jsonify({
            "message": "Patient registered successfully",
            "patient_id": data["patient_id"]
        })

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Patient ID already exists"}), 409

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data.get("email") or not data.get("patient_id"):
        return jsonify({"error": "Email and Patient ID are required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id, full_name
        FROM patient_details
        WHERE email = %s
          AND patient_id = %s
    """, (
        data["email"],
        data["patient_id"]
    ))

    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        return jsonify({"error": "Invalid email or patient ID"}), 401

    token = create_access_token({
        "patient_id": patient[0],
        "name": patient[1]
    })

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "token_type": "Bearer"
    })

# ---------------- ADD VITALS (JWT PROTECTED) ----------------
@app.route("/vitals/add", methods=["POST"])
@token_required
def add_vitals():
    data = request.json
    patient_id = request.user["patient_id"]

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO patient_vitals
            (patient_id, heart_rate_bpm, systolic_bp_mmHg, diastolic_bp_mmHg,
             body_temperature_c, respiratory_rate, oxygen_saturation, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING vital_id
        """, (
            patient_id,
            data.get("heart_rate_bpm"),
            data.get("systolic_bp_mmHg"),
            data.get("diastolic_bp_mmHg"),
            data.get("body_temperature_c"),
            data.get("respiratory_rate"),
            data.get("oxygen_saturation"),
            data.get("notes")
        ))

        vital_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Vitals added successfully",
            "vital_id": vital_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()

# ---------------- ROOT ----------------
@app.route("/")
def home():
    return jsonify({"status": "HealthSync API running"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
    