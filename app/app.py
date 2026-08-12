import streamlit as st
import pickle
import pandas as pd
import time
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="Health Predictor", page_icon="🧠")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background: #0f172a;
    color: white;
}

.block-container {
    padding-top: 2rem;
    max-width: 600px;
}

.card {
    background: #1e293b;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.stButton > button {
    width: 100%;
    height: 3rem;
    border-radius: 12px;
    font-weight: bold;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
}

.result {
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    font-size: 1.3rem;
    font-weight: bold;
}

.low { background: #065f46; }
.high { background: #7f1d1d; }
</style>
""", unsafe_allow_html=True)

# ---------- LOAD MODEL ----------
@st.cache_resource
def load():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(base_dir, "..", "models", "model.pkl")
        scaler_path = os.path.join(base_dir, "..", "models", "scaler.pkl")

        model = pickle.load(open(model_path, "rb"))
        scaler = pickle.load(open(scaler_path, "rb"))

        return model, scaler

    except Exception as e:
        st.error(f"❌ Model loading failed: {e}")
        return None, None

model, scaler = load()

if model is None:
    st.stop()

# ---------- SESSION ----------
if "step" not in st.session_state:
    st.session_state.step = 1

# ---------- HEADER (UPDATED) ----------
st.markdown(
    "<h1 style='text-align:center;'>🧠 Health Risk Analyzer</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; color:#94a3b8;'>Smart prediction using body metrics</p>",
    unsafe_allow_html=True
)

st.markdown("<div class='card'>", unsafe_allow_html=True)

# ---------- STEP 1 ----------
if st.session_state.step == 1:
    st.progress(1/3)
    st.subheader("👤 Basic Info")

    gender = st.radio("Gender", ["Female", "Male"])
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)

    if st.button("Next ➡️"):
        st.session_state.gender = gender
        st.session_state.weight = weight
        st.session_state.step = 2
        st.rerun()

# ---------- STEP 2 ----------
elif st.session_state.step == 2:
    st.progress(2/3)
    st.subheader("📏 Measurements")

    height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
    arm_length = st.number_input("Arm Length (cm)", 10.0, 60.0, 35.0)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back"):
            st.session_state.step = 1
            st.rerun()

    with col2:
        if st.button("Next ➡️"):
            st.session_state.height = height
            st.session_state.arm_length = arm_length
            st.session_state.step = 3
            st.rerun()

# ---------- STEP 3 ----------
elif st.session_state.step == 3:
    st.progress(3/3)
    st.subheader("📐 Final Details")

    leg_length = st.number_input("Leg Length (cm)", 10.0, 60.0, 40.0)
    arm_circum = st.number_input("Arm Circumference (cm)", 10.0, 70.0, 30.0)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back"):
            st.session_state.step = 2
            st.rerun()

    with col2:
        if st.button("🧠 Analyze"):
            with st.spinner("Analyzing health data..."):
                time.sleep(1.5)

                st.session_state.leg_length = leg_length
                st.session_state.arm_circum = arm_circum
                st.session_state.step = 4
                st.rerun()

# ---------- RESULT ----------
elif st.session_state.step == 4:
    st.subheader("📊 Result")

    weight = st.session_state.weight
    height = st.session_state.height

    bmi = weight / ((height / 100) ** 2)

    def bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    category = bmi_category(bmi)

    st.markdown(f"""
    <div style="text-align:center; font-size:1.1rem;">
        BMI: <b>{bmi:.2f}</b> ({category})
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame([[
        weight,
        height,
        bmi,
        st.session_state.arm_length,
        st.session_state.leg_length,
        st.session_state.arm_circum,
        (1 if st.session_state.gender == "Female" else 0)
    ]], columns=['BMXWT','BMXHT','BMI','BMXARML','BMXLEG','BMXARMC','Gender'])

    scaled = scaler.transform(df)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1]

    if pred == 1:
        st.markdown(f"""
        <div class='result high'>
            ⚠️ HIGH RISK<br>
            <span style="font-size:1rem;">Probability: {prob:.1%}</span>
        </div>
        """, unsafe_allow_html=True)
        st.warning("Consider improving diet, exercise, and regular health checkups.")
    else:
        st.markdown(f"""
        <div class='result low'>
            ✅ LOW RISK<br>
            <span style="font-size:1rem;">Probability: {prob:.1%}</span>
        </div>
        """, unsafe_allow_html=True)
        st.success("Your health indicators look good. Keep maintaining your lifestyle!")

    if st.button("🔄 Start Again"):
        st.session_state.clear()
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)