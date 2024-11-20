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

st.set_page_config(
    page_title="Heart Failure Risk Calculator",
    page_icon="❤️",
    layout="wide"
)

st.markdown("""
    <style>
    .stPlotlyChart {margin: 2rem 0;}
    .plot-container {margin-top: 2rem;}
    .main-header {display: flex; align-items: center; justify-content: center; padding: 1rem;}
    .header-image {max-width: 150px; height: auto;}
    .risk-box {padding: 20px; border-radius: 10px; margin: 10px 0;}
    .low-risk {background-color: #d4edda; border: 1px solid #c3e6cb;}
    .medium-risk {background-color: #fff3cd; border: 1px solid #ffeeba;}
    .high-risk {background-color: #f8d7da; border: 1px solid #f5c6cb;}
    </style>
""", unsafe_allow_html=True)

if 'previous_calculations' not in st.session_state:
    st.session_state.previous_calculations = []

def create_icon_image(color, icon_type="heart"):
    img = Image.new('RGB', (200, 200), color)
    draw = ImageDraw.Draw(img)
    if icon_type == "heart":
        points = [(100, 30), (180, 100), (100, 170), (20, 100)]
        draw.polygon(points, fill='white')
    else:
        draw.rectangle([80, 40, 120, 160], fill='white')
        draw.rectangle([40, 80, 160, 120], fill='white')
    return img

@st.cache_data(ttl=3600)
def load_images():
    try:
        heart_img = create_icon_image('#FF6B6B', 'heart')
        med_img = create_icon_image('#4ECDC4', 'cross')
        return heart_img, med_img
    except Exception as e:
        st.warning(f"Error creating images: {str(e)}")
        return None, None

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
    if systolic_bp <= diastolic_bp:
        st.error("⚠️ Systolic BP must be greater than Diastolic BP")
        return False
    if bmi < 15 or bmi > 50:
        st.warning("⚠️ BMI value seems unusual. Please verify.")
    if heart_rate < 40 or heart_rate > 200:
        st.warning("⚠️ Heart rate is outside normal range. Please verify.")
    return True

def calculate_risk_score(inputs):
    age = inputs["age"]
    bmi = inputs["bmi"]
    systolic_bp = inputs["systolic_bp"]
    diastolic_bp = inputs["diastolic_bp"]
    heart_rate = inputs["heart_rate"]
    smoking = inputs["smoking"]
    diabetes = inputs["diabetes"]
    hypertension = inputs["hypertension"]
    ejection_fraction = inputs["ejection_fraction"]
    
    age_score = (age - 18) / (120 - 18) * 25
    
    if bmi < 18.5:
        bmi_score = 15
    elif 18.5 <= bmi < 25:
        bmi_score = 0
    elif 25 <= bmi < 30:
        bmi_score = 10
    else:
        bmi_score = 20
    
    bp_score = 0
    if systolic_bp >= 180 or diastolic_bp >= 120:
        bp_score = 25
    elif systolic_bp >= 140 or diastolic_bp >= 90:
        bp_score = 15
    elif systolic_bp >= 130 or diastolic_bp >= 80:
        bp_score = 10
    
    risk_score = 0
    if smoking == "Current":
        risk_score += 15
    elif smoking == "Former":
        risk_score += 7
    if diabetes == "Yes":
        risk_score += 10
    if hypertension == "Yes":
        risk_score += 10
    
    ef_score = max(0, (55 - ejection_fraction)) * 0.5
    
    total_score = (
        age_score * 0.2 +
        bmi_score * 0.15 +
        bp_score * 0.15 +
        risk_score * 0.2 +
        ef_score * 0.3
    )
    
    return min(100, max(0, total_score))

def plot_metrics(inputs, risk_score):
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
    st.markdown(f"## Risk Assessment Results")
    st.progress(risk_score/100)
    
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
    
    st.markdown("### Detailed Health Metrics")
    plot_metrics(inputs, risk_score)

def get_recommendations(risk_score):
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

