import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import time
from datetime import datetime
import json
import requests
from io import BytesIO
import sys
import subprocess
import pkg_resources

# Configure page settings at the very start
st.set_page_config(
    page_title="Heart Failure Risk Calculator",
    page_icon="❤️",
    layout="wide"
)

# Add custom CSS
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state at the start
if 'previous_calculations' not in st.session_state:
    st.session_state.previous_calculations = []

@st.cache_data(ttl=3600)
def load_images():
    """Load and cache static images for the application."""
    try:
        # Create placeholder images
        placeholder1 = Image.new('RGB', (200, 200), '#FF6B6B')  # Red placeholder
        placeholder2 = Image.new('RGB', (200, 200), '#4ECDC4')  # Teal placeholder
        return placeholder1, placeholder2
    except Exception as e:
        st.warning("Error creating placeholder images")
        return None, None

def calculate_bmi(weight, height):
    """Calculate BMI from weight and height."""
    return weight / (height ** 2)

def validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
    """Validate clinical input parameters."""
    if systolic_bp <= diastolic_bp:
        st.error("Systolic BP must be greater than Diastolic BP")
        return False
    if bmi < 15 or bmi > 50:
        st.warning("BMI value seems unusual. Please verify.")
    if heart_rate < 40 or heart_rate > 200:
        st.warning("Heart rate is outside normal range. Please verify.")
    return True

def calculate_risk(age, sex, bmi, systolic_bp, diastolic_bp, heart_rate, 
                   ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                   creatinine, sodium, potassium, hemoglobin):
    """Calculate heart failure risk score."""
    # Risk factors scoring
    age_score = (age - 18) / (120 - 18) * 25  # Age contributes up to 25 points
    
    # BMI scoring
    if bmi < 18.5 or bmi > 30:
        bmi_score = 15
    elif 18.5 <= bmi <= 24.9:
        bmi_score = 0
    else:
        bmi_score = 10
    
    # Blood pressure scoring
    bp_score = 0
    if systolic_bp > 140 or diastolic_bp > 90:
        bp_score = 15
    elif systolic_bp > 130 or diastolic_bp > 80:
        bp_score = 10
        
    # Heart rate scoring
    hr_score = abs(heart_rate - 75) / 2
    
    # Ejection fraction scoring
    ef_score = max(0, (55 - ejection_fraction)) * 0.5
    
    # Risk factors scoring
    risk_factors_score = 0
    if smoking == "Current":
        risk_factors_score += 10
    elif smoking == "Former":
        risk_factors_score += 5
    if diabetes == "Yes":
        risk_factors_score += 10
    if hypertension == "Yes":
        risk_factors_score += 10
        
    # Calculate total score
    total_score = (age_score + bmi_score + bp_score + hr_score + 
                  ef_score + risk_factors_score)
    
    # Normalize to 0-100 scale
    return min(100, max(0, total_score))

def display_results(risk_score):
    """Display risk assessment results."""
    st.markdown("### Risk Assessment Results")
    
    # Create a progress bar
    st.progress(risk_score/100)
    
    if risk_score < 20:
        st.success(f"🟢 Low Risk: {risk_score:.1f}%")
        st.markdown("""
            ### Recommendations:
            - Continue maintaining a healthy lifestyle
            - Regular check-ups
            - Monitor blood pressure and heart rate
        """)
    elif risk_score < 50:
        st.warning(f"🟡 Moderate Risk: {risk_score:.1f}%")
        st.markdown("""
            ### Recommendations:
            - Schedule a follow-up with healthcare provider
            - Consider lifestyle modifications
            - Monitor symptoms closely
        """)
    else:
        st.error(f"🔴 High Risk: {risk_score:.1f}%")
        st.markdown("""
            ### Recommendations:
            - Immediate consultation with healthcare provider
            - Careful monitoring of symptoms
            - Follow prescribed medication regimen
        """)

def plot_feature_importance(inputs):
    """Create feature importance visualization with values on top of bars."""
    features = ["Age", "BMI", "Systolic BP", "Diastolic BP", "Heart Rate"]
    values = [inputs["age"], inputs["bmi"], inputs["systolic_bp"], 
             inputs["diastolic_bp"], inputs["heart_rate"]]
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Feature': features,
        'Value': values
    })
    
    fig = px.bar(
        df,
        x='Feature',
        y='Value',
        title="Clinical Parameters",
        text='Value',
        template="simple_white"
    )
    
    # Customize the layout
    fig.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        textfont=dict(size=14)
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Parameter",
        yaxis_title="Value",
        bargap=0.2
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function."""
    # Load images
    heart_img, logo_img = load_images()
    
    # Title and Header with images
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if heart_img:
            st.image(heart_img, width=150, use_column_width=False)
    
    with col2:
        st.title("❤️ Heart Failure Risk Calculator")
        st.markdown("---")
    
    with col3:
        if logo_img:
            st.image(logo_img, width=150, use_column_width=False)

    # Author Information
    st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
            <h3>Created by Md Abu Sufian</h3>
            <p>Researcher in AI & Healthcare | University of Oxford</p>
            <p>This calculator uses machine learning to assess heart failure risk.</p>
        </div>
    """, unsafe_allow_html=True)

    # Main Interface
    tab1, tab2 = st.tabs(["Calculator", "About"])

    with tab1:
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

        # Clinical Measurements
        st.subheader("🔬 Clinical Measurements")
        col3, col4 = st.columns(2)
        
        with col3:
            ejection_fraction = st.number_input("Ejection Fraction (%)", 10, 80, 55)
            bnp_level = st.number_input("BNP Level (pg/mL)", 0, 5000, 100)

        with col4:
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes"])
            hypertension = st.selectbox("Hypertension", ["No", "Yes"])

        # Lab Values
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
                    # Add progress bar
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # Calculate risk
                    risk_score = calculate_risk(
                        age, sex, bmi, systolic_bp, diastolic_bp, heart_rate,
                        ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                        creatinine, sodium, potassium, hemoglobin
                    )
                    
                    # Display results in columns
                    result_col1, result_col2 = st.columns([2,1])
                    
                    with result_col1:
                        display_results(risk_score)
                    
                    with result_col2:
                        plot_feature_importance(locals())
                    
                    # Store calculation
                    st.session_state.previous_calculations.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "risk_score": risk_score,
                        "parameters": {
                            "age": age,
                            "sex": sex,
                            "bmi": bmi,
                            "blood_pressure": f"{systolic_bp}/{diastolic_bp}",
                            "heart_rate": heart_rate
                        }
                    })

    with tab2:
        st.markdown("""
            ## About This Calculator
            
            This Heart Failure Risk Calculator uses machine learning algorithms to assess heart failure risk based on clinical parameters.
            
            ### Key Features:
            - Comprehensive risk assessment
            - Real-time calculation and visualization
            - Evidence-based risk factors
            - Personalized recommendations
            
            ### Risk Factors Considered:
            1. Demographics (Age, Sex, BMI)
            2. Vital Signs (Blood Pressure, Heart Rate)
            3. Clinical Measurements (Ejection Fraction, BNP)
            4. Medical History (Smoking, Diabetes, Hypertension)
            5. Laboratory Values
            
            ### Disclaimer:
            This calculator is for educational purposes only. Always consult healthcare providers for medical decisions.
        """)

if __name__ == "__main__":
    main()
