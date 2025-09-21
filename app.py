import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

# --- DATABASE FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('recruitment.db')

def create_user(username, password, full_name, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = pbkdf2_sha256.hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                       (username, password_hash, full_name, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- UPDATED FUNCTION ---
def verify_user(username, password, role):
    """Verifies user credentials against the database for a specific role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # CHANGED: Query now also checks for the role
    cursor.execute("SELECT password_hash, role, id, full_name FROM users WHERE username = ? AND role = ?", (username, role))
    user_data = cursor.fetchone()
    conn.close()
    if user_data and pbkdf2_sha256.verify(password, user_data[0]):
        # Return user info dictionary
        return {"role": user_data[1], "id": user_data[2], "full_name": user_data[3]}
    return None

# --- UI SETUP ---
st.set_page_config(page_title="Welcome", layout="centered")

st.title("Welcome to the Automated Recruitment System 🚀")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# --- LOGIN/SIGNUP LOGIC ---
if not st.session_state['logged_in']:
    choice = st.radio("Choose your action", ["Login", "Sign Up"])

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # --- NEW: Role selection added to login form ---
        role_str = st.selectbox("Login as", ["Student", "Recruiter"])
        role = 1 if role_str == "Student" else 2
        
        if st.button("Login"):
            # CHANGED: Pass the selected role to the verification function
            user_info = verify_user(username, password, role)
            if user_info:
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = user_info
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials for the selected role.")

    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        full_name = st.text_input("Full Name")
        role_str_signup = st.selectbox("I am a...", ["Student", "Recruiter"], key="signup_role")
        role_signup = 1 if role_str_signup == "Student" else 2

        if st.button("Sign Up"):
            if create_user(new_username, new_password, full_name, role_signup):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")

# --- REDIRECTION LOGIC ---
if st.session_state['logged_in']:
    st.write(f"Welcome, {st.session_state['user_info']['full_name']}!")
    
    user_role = st.session_state['user_info']['role']
    if user_role == 1: # Student
        st.write("Redirecting to your Student Dashboard...")
        st.switch_page("pages/1_Student_Dashboard.py")
    elif user_role == 2: # Recruiter
        st.write("Redirecting to your Recruiter Dashboard...")
        st.switch_page("pages/2_Recruiter_Dashboard.py")