def generate_report(inputs, risk_score):
    report = {
        "Heart Failure Risk Assessment Report": {
            "Assessment Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Risk Assessment": {
                "Overall Risk Score": f"{risk_score:.1f}%",
                "Risk Category": "Low" if risk_score < 20 else "Moderate" if risk_score < 50 else "High",
                "Recommendations": get_recommendations(risk_score)
            },
            "Patient Data": {
                "Demographics": {
                    "Age": inputs["age"],
                    "Sex": inputs["sex"],
                    "BMI": f"{inputs['bmi']:.1f}",
                    "Weight": f"{inputs['weight']} kg",
                    "Height": f"{inputs['height']} m"
                },
                "Vital Signs": {
                    "Blood Pressure": f"{inputs['systolic_bp']}/{inputs['diastolic_bp']} mmHg",
                    "Heart Rate": f"{inputs['heart_rate']} bpm"
                },
                "Clinical Measurements": {
                    "Ejection Fraction": f"{inputs['ejection_fraction']}%",
                    "BNP Level": f"{inputs['bnp_level']} pg/mL"
                },
                "Risk Factors": {
                    "Smoking Status": inputs["smoking"],
                    "Diabetes": inputs["diabetes"],
                    "Hypertension": inputs["hypertension"]
                },
                "Laboratory Values": {
                    "Creatinine": f"{inputs['creatinine']} mg/dL",
                    "Sodium": f"{inputs['sodium']} mEq/L",
                    "Potassium": f"{inputs['potassium']} mEq/L",
                    "Hemoglobin": f"{inputs['hemoglobin']} g/dL"
                }
            }
        }
    }
    return report

def main():
    heart_img, med_img = load_images()
    
    tab1, tab2 = st.tabs(["Calculator", "About"])

    with tab1:
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

        st.markdown("""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h3>Created by Md Abu Sufian</h3>
                <p>Researcher in AI & Healthcare | University Prospective PhD Student</p>
                <p>This calculator uses machine learning to assess heart failure risk.</p>
            </div>
        """, unsafe_allow_html=True)

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

        st.subheader("🔬 Clinical Measurements")
        col3, col4 = st.columns(2)
        
        with col3:
            ejection_fraction = st.number_input("Ejection Fraction (%)", 10, 80, 55)
            bnp_level = st.number_input("BNP Level (pg/mL)", 0, 5000, 100)

        with col4:
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes"])
            hypertension = st.selectbox("Hypertension", ["No", "Yes"])

        with st.expander("📊 Laboratory Values"):
            col5, col6 = st.columns(2)
            with col5:
                creatinine = st.number_input("Creatinine (mg/dL)", 0.0, 15.0, 1.0)
                sodium = st.number_input("Sodium (mEq/L)", 120, 150, 140)
            with col6:
                potassium = st.number_input("Potassium (mEq/L)", 2.5, 7.0, 4.0)
                hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0, 14.0)

        st.markdown("<br>", unsafe_allow_html=True)
        col_button1, col_button2, col_button3 = st.columns([1,2,1])
        with col_button2:
            calculate_button = st.button("Calculate Risk Score", type="primary", use_container_width=True)

        if calculate_button:
            if validate_inputs(age, bmi, systolic_bp, diastolic_bp, heart_rate):
                with st.spinner('Analyzing risk factors...'):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
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
                    
                    risk_score = calculate_risk_score(inputs)
                    display_results(risk_score, inputs)
                    
                    st.markdown("### 📊 Export Report")
                    report_data = generate_report(inputs, risk_score)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        json_report = json.dumps(report_data, indent=2)
                        st.download_button(
                            label="📥 Download JSON Report",
                            data=json_report,
                            file_name=f"heart_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            help="Download report in JSON format"
                        )
                    
                    with col2:
                        text_report = f"""Heart Failure Risk Assessment Report
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
{chr(10).join(get_recommendations(risk_score))}"""
                        st.download_button(
                            label="📄 Download Text Report",
                            data=text_report,
                            file_name=f"heart_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            help="Download report in text format"
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

if __name__ == "__main__":
    main()
