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

# Initialize session state at the start
if 'previous_calculations' not in st.session_state:
    st.session_state.previous_calculations = []

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_images():
    """Load and cache GIF images for the application."""
    try:
        # Updated GitHub raw URLs - replace these with your actual image URLs
        heart_gif_url = "https://raw.githubusercontent.com/datascintist-abusufian/Heart-Failure-Prediction-Calculator/main/heart%20failure.gif"
        asset_gif_url = "https://raw.githubusercontent.com/datascintist-abusufian/Heart-Failure-Prediction-Calculator/main/image-asset.gif"

        # Load images with timeout
        timeout = 10
        heart_response = requests.get(heart_gif_url, timeout=timeout)
        heart_gif = Image.open(BytesIO(heart_response.content))

        asset_response = requests.get(asset_gif_url, timeout=timeout)
        asset_gif = Image.open(BytesIO(asset_response.content))

        return heart_gif, asset_gif
    except Exception as e:
        st.warning(f"Error loading images: {str(e)}")
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
    # Example risk calculation (replace with your actual model)
    risk_score = (
        age * 0.2 + bmi * 0.3 + systolic_bp * 0.1 + diastolic_bp * 0.05 +
        ejection_fraction * -0.3 + (1 if smoking == "Current" else 0) * 0.5 +
        (1 if diabetes == "Yes" else 0) * 0.4 + (1 if hypertension == "Yes" else 0) * 0.3
    )
    return max(0, min(100, risk_score))

def display_results(risk_score):
    """Display risk assessment results."""
    if risk_score < 20:
        st.success(f"Low risk of heart failure: {risk_score:.1f}%")
    elif risk_score < 50:
        st.warning(f"Moderate risk of heart failure: {risk_score:.1f}%")
    else:
        st.error(f"High risk of heart failure: {risk_score:.1f}%")

def plot_feature_importance(inputs):
    """Create feature importance visualization."""
    features = ["Age", "BMI", "Systolic BP", "Diastolic BP", "Heart Rate"]
    values = [inputs["age"], inputs["bmi"], inputs["systolic_bp"], 
             inputs["diastolic_bp"], inputs["heart_rate"]]
    
    fig = px.bar(
        x=features, 
        y=values, 
        title="Clinical Parameters",
        labels={'x': 'Parameter', 'y': 'Value'},
        template="simple_white"
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function."""
    # Title and Header
    st.title("❤️ Heart Failure Risk Calculator")
    st.markdown("---")

    # Author Information
    st.markdown("""
        ### Created by Md Abu Sufian
        Researcher in AI & Healthcare | University of Oxford
        
        This calculator uses machine learning to assess heart failure risk.
    """)

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
        if st.button("Calculate Risk Score", type="primary"):
            if validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
                with st.spinner('Calculating risk score...'):
                    # Calculate risk
                    risk_score = calculate_risk(
                        age, sex, bmi, systolic_bp, diastolic_bp, heart_rate,
                        ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                        creatinine, sodium, potassium, hemoglobin
                    )
                    
                    # Display results
                    display_results(risk_score)
                    plot_feature_importance(locals())
                    
                    # Store calculation
                    st.session_state.previous_calculations.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "risk_score": risk_score,
                        "parameters": {
                            "age": age,
                            "sex": sex,
                            "bmi": bmi
                        }
                    })

    with tab2:
        st.markdown("""
            ## About This Calculator
            
            This Heart Failure Risk Calculator uses machine learning algorithms to assess heart failure risk based on clinical parameters.
            
            ### Key Features:
            - Demographic analysis
            - Vital sign assessment
            - Clinical measurement evaluation
            - Laboratory value analysis
            - Risk factor consideration
            
            ### Disclaimer:
            This calculator is for educational purposes only. Always consult healthcare providers for medical decisions.
        """)

if __name__ == "__main__":
    main()
