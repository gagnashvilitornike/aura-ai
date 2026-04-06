import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import stripe
# --- SETUP ---
load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
st.set_page_config(page_title="Aura | Premium Insights", layout="centered")

# --- THEME MANAGEMENT & MEMORY ---
if "theme" not in st.session_state:
    st.session_state.theme = "light" # საიტი ავტომატურად იხსნება თეთრ ფერში

if "report_stage" not in st.session_state:
    st.session_state.report_stage = 0
    st.session_state.free_text = ""
    st.session_state.premium_text = ""
    st.session_state.full_text = ""

# --- DYNAMIC CSS (LIGHT & DARK MODES) ---
if st.session_state.theme == "light":
    theme_css = """
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3, p, span, label, li { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif !important; }
    .sub-title { color: #555555 !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: transparent !important; color: #000000 !important; border: 1px solid #CCCCCC !important; }
    div[data-testid="stButton"] button { background-color: #000000 !important; color: #FFFFFF !important; border: none !important; }
    div[data-testid="stButton"] button p { color: #FFFFFF !important; }
    div[data-testid="stButton"] button:hover { background-color: #333333 !important; }
    .paywall-box { background-color: #000000; color: #FFFFFF !important; }
    .paywall-box h3, .paywall-box p { color: #FFFFFF !important; }
    .blur-text { color: transparent !important; text-shadow: 0 0 10px rgba(255,255,255,0.5); }
    """
else:
    theme_css = """
    .stApp { background-color: #0A0A0A !important; color: #F0F0F0 !important; }
    h1, h2, h3, p, span, label, li { color: #F0F0F0 !important; font-family: 'Helvetica Neue', sans-serif !important; }
    .sub-title { color: #888888 !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #333333 !important; }
    div[data-testid="stButton"] button { background-color: #FFFFFF !important; color: #000000 !important; border: none !important; }
    div[data-testid="stButton"] button p { color: #000000 !important; }
    div[data-testid="stButton"] button:hover { background-color: #CCCCCC !important; }
    .paywall-box { background-color: #111111; border: 1px solid #333333; color: #FFFFFF !important; }
    .paywall-box h3, .paywall-box p { color: #FFFFFF !important; }
    .blur-text { color: transparent !important; text-shadow: 0 0 10px rgba(255,255,255,0.3); }
    """

# Hiding native Streamlit menu to fix the glitch
global_css = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main-title { text-align: center; font-size: 3rem; font-weight: 300; letter-spacing: 2px; margin-bottom: 0px; }
    .sub-title { text-align: center; font-size: 1rem; font-weight: 300; margin-bottom: 20px; }
    div[data-testid="stButton"] button { border-radius: 4px !important; font-weight: bold !important; width: 100%; padding: 12px !important; transition: all 0.3s; }
    .paywall-box { padding: 30px; border-radius: 8px; text-align: center; margin: 20px 0; }
    """ + theme_css + """
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)

# --- CUSTOM THEME TOGGLE BUTTON ---
col_spacer, col_toggle = st.columns([8, 2])
with col_toggle:
    toggle_label = "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"
    if st.button(toggle_label):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

# --- MEGA PROMPT ---
AURA_PROMPT = """You are Aura, an elite psychological profiler. 
Based on the user's metrics and text, write a deep psychological report.
You MUST divide your response into exactly two parts, separated by this exact keyword: ===SPLIT===

PART 1 (Free content):
Write '## The Core Vibe' and a poetic summary of their state.
Write '## Cognitive Analysis' and an analysis of their state.

===SPLIT===

PART 2 (Premium content - THIS MUST BE EXTREMELY DETAILED AND VALUABLE):
This section must justify a premium price tag. Write an exhaustive, high-value psychological protocol (at least 500 words). Use these exact headers and expand on them deeply:

## 1. Deep Cognitive Diagnosis
(Analyze their hidden subconscious patterns, potential burnout triggers, and why they specifically feel this way based on the exact numbers they provided.)

## 2. Immediate Triage (Next 24 Hours)
(Provide exact, neuro-scientifically backed steps they must take today to regain control of their nervous system.)

## 3. The 7-Day Optimization Framework
(Create a structured daily system tailored to their specific metrics, including focus blocks, social energy management, and stress relief.)

## 4. Shadow Work & Long-Term Recalibration
(Give advanced psychological advice on how to manage their specific traits for lasting balance and deep fulfillment.)

Tone: Premium, highly analytical, deeply empathetic. English only. DO NOT use markdown code blocks."""

