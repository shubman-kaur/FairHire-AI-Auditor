import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config
st.set_page_config(page_title="FairHire AI | Under 100 Edition", layout="wide")

# 2. Design/CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .main-title { color: #1A73E8; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .compare-card { background: #E8F0FE; padding: 15px; border-radius: 10px; border-left: 5px solid #1A73E8; margin-bottom: 20px; }
    .advice-card { background: #E6F4EA; padding: 15px; border-radius: 10px; border-left: 5px solid #34A853; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✨ FairHire AI: Ethical Recruitment Auditor</div>', unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.header("🔑 Control Panel")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.success("🎯 Mission: Top 100 Standout")
    st.info("System: Analysis + Mitigation Mode")

# 4. Data Loading & Analytics
uploaded_file = st.file_uploader("Upload Company Hiring CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.markdown("### 🎯 Selection Landscape")
        fig_scatter = px.scatter(df, x="Skill_Score", y="Status", color="Gender",
                                 hover_data=['Candidate_ID'], symbol="Status",
                                 color_discrete_map={'Male': '#4285F4', 'Female': '#EA4335'})
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_b:
        st.markdown("### 📊 Quick Stats")
        m_sel = len(df[(df['Gender'] == 'Male') & (df['Status'] == 'Selected')])
        f_sel = len(df[(df['Gender'] == 'Female') & (df['Status'] == 'Selected')])
        st.write(f"✅ Males: {m_sel} | ✅ Females: {f_sel}")
        fig_pie = px.pie(values=[m_sel, f_sel], names=['Male', 'Female'], hole=0.4,
                         color_discrete_sequence=['#4285F4', '#EA4335'])
        st.plotly_chart(fig_pie, use_container_width=True)

    # 5. AI Audit Section
    st.divider()
    if api_key:
        genai.configure(api_key=api_key)
        st.subheader("🕵️‍♂️ Deep AI Audit & Recommendation Engine")
        
        suspects = df[(df['Gender'] == 'Female') & (df['Status'] == 'Rejected') & (df['Skill_Score'] > 60)]
        selected_males = df[(df['Gender'] == 'Male') & (df['Status'] == 'Selected')].sort_values(by='Skill_Score')
        
        if not suspects.empty:
            selected_id = st.selectbox("Select Candidate to Audit", suspects['Candidate_ID'].tolist())
            c = suspects[suspects['Candidate_ID'] == selected_id].iloc[0]
            avg_m = df[df['Gender'] == 'Male']['Skill_Score'].mean()

            if st.button("🚀 Execute Full Audit"):
                with st.spinner("AI Generating Audit & Mitigation Strategy..."):
                    try:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        prompt = f"""Perform a deep ethical audit:
                        CANDIDATE: {selected_id}, Female, Skill: {c['Skill_Score']}, Exp: {c['Experience_Years']}y.
                        MALE_AVG: {avg_m:.2f}, MIN_MALE_SELECTED: {selected_males['Skill_Score'].min() if not selected_males.empty else 'N/A'}
                        
                        Strictly return in this exact format:
                        RISK_SCORE: [Number 0-100]
                        VERDICT: [One sentence]
                        EVIDENCE: [Comparison text]
                        ADVICE: [Top 3 mitigation steps for HR]
                        """
                        response = model.generate_content(prompt)
                        raw = response.text
                        
                        # Solid Parsing
                        try:
                            r_score = int(raw.split("RISK_SCORE:")[1].split("VERDICT:")[0].strip())
                            v_text = raw.split("VERDICT:")[1].split("EVIDENCE:")[0].strip()
                            e_text = raw.split("EVIDENCE:")[1].split("ADVICE:")[0].strip()
                            a_text = raw.split("ADVICE:")[1].strip()
                        except:
                            r_score, v_text, e_text, a_text = 50, "Audit Complete", "See Raw Data", raw

                        c1, c2 = st.columns([1, 2])
                        with c1:
                            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=r_score, 
                                title={'text': "Bias Risk %", 'font': {'size': 24}},
                                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1A73E8"},
                                       'steps': [{'range': [0, 40], 'color': "#DFF0D8"}, 
                                                 {'range': [40, 80], 'color': "#FCF8E3"},
                                                 {'range': [80, 100], 'color': "#F2DEDE"}]}))
                            st.plotly_chart(fig_g, use_container_width=True)
                        
                        with c2:
                            st.markdown(f"#### ⚖️ Verdict: {v_text}")
                            st.markdown(f'<div class="compare-card"><b>📊 Comparison Evidence:</b><br>{e_text}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="advice-card"><b>💡 HR Action Plan:</b><br>{a_text}</div>', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Logic Error: {e}")
        else:
            st.success("No suspicious patterns found.")
else:
    st.warning("Please upload the CSV to start the audit.")
