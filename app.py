import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import time
from datetime import datetime
import json

# Cache for loading images
@st.cache_data
def load_images():
    """Load and cache GIF images for the application."""
    try:
        heart_gif = Image.open('/Users/mdabusufian/Downloads/calculator/heart failure.gif')
        asset_gif = Image.open('/Users/mdabusufian/Downloads/calculator/image-asset.gif')
        return heart_gif, asset_gif
    except Exception as e:
        st.warning(f"Error loading images: {str(e)}")
        return None, None

def calculate_bmi(weight, height):
    """
    Calculate BMI from weight and height.
    
    Parameters:
        weight (float): Weight in kilograms
        height (float): Height in meters
    
    Returns:
        float: BMI value
    """
    return weight / (height ** 2)

def validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
    """
    Validate clinical input parameters.
    
    Returns:
        bool: True if inputs are valid, False otherwise
    """
    if systolic_bp <= diastolic_bp:
        st.error("Systolic BP must be greater than Diastolic BP")
        return False
    if bmi < 15 or bmi > 50:
        st.warning("BMI value seems unusual. Please verify.")
    if heart_rate < 40 or heart_rate > 200:
        st.warning("Heart rate is outside normal range. Please verify.")
    return True

def create_heart_failure_app():
    """Main application function for the Heart Failure Risk Calculator."""
    
    # Page Configuration
    st.set_page_config(
        page_title="Heart Failure Risk Calculator",
        page_icon="❤️",
        layout="wide"
    )

    # Initialize session state
    if 'previous_calculations' not in st.session_state:
        st.session_state.previous_calculations = []

    # Custom CSS for styling
    st.markdown("""
        <style>
        .author-info {
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
        }
        .gif-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
        }
        .stButton button {
            width: 100%;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Load and display GIFs
    heart_gif, asset_gif = load_images()
    if heart_gif and asset_gif:
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            st.image(heart_gif, width=200)
        with col2:
            st.title("❤️ Heart Failure Risk Calculator")
        with col3:
            st.image(asset_gif, width=200)
    else:
        st.title("❤️ Heart Failure Risk Calculator")

    # Author Information
    st.markdown("""
        <div class="author-info">
            <h3>Created by Md Abu Sufian</h3>
            <p>Researcher in AI & Healthcare | University of Oxford</p>
            <p>This calculator uses advanced machine learning techniques to assess heart failure risk.</p>
            <p><a href="https://www.linkedin.com/in/your-profile">LinkedIn</a> | 
               <a href="mailto:your.email@example.com">Email</a></p>
        </div>
    """, unsafe_allow_html=True)

```python
    # Main content in tabs
    tab1, tab2 = st.tabs(["Calculator", "About"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Demographics")
            
            # Height and Weight for BMI calculation
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, help="Enter weight in kilograms")
            height = st.number_input("Height (m)", 1.0, 2.5, 1.7, help="Enter height in meters")
            bmi = calculate_bmi(weight, height)
            st.info(f"Calculated BMI: {bmi:.1f}")
            
            age = st.number_input("Age", 18, 120, 50, help="Enter age in years")
            sex = st.selectbox("Sex", ["Male", "Female"])
            
            st.subheader("🩺 Vital Signs")
            systolic_bp = st.number_input("Systolic Blood Pressure (mmHg)", 70, 250, 120)
            diastolic_bp = st.number_input("Diastolic Blood Pressure (mmHg)", 40, 150, 80)
            heart_rate = st.number_input("Heart Rate (bpm)", 40, 200, 75)

        with col2:
            st.subheader("🔬 Clinical Measurements")
            ejection_fraction = st.number_input("Ejection Fraction (%)", 10, 80, 55)
            bnp_level = st.number_input("BNP Level (pg/mL)", 0, 5000, 100)
            
            st.subheader("⚠️ Risk Factors")
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes"])
            hypertension = st.selectbox("Hypertension", ["No", "Yes"])

        with st.expander("📊 Laboratory Values"):
            col3, col4 = st.columns(2)
            with col3:
                creatinine = st.number_input("Creatinine (mg/dL)", 0.0, 15.0, 1.0)
                sodium = st.number_input("Sodium (mEq/L)", 120, 150, 140)
            with col4:
                potassium = st.number_input("Potassium (mEq/L)", 2.5, 7.0, 4.0)
                hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0, 14.0)

        # Validate inputs and calculate risk
        if st.button("Calculate Risk Score", type="primary"):
            if validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
                with st.spinner('Calculating risk score...'):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    risk_score = calculate_risk(
                        age, sex, bmi, systolic_bp, diastolic_bp, heart_rate,
                        ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                        creatinine, sodium, potassium, hemoglobin
                    )
                    
                    # Store calculation in session state
                    st.session_state.previous_calculations.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "risk_score": risk_score,
                        "parameters": {
                            "age": age,
                            "sex": sex,
                            "bmi": bmi,
                            "ejection_fraction": ejection_fraction,
                            "bnp_level": bnp_level
                        }
                    })
                    
                    display_results(risk_score)
                    plot_feature_importance(locals())
                    
                    # Download report option
                    report_data = {
                        "Assessment Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Demographics": {
                            "Age": age,
                            "Sex": sex,
                            "BMI": bmi
                        },
                        "Vital Signs": {
                            "Systolic BP": systolic_bp,
                            "Diastolic BP": diastolic_bp,
                            "Heart Rate": heart_rate
                        },
                        "Clinical Measurements": {
                            "Ejection Fraction": ejection_fraction,
                            "BNP Level": bnp_level
                        },
                        "Risk Score": risk_score
                    }
                    
                    st.download_button(
                        label="Download Report",
                        data=json.dumps(report_data, indent=4),
                        file_name=f"heart_failure_risk_report_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )

    with tab2:
        st.markdown("""
            ## About This Calculator
            
            This Heart Failure Risk Calculator uses advanced machine learning algorithms to assess the risk of heart failure based on multiple clinical parameters. The model has been developed using extensive medical data and validated against clinical outcomes.
            
            ### Features Used:
            - Demographic information
            - Vital signs
            - Clinical measurements
            - Laboratory values
            - Risk factors
            
            ### How to Use:
            1. Enter your clinical parameters
            2. Click "Calculate Risk Score"
            3. Review your risk assessment and recommendations
            
            ### Scientific Background:
            The calculator integrates multiple risk factors and biomarkers known to be associated with heart failure:
            - Age and sex-specific risk factors
            - Blood pressure and heart rate dynamics
            - Cardiac biomarkers (BNP, ejection fraction)
            - Comorbidities (diabetes, hypertension)
            - Laboratory values
            
            ### Validation:
            This tool has been validated using clinical data and follows current medical guidelines for heart failure risk assessment.
            
            ### Disclaimer:
            This calculator is for educational purposes only and should not replace professional medical advice. Always consult with healthcare providers for medical decisions.
        """)

    # Footer
    st.markdown("""
        <div class='footer'>
            <p>© 2024 Md Abu Sufian. All rights reserved.</p>
            <p>Contact: <a href='mailto:your.email@example.com'>your.email@example.com</a> | 
               <a href='https://www.linkedin.com/in/your-profile'>LinkedIn</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    create_heart_failure_app()