# --- UI HEADER ---
st.markdown("<h1 class='main-title'>AURA</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>DEEP PSYCHOLOGICAL INSIGHTS DRIVEN BY AI</p>", unsafe_allow_html=True)

# --- ASSESSMENT FORM ---
col1, col2 = st.columns(2)
with col1:
    stress = st.slider("Stress & Overwhelm", 1, 10, 5)
    social = st.slider("Social Battery", 1, 10, 5)
with col2:
    focus = st.slider("Focus & Clarity", 1, 10, 5)
    emotion = st.slider("Emotional Baseline", 1, 10, 5)

narrative = st.text_area("Describe what is taking up the most space in your mind right now.", height=100)
email = st.text_input("Enter your email address (Required)", placeholder="your@email.com")

# --- GENERATION LOGIC ---
if st.button("GENERATE MY AURA REPORT"):
    if len(narrative) < 5 or "@" not in email:
        st.warning("Please provide a bit more detail and a valid email address.")
    else:
        with st.spinner("Generating High-Value Cognitive Blueprint..."):
            user_input = f"Stress:{stress}, Social:{social}, Focus:{focus}, Emotion:{emotion}. Text:{narrative}"
            
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": AURA_PROMPT},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7
                )
                
                raw_text = resp.choices[0].message.content.replace("```markdown", "").replace("```", "")
                
                if "===SPLIT===" in raw_text:
                    parts = raw_text.split("===SPLIT===")
                    st.session_state.free_text = parts[0].strip()
                    st.session_state.premium_text = parts[1].strip()
                else:
                    st.session_state.free_text = raw_text
                    st.session_state.premium_text = "## Error\nAI format error. Please try again."
                
                st.session_state.full_text = st.session_state.free_text + "\n\n" + st.session_state.premium_text
                st.session_state.report_stage = 1
                
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")

# --- DISPLAY LOGIC ---
# --- PAYMENT REDIRECT HANDLING ---
# This checks if the user just returned from a successful Stripe payment
if st.query_params.get("success") == "true":
    st.session_state.report_stage = 2

# --- DISPLAY LOGIC ---
if st.session_state.report_stage > 0:
    if st.session_state.report_stage == 1:
        # --- SHOW FREE CONTENT FIRST ---
        st.markdown("### Your Initial Aura Analysis")
        st.write(st.session_state.free_text)
        st.markdown("---")
        # Paywall UI
        st.markdown("""
        <div class='paywall-box'>
            <p class='blur-text'>1. Deep Cognitive Diagnosis: Analyzing your hidden patterns...<br>
            2. Immediate Triage: Exact steps for the next 24 hours...<br>
            3. The 7-Day Framework: Your daily optimization system...</p>
            <p style='font-weight: bold;'>Unlock a deep, 4-stage cognitive framework tailored strictly to your metrics.</p>
        </div>
        """, unsafe_allow_html=True)

        # Stripe Checkout Button
        if st.button("🔓 UNLOCK FULL PROTOCOL (1.99€)"):
            try:
                session = stripe.checkout.Session.create(
                    line_items=[{
                        'price': st.secrets["STRIPE_PRICE_ID"],
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url="https://aura-ai-mqxnltpcnm7bq45wromtbd.streamlit.app/?success=true",
                    cancel_url="https://aura-ai-mqxnltpcnm7bq45wromtbd.streamlit.app/",
                )
                
                # Professional redirect button
                st.markdown(f'''
                    <a href="{session.url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #000000; color: white; padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px;">
                            PROCEED TO SECURE PAYMENT
                        </div>
                    </a>
                ''', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Payment System Error: {e}")

    elif st.session_state.report_stage == 2:
        # Premium Content Display
        st.balloons()
        st.success("✨ **Premium Master Protocol Unlocked** ✨")
        st.markdown(st.session_state.premium_text)
        st.markdown("---")
        st.download_button(
            label="📩 DOWNLOAD FULL PREMIUM REPORT (.TXT)",
            data=st.session_state.premium_text,
            file_name="Aura_Premium_Report.txt",
            mime="text/plain"
        )