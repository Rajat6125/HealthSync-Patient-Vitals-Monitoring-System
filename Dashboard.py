from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from jose import jwt, JWTError
from urllib.parse import parse_qs
from datetime import date

SECRET_KEY = "healthsync_secret_key"
ALGORITHM = "HS256"

# ---------------- DATABASE CONNECTION ----------------
url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="Shahil@6125",
    host="localhost",
    port=5432,
    database="patient"
)
engine = create_engine(url)

# ---------------- DASH APP ----------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "HealthSync | Patient Vitals"

# ---------------- HELPER FUNCTIONS ----------------
def load_patient_data(patient_id: int):
    patient_df = pd.read_sql(f"""
        SELECT full_name, gender, date_of_birth, blood_group
        FROM patient_details
        WHERE patient_id = {patient_id}
    """, engine)

    vitals_df = pd.read_sql(f"""
        SELECT recorded_at,
               heart_rate_bpm,
               systolic_bp_mmhg,
               diastolic_bp_mmhg,
               body_temperature_c,
               respiratory_rate,
               oxygen_saturation
        FROM patient_vitals
        WHERE patient_id = {patient_id}
        ORDER BY recorded_at
    """, engine)

    return patient_df, vitals_df

def get_patient_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["patient_id"]
    except JWTError:
        return None

# ---------------- DASH LAYOUT ----------------
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.H1(
        "HealthSync – Patient Vitals Dashboard",
        style={"textAlign": "center", "color": "#2c3e50", "fontFamily": "Arial, sans-serif", "marginBottom": "30px"}
    ),
    html.Div(id="dashboard-content")
], style={"backgroundColor": "#f0f2f5", "padding": "20px", "minHeight": "100vh"})

# ---------------- CALLBACK ----------------
@app.callback(
    Output("dashboard-content", "children"),
    Input("url", "search")
)
def render_dashboard(search):
    if not search:
        return html.Div("No token provided. Please log in.", style={"color": "red", "fontWeight": "bold", "fontSize": "18px"})
    
    query_params = parse_qs(search[1:])
    token = query_params.get("token", [None])[0]
    if not token:
        return html.Div("No token provided. Please log in.", style={"color": "red", "fontWeight": "bold", "fontSize": "18px"})

    patient_id = get_patient_id_from_token(token)
    if not patient_id:
        return html.Div("Invalid or expired token.", style={"color": "red", "fontWeight": "bold", "fontSize": "18px"})

    # Fetch data
    patient_df, vitals_df = load_patient_data(patient_id)
    if patient_df.empty or vitals_df.empty:
        return html.Div("No data found for this patient.", style={"color": "red", "fontWeight": "bold", "fontSize": "18px"})

    # Calculate age
    dob = pd.to_datetime(patient_df.iloc[0]["date_of_birth"]).date()
    age = (date.today() - dob).days // 365

    # Latest vitals
    latest_vitals = vitals_df.iloc[-1]

    # ---------- CHARTS ----------
    chart_color = "#3498db"  # blue accent
    hr_fig = px.line(vitals_df, x="recorded_at", y="heart_rate_bpm", title="Heart Rate (BPM)", template="plotly_white")
    hr_fig.update_traces(line=dict(color=chart_color, width=3), marker=dict(color=chart_color))

    bp_fig = go.Figure()
    bp_fig.add_trace(go.Scatter(x=vitals_df["recorded_at"], y=vitals_df["systolic_bp_mmhg"],
                                name="Systolic BP", mode="lines+markers", line=dict(color="#e74c3c", width=3)))
    bp_fig.add_trace(go.Scatter(x=vitals_df["recorded_at"], y=vitals_df["diastolic_bp_mmhg"],
                                name="Diastolic BP", mode="lines+markers", line=dict(color="#f1c40f", width=3)))
    bp_fig.update_layout(title="Blood Pressure (mmHg)", template="plotly_white")

    temp_fig = px.line(vitals_df, x="recorded_at", y="body_temperature_c", title="Body Temperature (°C)", template="plotly_white")
    temp_fig.update_traces(line=dict(color="#9b59b6", width=3))

    spo2_fig = px.line(vitals_df, x="recorded_at", y="oxygen_saturation", title="Oxygen Saturation (%)", template="plotly_white")
    spo2_fig.update_traces(line=dict(color="#1abc9c", width=3))

    resp_fig = px.line(vitals_df, x="recorded_at", y="respiratory_rate", title="Respiratory Rate (breaths/min)", template="plotly_white")
    resp_fig.update_traces(line=dict(color="#34495e", width=3))

    # ---------- DASHBOARD CONTENT ----------
    content = [
        # Patient info
        html.Div(style={
            "background": "white", "padding": "25px", "borderRadius": "15px",
            "marginBottom": "25px", "boxShadow": "0 8px 25px rgba(0,0,0,0.1)"
        }, children=[
            html.H3("Patient Information", style={"color": "#2c3e50"}),
            html.P(f"Name: {patient_df.iloc[0]['full_name']}", style={"fontSize": "16px", "color": "#34495e"}),
            html.P(f"Gender: {patient_df.iloc[0]['gender']}", style={"fontSize": "16px", "color": "#34495e"}),
            html.P(f"Age: {age} years", style={"fontSize": "16px", "color": "#34495e"}),
            html.P(f"Blood Group: {patient_df.iloc[0]['blood_group']}", style={"fontSize": "16px", "color": "#34495e"})
        ]),

        # KPI Cards
        html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "30px"}, children=[
            html.Div(style={"background": "#ff7675", "padding": "20px", "borderRadius": "15px",
                            "flex": 1, "textAlign": "center", "color": "black", "boxShadow": "0 6px 15px rgba(0,0,0,0.1)"},
                     children=[html.H4("Latest Heart Rate", style={"marginBottom": "10px"}),
                               html.H2(latest_vitals["heart_rate_bpm"], style={"fontSize": "28px", "fontWeight": "bold"})]),

            html.Div(style={"background": "#fdcb6e", "padding": "20px", "borderRadius": "15px",
                            "flex": 1, "textAlign": "center", "color": "black", "boxShadow": "0 6px 15px rgba(0,0,0,0.1)"},
                     children=[html.H4("Latest Blood Pressure", style={"marginBottom": "10px"}),
                               html.H2(f"{latest_vitals['systolic_bp_mmhg']} / {latest_vitals['diastolic_bp_mmhg']}",
                                       style={"fontSize": "28px", "fontWeight": "bold"})]),

            html.Div(style={"background": "#55efc4", "padding": "20px", "borderRadius": "15px",
                            "flex": 1, "textAlign": "center", "color": "black", "boxShadow": "0 6px 15px rgba(0,0,0,0.1)"},
                     children=[html.H4("SpO₂", style={"marginBottom": "10px"}),
                               html.H2(f"{latest_vitals['oxygen_saturation']}%", style={"fontSize": "28px", "fontWeight": "bold"})])
        ]),

        # Charts
        dcc.Graph(figure=hr_fig),
        dcc.Graph(figure=bp_fig),
        dcc.Graph(figure=temp_fig),
        dcc.Graph(figure=spo2_fig),
        dcc.Graph(figure=resp_fig)
    ]

    return content

# ---------------- RUN DASH ----------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)
