import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# 1. Page Config
st.set_page_config(page_title="FairHire AI | Workspace", page_icon="✨", layout="wide")

# 2. Ultimate Google UI/UX CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Google Sans', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background-color: #F8F9FA;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #DADCE0;
    }

    /* Google Material Cards */
    .g-card {
        background-color: white;
        border: 1px solid #DADCE0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .g-card:hover {
        box-shadow: 0 4px 6px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
        transform: translateY(-2px);
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #4285F4 0%, #1967D2 100%);
        color: white;
        padding: 35px 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(66, 133, 244, 0.3);
    }
    .hero-banner h1 {
        color: white;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Primary Google Button */
    .stButton>button {
        background-color: #4285F4;
        color: white !important;
        border-radius: 24px;
        border: none;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
    }
    .stButton>button:hover {
        background-color: #1A73E8;
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
    }

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
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    /* Metric Typography */
    .g-metric-title {
        color: #5F6368;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .g-metric-value {
        color: #202124;
        font-size: 2.2rem;
        font-weight: 400;
        margin: 0;
    }
    
    /* Utility Colors */
    .text-blue { color: #4285F4 !important; }
    .text-green { color: #34A853 !important; }
    .text-red { color: #EA4335 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
            <img src="https://img.icons8.com/color/48/google-logo.png" width="35">
            <h2 style='color: #202124; margin: 0; font-size: 1.5rem;'>Google Cloud</h2>
        </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("<p style='color: #5F6368; font-size: 0.85rem;'>Connect to Gemini 2.5 Flash Engine.</p>", unsafe_allow_html=True)
    st.divider()
    st.info("💡 **Tip:** Use a dataset with 'Gender', 'Skill_Score', and 'Status' columns for the AI to audit.")
# 4. Hero Banner
st.markdown("""
    <div class="hero-banner">
        <h1>✨ FairHire AI Auditor</h1>
        <p style="font-size: 1.2rem; margin: 10px 0 0 0; font-weight: 400; opacity: 0.95;">
            Detecting unconscious bias in recruitment using Google's Generative AI.
        </p>
    </div>
""", unsafe_allow_html=True)

# 5. Main Dashboard Layout
col1, col2 = st.columns([1.2, 2], gap="large")

with col1:
    st.markdown("<h3 style='color: #202124;'>📁 1. Ingest Data</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Recruitment CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.markdown(f"""
            <div class="g-card">
                <div class="g-metric-title">Total Records Scanned</div>
                <div class="g-metric-value">{len(df)}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if api_key:
            st.success("✅ **System Status:** Ready for Audit")
        else:
            st.warning("⚠️ **System Status:** Waiting for API Key")

with col2:
    st.markdown("<h3 style='color: #202124;'>🔎 2. Bias Analysis</h3>", unsafe_allow_html=True)
    
    if uploaded_file and api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        suspects = df[(df['Gender'] == 'Female') & (df['Status'] == 'Rejected') & (df['Skill_Score'] > 60)]
        
        if not suspects.empty:
            st.markdown(f"<p style='color: #EA4335; font-weight: 500; font-size: 1.1rem;'>⚠️ System flagged {len(suspects)} rejected candidates with high skill scores.</p>", unsafe_allow_html=True)
            
            selected_id = st.selectbox("Select Candidate ID for Deep Audit", suspects['Candidate_ID'].tolist())
            c = suspects[suspects['Candidate_ID'] == selected_id].iloc[0]
            
            # Interactive Profile Cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                    <div class="g-card" style="text-align: center; padding: 15px;">
                        <div class="g-metric-title">Experience</div>
                        <div class="g-metric-value text-blue">{c['Experience_Years']} yrs</div>
                    </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                    <div class="g-card" style="text-align: center; padding: 15px;">
                        <div class="g-metric-title">Skill Score</div>
                        <div class="g-metric-value text-green">{c['Skill_Score']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                    <div class="g-card" style="text-align: center; padding: 15px;">
                        <div class="g-metric-title">Status</div>
                        <div class="g-metric-value text-red">{c['Status']}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.write("")
            
            if st.button("🚀 Run Google AI Audit"):
                with st.spinner("Gemini Engine is analyzing the hiring pattern..."):
                    time.sleep(1) # Adds a slight professional loading feel
                    prompt = f"Audit Candidate {selected_id} (Female, {c['Experience_Years']}yrs experience, {c['Skill_Score']} score, Status: Rejected) for potential gender bias. Give a sharp, professional 3-line expert verdict based on these metrics."
                    response = model.generate_content(prompt)
                    
                    st.markdown("### ⚖️ Official Auditor Verdict")
                    st.markdown(f"""
                        <div class="verdict-box">
                            <strong>AI Reasoning:</strong><br><br>
                            {response.text}
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
        else:
            st.info("No immediate bias risks detected in this dataset based on current thresholds.")
    else:
        # Placeholder when no data is uploaded
        st.markdown("""
            <div class="g-card" style="text-align: center; padding: 60px 20px; background-color: white; border: 2px dashed #DADCE0;">
                <h4 style="color: #5F6368; margin: 0;">Awaiting Data</h4>
                <p style="color: #80868B; margin-top: 10px;">Upload a CSV file and enter your API key to activate the dashboard.</p>
            </div>
        """, unsafe_allow_html=True)