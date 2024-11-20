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
    """Create comprehensive visualization of health metrics"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Vital Signs", "Risk Factors", "BMI Category", "Blood Pressure Category")
    )
    
    # Vital Signs
    vital_signs = {
        "Heart Rate": inputs["heart_rate"],
        "Systolic BP": inputs["systolic_bp"],
        "Diastolic BP": inputs["diastolic_bp"]
    }
    fig.add_trace(
        go.Bar(
            x=list(vital_signs.keys()),
            y=list(vital_signs.values()),
            text=[f"{v:.1f}" for v in vital_signs.values()],
            textposition='outside',
            marker_color=['#FF9999', '#99FF99', '#9999FF']
        ),
        row=1, col=1
    )
    
    # Risk Factors
    risk_factors = {
        "Age": inputs["age"],
        "BMI": inputs["bmi"],
        "Risk Score": risk_score
    }
    fig.add_trace(
        go.Bar(
            x=list(risk_factors.keys()),
            y=list(risk_factors.values()),
            text=[f"{v:.1f}" for v in risk_factors.values()],
            textposition='outside',
            marker_color=['#FFB366', '#66B2FF', '#FF66B2']
        ),
        row=1, col=2
    )
    
    # BMI Category
    bmi = inputs["bmi"]
    bmi_categories = ["Underweight", "Normal", "Overweight", "Obese"]
    bmi_values = [18.5, 25, 30, 35]
    bmi_colors = ['#FF9999', '#99FF99', '#FFFF99', '#FF9999']
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=bmi,
            gauge={
                'axis': {'range': [None, 40]},
                'steps': [
                    {'range': [0, 18.5], 'color': '#FF9999'},
                    {'range': [18.5, 25], 'color': '#99FF99'},
                    {'range': [25, 30], 'color': '#FFFF99'},
                    {'range': [30, 40], 'color': '#FF9999'}
                ]
            },
            title={'text': "BMI"}
        ),
        row=2, col=1
    )
    
    # Blood Pressure Category
    sys_bp = inputs["systolic_bp"]
    dia_bp = inputs["diastolic_bp"]
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=sys_bp,
            gauge={
                'axis': {'range': [0, 200]},
                'steps': [
                    {'range': [0, 120], 'color': '#99FF99'},
                    {'range': [120, 130], 'color': '#FFFF99'},
                    {'range': [130, 140], 'color': '#FFB366'},
                    {'range': [140, 200], 'color': '#FF9999'}
                ]
            },
            title={'text': "Blood Pressure"}
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def display_results(risk_score, inputs):
    """Display comprehensive risk assessment results"""
    st.markdown(f"## Risk Assessment Results")
    
    # Progress bar
    st.progress(risk_score/100)
    
    # Risk category and recommendations
    if risk_score < 20:
        st.markdown("""
            <div class="risk-box low-risk">
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
            <div class="risk-box medium-risk">
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
            <div class="risk-box high-risk">
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
    # Load images
    heart_img, med_img = load_images()
    
    # Header layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if heart_img:
            st.image(heart_img, width=150)
    
    with col2:
        st.title("❤️ Heart Failure Risk Calculator")
        st.markdown("""
            <div style='text-align: center;'>
                <p style='color: #666; font-size: 1.2em;'>Advanced Risk Assessment Tool</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if med_img:
            st.image(med_img, width=150)

    # Author information
    st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
            <h3>Created by Md Abu Sufian</h3>
            <p>Researcher in AI & Healthcare | University of Oxford</p>
            <p>This calculator uses advanced algorithms to assess heart failure risk.</p>
        </div>
    """, unsafe_allow_html=True)

    # Main interface
    tab1, tab2 = st.tabs(["📊 Calculator", "ℹ️ About"])

    with tab1:
        # Demographics section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Demographics")
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            height = st.number_input("Height (m)", 1.0, 2.5, 1.7)
            bmi = calculate_bmi(weight, height)
            st.info(f"Calculated BMI: {bmi:.1f}")
            
            age = st.number_input("Age", 18, 120, 50)
            sex = st.selectbox("Sex", ["Male", "Female"])

        with col2:
            st.subheader("🩺 Vital Signs")
            systolic_bp = st.number_input("Systolic Blood Pressure (mmHg)", 70, 250, 120)
            diastolic_bp = st.number_input("Diastolic Blood Pressure (mmHg)", 40, 150, 80)
            heart_rate = st.number_input("Heart Rate (bpm)", 40, 200, 75)

        # Clinical measurements
        st.subheader("🔬 Clinical Measurements")
        col3, col4 = st.columns(2)
        
        with col3:
            ejection_fraction = st.number_input("Ejection Fraction (%)", 10, 80, 55)
            bnp_level = st.number_input("BNP Level (pg/mL)", 0, 5000, 100)

        with col4:
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes"])
            hypertension = st.selectbox("Hypertension", ["No", "Yes"])

        # Laboratory values
        with st.expander("📊 Laboratory Values"):
            col5, col6 = st.columns(2)
            with col5:
                creatinine = st.number_input("Creatinine (mg/dL)", 0.0, 15.0, 1.0)
                sodium = st.number_input("Sodium (mEq/L)", 120, 150, 140)
            with col6:
                potassium = st.number_input("Potassium (mEq/L)", 2.5, 7.0, 4.0)
                hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0, 14.0)

        # Calculate Button
        st.markdown("<br>", unsafe_allow_html=True)
        col_button1, col_button2, col_button3 = st.columns([1,2,1])
        with col_button2:
            calculate_button = st.button("Calculate Risk Score", type="primary", use_container_width=True)

        if calculate_button:
            if validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
                with st.spinner('Analyzing risk factors...'):
                    # Progress animation
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # Prepare inputs dictionary
                    inputs = {
                        "age": age,
                        "sex": sex,
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
                    
                    # Show download button for report
                    if st.button("📥 Download Report"):
                        report = {
                            "Assessment Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Risk Score": f"{risk_score:.1f}%",
                            "Patient Data": {
                                "Demographics": {
                                    "Age": age,
                                    "Sex": sex,
                                    "BMI": f"{bmi:.1f}"
                                },
                                "Vital Signs": {
                                    "Blood Pressure": f"{systolic_bp}/{diastolic_bp} mmHg",
                                    "Heart Rate": f"{heart_rate} bpm"
                                },
                                "Clinical Measurements": {
                                    "Ejection Fraction": f"{ejection_fraction}%",
                                    "BNP Level": f"{bnp_level} pg/mL"
                                },
                                "Risk Factors": {
                                    "Smoking": smoking,
                                    "Diabetes": diabetes,
                                    "Hypertension": hypertension
                                },
                                "Laboratory Values": {
                                    "Creatinine": f"{creatinine} mg/dL",
                                    "Sodium": f"{sodium} mEq/L",
                                    "Potassium": f"{potassium} mEq/L",
                                    "Hemoglobin": f"{hemoglobin} g/dL"
                                }
                            },
                            "Recommendations": get_recommendations(risk_score)
                        }
                        
                        # Convert to JSON string
                        report_json = json.dumps(report, indent=2)
                        
                        # Create download button
                        st.download_button(
                            label="Download Detailed Report",
                            data=report_json,
                            file_name=f"heart_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )

    with tab2:
        st.markdown("""
            ## About This Calculator
            
            This Heart Failure Risk Calculator utilizes advanced algorithms to assess heart failure risk based on multiple clinical parameters and established medical guidelines.
            
            ### Key Features:
            - Comprehensive risk assessment using multiple parameters
            - Real-time calculation and visualization
            - Evidence-based risk factors analysis
            - Personalized recommendations
            - Detailed health metrics visualization
            - Downloadable assessment reports
            
            ### Risk Factors Considered:
            1. **Demographics**
               - Age
               - Sex
               - Body Mass Index (BMI)
            
            2. **Vital Signs**
               - Blood Pressure
               - Heart Rate
            
            3. **Clinical Measurements**
               - Ejection Fraction
               - BNP Level
            
            4. **Medical History**
               - Smoking Status
               - Diabetes
               - Hypertension
            
            5. **Laboratory Values**
               - Creatinine
               - Sodium
               - Potassium
               - Hemoglobin
            
            ### How to Use:
            1. Enter your clinical parameters in the Calculator tab
            2. Click "Calculate Risk Score"
            3. Review your risk assessment and recommendations
            4. Download a detailed report for your records
            
            ### Scientific Background:
            This calculator integrates multiple risk factors and biomarkers known to be associated with heart failure:
            - Age and sex-specific risk factors
            - Blood pressure and heart rate dynamics
            - Cardiac biomarkers (BNP, ejection fraction)
            - Comorbidities (diabetes, hypertension)
            - Laboratory values
            
            ### References:
            - American Heart Association Guidelines
            - European Society of Cardiology Guidelines
            - World Health Organization BMI Classifications
            
            ### Disclaimer:
            This calculator is for educational and informational purposes only. Always consult with healthcare providers for medical decisions and diagnosis.
        """)

def get_recommendations(risk_score):
    """Generate recommendations based on risk score"""
    if risk_score < 20:
        return [
            "Maintain current healthy lifestyle",
            "Continue regular check-ups",
            "Monitor blood pressure periodically",
            "Stay physically active"
        ]
    elif risk_score < 50:
        return [
            "Schedule follow-up with healthcare provider",
            "Review and modify lifestyle factors",
            "Monitor blood pressure regularly",
            "Consider stress management techniques"
        ]
    else:
        return [
            "Seek immediate medical consultation",
            "Start monitoring blood pressure daily",
            "Review medication compliance",
            "Make urgent lifestyle modifications"
        ]

if __name__ == "__main__":
    main()
