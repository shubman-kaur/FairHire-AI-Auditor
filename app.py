import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="FairHire AI | Workspace", page_icon="✨", layout="wide")

# 2. Professional UI/UX Styling (Google Material Design)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    * { font-family: 'Google Sans', sans-serif; }
    
    .stApp { background-color: #F8F9FA; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #DADCE0;
    }

    /* Professional Card Styling */
    .g-card {
        background-color: white;
        border: 1px solid #DADCE0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
        margin-bottom: 20px;
    }

    /* Hero Banner Styling */
    .hero-banner {
        background: linear-gradient(135deg, #4285F4 0%, #1967D2 100%);
        color: white;
        padding: 35px 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(66, 133, 244, 0.3);
    }
    .hero-banner h1 { color: white; margin: 0; font-size: 2.5rem; font-weight: 700; }

    /* AI Verdict Box */
    .verdict-box {
        background-color: #E8F0FE;
        border-left: 5px solid #4285F4;
        padding: 25px;
        border-radius: 4px 12px 12px 4px;
        color: #1967D2;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-top: 20px;
    }

    /* Metric Labels */
    .g-metric-title { color: #5F6368; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; margin-bottom: 8px; }
    .g-metric-value { color: #202124; font-size: 2.2rem; font-weight: 400; margin: 0; }
    
    .text-blue { color: #4285F4 !important; }
    .text-green { color: #34A853 !important; }
    .text-red { color: #EA4335 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Helper Function for Visualization
def generate_fairness_gauge(score):
    """Generates a Gauge Chart to visualize the overall fairness of the hiring process."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Ethical Fairness Index", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4285F4"},
            'steps': [
                {'range': [0, 45], 'color': '#FFCDD2'}, # Bias Risk
                {'range': [45, 75], 'color': '#FFF9C4'}, # Neutral
                {'range': [75, 100], 'color': '#C8E6C9'} # Fair
            ],
            'threshold': {'line': {'color': "black", 'width': 3}, 'value': score}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# 4. Sidebar Branding and Configuration
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
            <img src="https://img.icons8.com/color/48/google-logo.png" width="35">
            <h2 style='color: #202124; margin: 0; font-size: 1.5rem;'>Google Cloud</h2>
        </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("<p style='color: #5F6368; font-size: 0.85rem;'>Authorized connection to Gemini 1.5 Flash Engine.</p>", unsafe_allow_html=True)
    st.divider()
    st.info("💡 **Best Practice:** Ensure your CSV contains 'Gender', 'Skill_Score', and 'Status' for optimal auditing.")

# 5. Hero Banner
st.markdown("""
    <div class="hero-banner">
        <h1>✨ FairHire AI Auditor</h1>
        <p style="font-size: 1.1rem; margin-top: 5px; opacity: 0.9;">Professional Ethical Recruitment Auditing System</p>
    </div>
""", unsafe_allow_html=True)

# 6. Main Dashboard Logic
col1, col2 = st.columns([1.2, 2], gap="large")

with col1:
    st.markdown("<h3 style='color: #202124;'>📁 1. Ingest Data</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Recruitment CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Core Logic: Calculate Bias Score for the Gauge
        total_rejected_females = len(df[(df['Gender'] == 'Female') & (df['Status'] == 'Rejected')])
        total_records = len(df)
        # Simplified Mock Logic: Lower score if more high-skilled females are rejected
        fairness_score = max(min(100 - (total_rejected_females / total_records * 200), 100), 15) if total_records > 0 else 100

        # Display Metrics and Gauge
        st.plotly_chart(generate_fairness_gauge(fairness_score), use_container_width=True)
        
        st.markdown(f"""
            <div class="g-card">
                <div class="g-metric-title">Total Records Scanned</div>
                <div class="g-metric-value text-blue">{total_records}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if api_key:
            st.success("✅ **System Status:** Online")
        else:
            st.warning("⚠️ **System Status:** API Authorization Required")

with col2:
    st.markdown("<h3 style='color: #202124;'>🔎 2. Bias Analysis</h3>", unsafe_allow_html=True)
    
    if uploaded_file and api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Logic to identify suspicious rejections
        suspects = df[(df['Gender'] == 'Female') & (df['Status'] == 'Rejected') & (df['Skill_Score'] > 60)]
        
        if not suspects.empty:
            st.markdown(f"<p style='color: #EA4335; font-weight: 500;'>Detected {len(suspects)} high-skill rejection patterns.</p>", unsafe_allow_html=True)
            
            selected_id = st.selectbox("Select Candidate for Deep Audit", suspects['Candidate_ID'].tolist())
            c = suspects[suspects['Candidate_ID'] == selected_id].iloc[0]
            
            # Candidate Summary Cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="g-card" style="text-align: center;"><div class="g-metric-title">Exp.</div><div class="g-metric-value text-blue">{c["Experience_Years"]}y</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="g-card" style="text-align: center;"><div class="g-metric-title">Score</div><div class="g-metric-value text-green">{c["Skill_Score"]}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="g-card" style="text-align: center;"><div class="g-metric-title">Status</div><div class="g-metric-value text-red">Rejected</div></div>', unsafe_allow_html=True)
            
            if st.button("🚀 Execute AI Audit"):
                with st.spinner("Gemini performing cross-metric audit..."):
                    time.sleep(1)
                    prompt = f"Perform a merit-based audit for Candidate {selected_id}. Details: Female, {c['Experience_Years']} years experience, {c['Skill_Score']}/100 Skill Score. Status: Rejected. Explain potential gender bias in 3 professional lines."
                    response = model.generate_content(prompt)
                    
                    st.markdown("### ⚖️ Auditor Verdict")
                    st.markdown(f"""<div class="verdict-box"><strong>Gemini Intelligence Reasoning:</strong><br><br>{response.text}</div>""", unsafe_allow_html=True)
                    st.toast('Deep Audit Completed!', icon='✅')
        else:
            st.success("No critical bias patterns found in the current dataset.")
    else:
        st.info("Please upload a dataset and provide an API key to begin the analysis.")
