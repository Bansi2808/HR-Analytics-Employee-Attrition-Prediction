import streamlit as st
import pandas as pd
import joblib
import bcrypt

# ------------------ AUTH SETUP ------------------

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin": {
            "password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
            "role": "admin"
        }
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ------------------ LOGIN / SIGNUP ------------------

menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if not st.session_state.logged_in:

    if menu == "Signup":
        st.title("📝 Create Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Signup"):
            if new_user in st.session_state.users_db:
                st.error("User already exists")
            else:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
                st.session_state.users_db[new_user] = {
                    "password": hashed,
                    "role": "user"
                }
                st.success("Account created! Please login.")

    elif menu == "Login":
        st.title("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users_db:
                stored_pw = st.session_state.users_db[username]["password"]

                if bcrypt.checkpw(password.encode(), stored_pw):
                    st.session_state.logged_in = True
                    st.session_state.role = st.session_state.users_db[username]["role"]
                    st.session_state.username = username
                    st.success(f"Welcome {username}")
                    st.rerun()
                else:
                    st.error("Invalid password")
            else:
                st.error("User not found")

    st.stop()

# ------------------ LOAD MODEL ------------------

model = joblib.load("model.pkl")
encoders = joblib.load("label_encoders.pkl")

# ------------------ HEADER ------------------

st.title("📊 HR Analytics Prediction App")

st.sidebar.write(f"👤 User: {st.session_state.username}")
st.sidebar.write(f"🔑 Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# ------------------ INPUTS ------------------

st.sidebar.header("🔧 Employee Details")

satisfaction_level = st.sidebar.slider("Satisfaction Level", 0.0, 1.0, 0.5, 0.01)
last_evaluation = st.sidebar.slider("Last Evaluation Score", 0.0, 1.0, 0.5, 0.01)
number_projects = st.sidebar.slider("Number of Projects", 1, 10, 3)
monthly_hours = st.sidebar.slider("Average Monthly Hours", 50, 350, 160, 10)
time_spend_company = st.sidebar.slider("Years in Company", 1, 10, 3)

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

# ------------------ DISPLAY INPUT ------------------

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

# ------------------ PREDICTION ------------------

if st.button("🔍 Predict Employee Status", use_container_width=True):

    data = pd.DataFrame({
        'satisfaction_level': [satisfaction_level],
        'last_evaluation': [last_evaluation],
        'number_project': [number_projects],
        'average_montly_hours': [monthly_hours],
        'time_spend_company': [time_spend_company],
        'promotion_last_5years': [promotion_last_5years],
        'dept': [dept],
        'salary': [salary]
    })

    for col in ['dept', 'salary']:
        data[col] = encoders[col].transform(data[col])

    prediction = model.predict(data)[0]
    prob = model.predict_proba(data)[0][1]

    st.subheader("📌 Prediction Result")

    st.progress(int(prob * 100))
    st.write(f"📊 Risk Score: {prob:.2%}")

    if prediction == 1:
        st.warning("⚠️ Employee is Likely to Quit")
        st.info("Recommendation: Consider HR intervention and engagement strategies.")
    else:
        st.success("✅ Employee is Not Likely to Quit")

# ------------------ FOOTER ------------------

st.markdown(
    "<p style='text-align:center; color:gray;'>Built with Streamlit</p>",
    unsafe_allow_html=True
)
