import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image, ImageDraw
import time
from datetime import datetime
import json
import base64
from io import BytesIO

# Configure page settings
st.set_page_config(
    page_title="Heart Failure Risk Calculator",
    page_icon="❤️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stPlotlyChart {
        margin: 2rem 0;
    }
    .plot-container {
        margin-top: 2rem;
    }
    .main-header {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    .header-image {
        max-width: 150px;
        height: auto;
    }
    .risk-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .low-risk {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .medium-risk {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .high-risk {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'previous_calculations' not in st.session_state:
    st.session_state.previous_calculations = []

def create_icon_image(color, icon_type="heart"):
    """Create custom icon images"""
    img = Image.new('RGB', (200, 200), color)
    draw = ImageDraw.Draw(img)
    
    if icon_type == "heart":
        # Draw heart shape
        points = [
            (100, 30),   # top
            (180, 100),  # right
            (100, 170),  # bottom
            (20, 100),   # left
        ]
        draw.polygon(points, fill='white')
    else:
        # Draw medical cross
        draw.rectangle([80, 40, 120, 160], fill='white')
        draw.rectangle([40, 80, 160, 120], fill='white')
    
    return img

@st.cache_data(ttl=3600)
def load_images():
    """Load and cache images for the application."""
    try:
        heart_img = create_icon_image('#FF6B6B', 'heart')
        med_img = create_icon_image('#4ECDC4', 'cross')
        return heart_img, med_img
    except Exception as e:
        st.warning(f"Error creating images: {str(e)}")
        return None, None

def calculate_bmi(weight, height):
    """Calculate BMI from weight and height."""
    return weight / (height ** 2)

def validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
    """Validate clinical input parameters."""
    if systolic_bp <= diastolic_bp:
        st.error("⚠️ Systolic BP must be greater than Diastolic BP")
        return False
    if bmi < 15 or bmi > 50:
        st.warning("⚠️ BMI value seems unusual. Please verify.")
    if heart_rate < 40 or heart_rate > 200:
        st.warning("⚠️ Heart rate is outside normal range. Please verify.")
    return True

def calculate_risk_score(inputs):
    """Calculate comprehensive risk score"""
    # Extract inputs
    age = inputs["age"]
    bmi = inputs["bmi"]
    systolic_bp = inputs["systolic_bp"]
    diastolic_bp = inputs["diastolic_bp"]
    heart_rate = inputs["heart_rate"]
    smoking = inputs["smoking"]
    diabetes = inputs["diabetes"]
    hypertension = inputs["hypertension"]
    ejection_fraction = inputs["ejection_fraction"]
    
    # Calculate component scores
    age_score = (age - 18) / (120 - 18) * 25
    
    # BMI scoring
    if bmi < 18.5:
        bmi_score = 15  # Underweight
    elif 18.5 <= bmi < 25:
        bmi_score = 0   # Normal
    elif 25 <= bmi < 30:
        bmi_score = 10  # Overweight
    else:
        bmi_score = 20  # Obese
    
    # Blood pressure scoring
    bp_score = 0
    if systolic_bp >= 180 or diastolic_bp >= 120:
        bp_score = 25  # Crisis
    elif systolic_bp >= 140 or diastolic_bp >= 90:
        bp_score = 15  # High
    elif systolic_bp >= 130 or diastolic_bp >= 80:
        bp_score = 10  # Elevated
    
    # Risk factors scoring
    risk_score = 0
    if smoking == "Current":
        risk_score += 15
    elif smoking == "Former":
        risk_score += 7
    if diabetes == "Yes":
        risk_score += 10
    if hypertension == "Yes":
        risk_score += 10
    
    # Ejection fraction impact
    ef_score = max(0, (55 - ejection_fraction)) * 0.5
    
    # Calculate final score
    total_score = (
        age_score * 0.2 +
        bmi_score * 0.15 +
        bp_score * 0.15 +
        risk_score * 0.2 +
        ef_score * 0.3
    )
    
    return min(100, max(0, total_score))

def plot_metrics(inputs, risk_score):
    """Create simplified visualization of health metrics"""
    # Create two separate visualizations instead of subplots
    
    # 1. Vital Signs Bar Chart
    vital_signs = pd.DataFrame({
        'Metric': ["Heart Rate", "Systolic BP", "Diastolic BP"],
        'Value': [inputs["heart_rate"], inputs["systolic_bp"], inputs["diastolic_bp"]]
    })
    
    fig1 = px.bar(
        vital_signs,
        x='Metric',
        y='Value',
        title="Vital Signs",
        text='Value'
    )
    
    fig1.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_color=['#FF9999', '#99FF99', '#9999FF']
    )
    
    fig1.update_layout(
        height=400,
        showlegend=False,
        yaxis_title="Value",
        xaxis_title=""
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Risk Factors Bar Chart
    risk_factors = pd.DataFrame({
        'Factor': ["Age", "BMI", "Risk Score"],
        'Value': [inputs["age"], inputs["bmi"], risk_score]
    })
    
    fig2 = px.bar(
        risk_factors,
        x='Factor',
        y='Value',
        title="Risk Factors",
        text='Value'
    )
    
    fig2.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_color=['#FFB366', '#66B2FF', '#FF66B2']
    )
    
    fig2.update_layout(
        height=400,
        showlegend=False,
        yaxis_title="Value",
        xaxis_title=""
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Add BMI and Blood Pressure indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### BMI Category")
        bmi = inputs["bmi"]
        if bmi < 18.5:
            st.error(f"Underweight (BMI: {bmi:.1f})")
        elif 18.5 <= bmi < 25:
            st.success(f"Normal (BMI: {bmi:.1f})")
        elif 25 <= bmi < 30:
            st.warning(f"Overweight (BMI: {bmi:.1f})")
        else:
            st.error(f"Obese (BMI: {bmi:.1f})")
    
    with col2:
        st.markdown("### Blood Pressure Category")
        sys_bp = inputs["systolic_bp"]
        dia_bp = inputs["diastolic_bp"]
        if sys_bp < 120 and dia_bp < 80:
            st.success(f"Normal ({sys_bp}/{dia_bp} mmHg)")
        elif sys_bp < 130 and dia_bp < 80:
            st.info(f"Elevated ({sys_bp}/{dia_bp} mmHg)")
        elif sys_bp < 140 or dia_bp < 90:
            st.warning(f"Stage 1 Hypertension ({sys_bp}/{dia_bp} mmHg)")
        else:
            st.error(f"Stage 2 Hypertension ({sys_bp}/{dia_bp} mmHg)")

def display_results(risk_score, inputs):
    """Display comprehensive risk assessment results"""
    st.markdown(f"## Risk Assessment Results")
    
    # Progress bar
    st.progress(risk_score / 100)
    
    # Risk category and recommendations
    if risk_score < 20:
        st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #d4edda; border: 1px solid #c3e6cb;">
                <h3>🟢 Low Risk Level</h3>
                <p>Your calculated risk score: {:.1f}%</p>
                <h4>Recommendations:</h4>
                <ul>
                    <li>Maintain current healthy lifestyle</li>
                    <li>Continue regular check-ups</li>
                    <li>Monitor blood pressure periodically</li>
                    <li>Stay physically active</li>
                </ul>
            </div>
        """.format(risk_score), unsafe_allow_html=True)
    elif risk_score < 50:
        st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #fff3cd; border: 1px solid #ffeeba;">
                <h3>🟡 Moderate Risk Level</h3>
                <p>Your calculated risk score: {:.1f}%</p>
                <h4>Recommendations:</h4>
                <ul>
                    <li>Schedule follow-up with healthcare provider</li>
                    <li>Review and modify lifestyle factors</li>
                    <li>Monitor blood pressure regularly</li>
                    <li>Consider stress management techniques</li>
                </ul>
            </div>
        """.format(risk_score), unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="padding: 20px; border-radius: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb;">
                <h3>🔴 High Risk Level</h3>
                <p>Your calculated risk score: {:.1f}%</p>
                <h4>Recommendations:</h4>
                <ul>
                    <li>Seek immediate medical consultation</li>
                    <li>Start monitoring blood pressure daily</li>
                    <li>Review medication compliance</li>
                    <li>Make urgent lifestyle modifications</li>
                </ul>
            </div>
        """.format(risk_score), unsafe_allow_html=True)
    
    # Display detailed metrics
    st.markdown("### Detailed Health Metrics")
    plot_metrics(inputs, risk_score)

def main():
    """Main application function"""
    st.title("Heart Failure Risk Calculator")
    st.markdown("### Comprehensive Risk Assessment Tool")
    
    # Input sections
    st.header("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (years)", min_value=18, max_value=120, value=30, step=1)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.75, step=0.01)
        sex = st.selectbox("Sex", ["Male", "Female"])
    with col2:
        systolic_bp = st.number_input("Systolic Blood Pressure (mmHg)", min_value=80, max_value=300, value=120, step=1)
        diastolic_bp = st.number_input("Diastolic Blood Pressure (mmHg)", min_value=40, max_value=200, value=80, step=1)
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=70, step=1)
    
    st.header("Clinical and Laboratory Data")
    col1, col2 = st.columns(2)
    with col1:
        smoking = st.selectbox("Smoking Status", ["Non-smoker", "Former", "Current"])
        diabetes = st.selectbox("Diabetes", ["No", "Yes"])
        hypertension = st.selectbox("Hypertension", ["No", "Yes"])
    with col2:
        ejection_fraction = st.number_input("Ejection Fraction (%)", min_value=10.0, max_value=80.0, value=55.0, step=0.1)
        bnp_level = st.number_input("BNP Level (pg/mL)", min_value=0.0, max_value=5000.0, value=100.0, step=1.0)
    
    st.header("Laboratory Values")
    col1, col2 = st.columns(2)
    with col1:
        creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=10.0, value=1.0, step=0.01)
        sodium = st.number_input("Sodium (mEq/L)", min_value=120, max_value=160, value=140, step=1)
    with col2:
        potassium = st.number_input("Potassium (mEq/L)", min_value=2.0, max_value=10.0, value=4.0, step=0.1)
        hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=5.0, max_value=20.0, value=14.0, step=0.1)

    # Calculate BMI
    bmi = calculate_bmi(weight, height)
    st.markdown(f"### Calculated BMI: {bmi:.1f}")
    
    # Calculate Button
    st.markdown("<br>", unsafe_allow_html=True)
    col_button1, col_button2, col_button3 = st.columns([1, 2, 1])
    with col_button2:
        calculate_button = st.button("Calculate Risk Score", type="primary", use_container_width=True)
    
    if calculate_button:
        if validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
            with st.spinner('Analyzing risk factors...'):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Prepare inputs dictionary
                inputs = {
                    "age": age,
                    "sex": sex,
                    "weight": weight,
                    "height": height,
                    "bmi": bmi,
                    "systolic_bp": systolic_bp,
                    "diastolic_bp": diastolic_bp,
                    "heart_rate": heart_rate,
                    "ejection_fraction": ejection_fraction,
                    "bnp_level": bnp_level,
                    "smoking": smoking,
                    "diabetes": diabetes,
                    "hypertension": hypertension,
                    "creatinine": creatinine,
                    "sodium": sodium,
                    "potassium": potassium,
                    "hemoglobin": hemoglobin
                }
                
                # Calculate risk score
                risk_score = calculate_risk_score(inputs)
                
                # Display results
                display_results(risk_score, inputs)
                
                # Generate and display download options
                st.markdown("### 📊 Export Report")
                
                # Generate report
                report_data = generate_report(inputs, risk_score)
                
                # Create download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # JSON format
                    json_report = json.dumps(report_data, indent=2)
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json_report,
                        file_name=f"heart_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        help="Download report in JSON format"
                    )
                
                with col2:
                    # Text format
                    text_report = f"""
Heart Failure Risk Assessment Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RISK ASSESSMENT
--------------
Risk Score: {risk_score:.1f}%
Category: {"Low" if risk_score < 20 else "Moderate" if risk_score < 50 else "High"}

PATIENT DATA
-----------
Age: {age} years
Sex: {sex}
BMI: {bmi:.1f}
Blood Pressure: {systolic_bp}/{diastolic_bp} mmHg
Heart Rate: {heart_rate} bpm

RISK FACTORS
-----------
Smoking: {smoking}
Diabetes: {diabetes}
Hypertension: {hypertension}

CLINICAL MEASUREMENTS
-------------------
Ejection Fraction: {ejection_fraction}%
BNP Level: {bnp_level} pg/mL

LABORATORY VALUES
---------------
Creatinine: {creatinine} mg/dL
Sodium: {sodium} mEq/L
Potassium: {potassium} mEq/L
Hemoglobin: {hemoglobin} g/dL

RECOMMENDATIONS
--------------
{chr(10).join(get_recommendations(risk_score))}
"""
                    st.download_button(
                        label="📄 Download Text Report",
                        data=text_report,
                        file_name=f"heart_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        help="Download report in text format"
                    )
                
                # Store calculation in session state
                st.session_state.previous_calculations.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "risk_score": risk_score,
                    "parameters": {
                        "age": age,
                        "sex": sex,
                        "bmi": bmi,
                        "blood_pressure": f"{systolic_bp}/{diastolic_bp}",
                        "heart_rate": heart_rate,
                        "smoking": smoking,
                        "diabetes": diabetes,
                        "hypertension": hypertension
                    }
                })

if __name__ == "__main__":
    main()
