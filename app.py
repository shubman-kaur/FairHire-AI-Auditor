import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import time

# 1. Page Config
st.set_page_config(page_title="FairHire AI | Ethical Auditor", layout="wide")

# 2. Design/CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .main-title { color: #1A73E8; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✨ FairHire AI: Recruitment Bias Auditor</div>', unsafe_allow_html=True)

# 3. Sidebar for API Key
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Using Model: gemini-2.0-flash")

# 4. Main Layout
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📁 Upload Hiring Data")
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("Data loaded successfully!")
        st.dataframe(df.head(10))

with col2:
    st.subheader("📊 Rejection Analytics")
    if uploaded_file:
        # Simple Bar Chart to show Gender Distribution in Rejections
        rejections = df[df['Status'] == 'Rejected']
        fig = px.histogram(rejections, x="Gender", color="Gender", 
                           title="Rejections by Gender",
                           color_discrete_map={'Male': '#4285F4', 'Female': '#EA4335'})
        st.plotly_chart(fig, use_container_width=True)

# 5. AI Audit Section
st.divider()
if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    
    st.subheader("🕵️‍♂️ Deep AI Audit")
    # Identify high-skill females who were rejected
    suspects = df[(df['Gender'] == 'Female') & (df['Status'] == 'Rejected') & (df['Skill_Score'] > 60)]
    
    if not suspects.empty:
        selected_id = st.selectbox("Select Candidate to Audit", suspects['Candidate_ID'].tolist())
        c = suspects[suspects['Candidate_ID'] == selected_id].iloc[0]
        
        if st.button("🚀 Execute Audit"):
            with st.spinner("AI is analyzing recruitment patterns..."):
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')
                    prompt = f"""Audit this hiring decision for bias:
                    Candidate: {selected_id}, Gender: Female, Skill Score: {c['Skill_Score']}, Exp: {c['Experience_Years']}y.
                    Compare with general hiring standards. Provide:
                    1. Verdict
                    2. Possible Bias Detection
                    3. Actionable HR Advice."""
                    
                    response = model.generate_content(prompt)
                    report_text = response.text
                    
                    st.markdown("### 📝 Audit Report")
                    st.info(report_text)
                    
                    # 6. Download Button
                    st.download_button(label="📥 Download This Report", 
                                       data=report_text, 
                                       file_name=f"Audit_Report_{selected_id}.txt", 
                                       mime="text/plain")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.success("No suspicious rejection patterns found for high-skilled candidates!")
else:
    st.warning("Please upload CSV and enter API Key to start the audit.")
