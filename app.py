import streamlit as st
import pandas as pd
import joblib

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="HR Analytics Prediction",
    page_icon=":alarm_clock:",
    layout="centered"
)

# ------------------ Load Model ------------------
model = joblib.load("model.pkl")
encoders = joblib.load("label_encoders.pkl")

# ------------------ Header ------------------
st.markdown(
    """
    <h1 style='text-align: center;'>📊 HR Analytics Prediction App </h1>
    <p style='text-align: center; color: gray;'>
    Predict whether an employee is likely to leave the company or not
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ------------------ Sidebar Inputs ------------------
st.sidebar.header("🔧 Employee Details")

satisfaction_level = st.sidebar.slider(
    "Satisfaction Level", 0.0, 1.0, 0.5, 0.01
)

last_evaluation = st.sidebar.slider(
    "Last Evaluation Score", 0.0, 1.0, 0.5, 0.01
)

number_projects = st.sidebar.slider(
    "Number of Projects", 1, 10, 3
)

monthly_hours = st.sidebar.slider(
    "Average Monthly Hours", 50, 350, 160, 10
)

time_spend_company = st.sidebar.slider(
    "Years in Company", 1, 10, 3
)

promotion_last_5years = st.sidebar.radio(
    "Promotion in Last 5 Years",
    options=[0, 1],
    format_func=lambda x: "Yes" if x == 1 else "No"
)

dept = st.sidebar.selectbox(
    "Department", encoders['dept'].classes_.tolist()
)

salary = st.sidebar.selectbox(
    "Salary Bracket", encoders['salary'].classes_.tolist()
)

# ------------------ Main Section ------------------
st.subheader("📋 Review Employee Information")

col1, col2 = st.columns(2)

with col1:
    st.metric("Satisfaction Level", satisfaction_level)
    st.metric("Last Evaluation", last_evaluation)
    st.metric("Projects", number_projects)
    st.metric("Years in Company", time_spend_company)

with col2:
    st.metric("Monthly Hours", monthly_hours)
    st.metric("Promotion", "Yes" if promotion_last_5years else "No")
    st.metric("Department", dept)
    st.metric("Salary", salary)

st.divider()

# ------------------ Prediction ------------------
prediction = model.predict(data)[0]

# 👉 Probability
prob = model.predict_proba(data)[0][1]

st.subheader("📌 Prediction Result")

# 👉 Show probability
st.write(f"📊 Probability of Leaving: {prob:.2f}")

# 👉 Show result
if prediction == 1:
    st.warning("⚠️ Employee is Likely to Quit")
    st.info("Recommendation: Consider HR intervention and engagement strategies.")
else:
    st.success("✅ Employee is Not Likely to Quit")


# 👉 ADD THIS LINE
st.progress(int(prob * 100))
st.write(f"📊 Risk Score: {prob:.2%}")

# ------------------ Footer ------------------
st.markdown(
    "<p style='text-align:center; color:gray;'>Built with Streamlit</p>",
    unsafe_allow_html=True
)
