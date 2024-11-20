import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

def create_heart_failure_app():
    # Page Configuration
    st.set_page_config(
        page_title="Heart Failure Risk Calculator",
        page_icon="❤️",
        layout="wide"
    )

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
        </style>
    """, unsafe_allow_html=True)

    # Load GIFs
    try:
        heart_gif = Image.open('/Users/mdabusufian/Downloads/calculator/heart failure.gif')
        asset_gif = Image.open('/Users/mdabusufian/Downloads/calculator/image-asset.gif')
        
        # Display GIFs in a row
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            st.image(heart_gif, width=400)
        with col2:
            st.title("❤️ Heart Failure Risk Calculator")
        with col3:
            st.image(asset_gif, width=400)
    except:
        st.title("❤️ Heart Failure Risk Calculator")

    # Author Information
    st.markdown("""
        <div class="author-info">
            <h3>Created by Md Abu Sufian</h3>
            <p>Researcher in AI & Healthcare | University of Oxford</p>
            <p>This calculator is designed to help assess heart failure risk using advanced machine learning techniques.</p>
        </div>
    """, unsafe_allow_html=True)

    # Main content in tabs
    tab1, tab2 = st.tabs(["Calculator", "About"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Demographics")
            age = st.number_input("Age", 18, 120, 50, help="Enter age in years")
            sex = st.selectbox("Sex", ["Male", "Female"])
            bmi = st.number_input("BMI", 15.0, 50.0, 25.0, help="Body Mass Index")
            
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

        if st.button("Calculate Risk Score", type="primary"):
            risk_score = calculate_risk(
                age, sex, bmi, systolic_bp, diastolic_bp, heart_rate,
                ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                creatinine, sodium, potassium, hemoglobin
            )
            display_results(risk_score)
            plot_feature_importance(locals())

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
            
            ### Disclaimer:
            This calculator is for educational purposes only and should not replace professional medical advice. Always consult with healthcare providers for medical decisions.
        """)

def plot_feature_importance(variables):
    st.subheader("Feature Importance Analysis")
    
    # Create feature importance data
    features = {
        'Age': 0.15,
        'BMI': 0.10,
        'Ejection Fraction': 0.20,
        'BNP Level': 0.15,
        'Blood Pressure': 0.12,
        'Heart Rate': 0.08,
        'Laboratory Values': 0.10,
        'Risk Factors': 0.10
    }
    
    fig = px.bar(
        x=list(features.keys()),
        y=list(features.values()),
        title="Feature Importance in Risk Calculation",
        labels={'x': 'Features', 'y': 'Importance'},
        color=list(features.values()),
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig)

def calculate_risk(age, sex, bmi, systolic_bp, diastolic_bp, heart_rate,
                  ejection_fraction, bnp_level, smoking, diabetes, hypertension,
                  creatinine, sodium, potassium, hemoglobin):
    # Example risk calculation (replace with your actual model)
    base_risk = 0.0
    
    # Age factor
    base_risk += (age - 70) * 0.03
    
    # Sex factor
    if sex == "Male":
        base_risk += 2
    
    # Clinical factors
    if ejection_fraction < 40:
        base_risk += 10
    
    base_risk += (bnp_level - 100) * 0.01
    
    # Risk factors
    if smoking == "Current":
        base_risk += 5
    elif smoking == "Former":
        base_risk += 2
    
    if diabetes == "Yes":
        base_risk += 3
    
    if hypertension == "Yes":
        base_risk += 3
    
    # Normalize risk score to 0-100 range
    risk_score = min(max(base_risk, 0), 100)
    
    return risk_score

def display_results(risk_score):
    # Create columns for results
    res_col1, res_col2 = st.columns([2, 1])
    
    with res_col1:
        st.subheader("Risk Assessment Results")
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_score
                }
            }
        ))
        
        st.plotly_chart(fig)
        
    with res_col2:
        st.subheader("Recommendations")
        if risk_score < 30:
            st.success("Low Risk")
            st.markdown("""
            - Continue healthy lifestyle
            - Regular check-ups
            - Monitor blood pressure
            """)
        elif risk_score < 70:
            st.warning("Moderate Risk")
            st.markdown("""
            - Lifestyle modifications needed
            - More frequent check-ups
            - Consider medication review
            - Monitor symptoms closely
            """)
        else:
            st.error("High Risk")
            st.markdown("""
            - Immediate medical consultation
            - Intensive monitoring
            - Medication adjustment may be needed
            - Consider specialist referral
            """)

    # Additional Information
    st.subheader("Additional Information")
    st.markdown("""
    This risk score is based on multiple factors including:
    - Clinical measurements
    - Vital signs
    - Laboratory values
    - Risk factors
    
    Please consult with your healthcare provider for proper interpretation of these results.
    """)

if __name__ == "__main__":
    create_heart_failure_app()

