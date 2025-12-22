# 🏥 HealthSync – Patient Vital Monitoring Dashboard

HealthSync is a full-stack healthcare monitoring system that allows patients and healthcare staff to securely record, manage, and visualize daily health vitals such as heart rate, blood pressure, body temperature, oxygen saturation, and respiratory rate.

The system is built using Flask-based REST APIs, PostgreSQL for structured data storage, JWT authentication for security, and an interactive Dash–Plotly dashboard for real-time analytics. A responsive frontend provides seamless user interaction for registration, login, vitals entry, and dashboard access.

---

## 🚀 Features

- Patient registration and secure login
- JWT-based authentication and authorization
- Add and store daily patient vitals
- PostgreSQL relational database integration
- Interactive analytics dashboard with trends
- Real-time reflection of database updates
- Responsive and user-friendly web pages

---

## 🛠 Tech Stack

### Backend
- Flask (REST APIs)
- JWT Authentication
- psycopg2
- flask-cors

### Database
- PostgreSQL

### Dashboard & Analytics
- Dash
- Plotly
- Pandas
- SQLAlchemy

### Frontend
- HTML
- CSS
- JavaScript

---

## 🗄 Database Schema

### patient_details
- patient_id (Primary Key)
- full_name
- gender
- date_of_birth
- blood_group
- phone_number
- email
- address
- city
- state
- country
- height_cm
- weight_kg

### patient_vitals
- vital_id (Primary Key)
- patient_id (Foreign Key)
- heart_rate_bpm
- systolic_bp_mmhg
- diastolic_bp_mmhg
- body_temperature_c
- respiratory_rate
- oxygen_saturation
- notes
- recorded_at

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | `/patients/add` | Register a new patient |
| POST | `/login` | Login and generate JWT |
| POST | `/vitals/add` | Add patient vitals (JWT required) |
| GET | `/` | API health check |

---

## 📊 Dashboard Visualizations

- Heart Rate Trend (Line Chart)
- Blood Pressure Trend (Systolic & Diastolic)
- Body Temperature Trend
- Oxygen Saturation Trend
- Respiratory Rate Trend
- Latest vitals summary cards

---

## 🔐 Authentication Flow

Patient registers using Register page

Patient logs in using email and patient ID

JWT token is issued and stored in browser

Token is sent with API requests

Dashboard uses token to display patient-specific data

User Input → Flask API → PostgreSQL → Dash Dashboard
---

## Conclusion

HealthSync demonstrates end-to-end full-stack development with secure API design, relational database management, authentication, and real-time data visualization, making it suitable for healthcare monitoring and analytics applications.
