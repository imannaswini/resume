import streamlit as st
import sqlite3
import pandas as pd
# Import the new parser functions
from file_parser import extract_text_from_pdf_bytes, extract_text_from_docx_bytes, parse_job_description_text

def get_db_connection():
    return sqlite3.connect('recruitment.db')

# --- UI ---
st.set_page_config(page_title="Recruiter Dashboard", layout="wide")

if not st.session_state.get('logged_in') or st.session_state['user_info']['role'] != 2:
    st.error("You must be a logged-in recruiter to view this page.")
    st.stop()

with st.sidebar:
    st.title(f"Welcome, {st.session_state['user_info']['full_name']}!")
    if st.button("Logout 🚪"):
        st.session_state.clear() # Clear all session state on logout
        st.switch_page("app.py")

st.title("💼 Recruiter Dashboard")

tab1, tab2 = st.tabs(["Post a New Job", "View Applications"])

# --- TAB 1: POST A JOB (UPDATED) ---
with tab1:
    st.header("Create a New Job Posting")
    
    st.subheader("Option 1: Upload a Job Description File")
    st.info("Upload a PDF or DOCX file to automatically fill the fields below.")
    uploaded_jd = st.file_uploader("Upload Job Description", type=['pdf', 'docx'])
    
    # When a new file is uploaded, parse it and store details in session_state
    if uploaded_jd:
        # Check if this is a new file to avoid reprocessing on every rerun
        if 'uploaded_jd_name' not in st.session_state or st.session_state.uploaded_jd_name != uploaded_jd.name:
            with st.spinner("Parsing document..."):
                jd_bytes = uploaded_jd.getvalue()
                text = ""
                if uploaded_jd.type == "application/pdf":
                    text = extract_text_from_pdf_bytes(jd_bytes)
                else: # application/vnd.openxmlformats-officedocument.wordprocessingml.document
                    text = extract_text_from_docx_bytes(jd_bytes)
                
                # Store the parsed details and the filename in session state
                st.session_state.job_details = parse_job_description_text(text)
                st.session_state.uploaded_jd_name = uploaded_jd.name

    st.markdown("---")
    st.subheader("Option 2: Fill Manually (or Edit Extracted Details)")

    # Retrieve pre-filled details from session_state if they exist
    prefill = st.session_state.get('job_details', {})

    with st.form("job_post_form", clear_on_submit=True):
        title = st.text_input("Job Title", value=prefill.get('title', ''))
        description = st.text_area("Job Description", value=prefill.get('description', ''), height=300)
        skills = st.text_input("Required Skills (comma-separated)", value=prefill.get('skills', ''), help="e.g., Python, SQL, AWS")
        
        submitted = st.form_submit_button("Post Job")
        if submitted:
            recruiter_id = st.session_state['user_info']['id']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO jobs (recruiter_id, title, description, required_skills) VALUES (?, ?, ?, ?)",
                           (recruiter_id, title, description, skills))
            conn.commit()
            conn.close()
            st.success(f"Job '{title}' posted successfully!")
            # Clear the pre-filled details after submission
            if 'job_details' in st.session_state:
                del st.session_state.job_details
            if 'uploaded_jd_name' in st.session_state:
                del st.session_state.uploaded_jd_name


# --- TAB 2: VIEW APPLICATIONS ---
with tab2:
    # This part remains the same
    st.header("Manage Candidate Applications")
    recruiter_id = st.session_state['user_info']['id']
    conn = get_db_connection()
    
    my_jobs = pd.read_sql_query(f"SELECT id, title FROM jobs WHERE recruiter_id = {recruiter_id}", conn)
    if my_jobs.empty:
        st.info("You have not posted any jobs yet.")
    else:
        job_options = {row['title']: row['id'] for index, row in my_jobs.iterrows()}
        selected_job_title = st.selectbox("Select one of your jobs to view applicants", options=job_options.keys())
        
        if selected_job_title:
            job_id = job_options[selected_job_title]
            
            applicants_df = pd.read_sql_query(f"""
                SELECT a.id as application_id, u.full_name, u.username, a.resume_score, a.status, a.matching_skills, a.missing_skills
                FROM applications a
                JOIN users u ON a.student_id = u.id
                WHERE a.job_id = {job_id}
            """, conn)
            
            if applicants_df.empty:
                st.warning("No applications received for this job yet.")
            else:
                st.dataframe(applicants_df[['full_name', 'resume_score', 'status', 'matching_skills', 'missing_skills']], use_container_width=True)
                
                st.subheader("Update Application Status")
                app_id_to_update = st.number_input("Enter Application ID to update", min_value=1, step=1)
                new_status = st.selectbox("New Status", ["Accepted", "Rejected"])
                
                if st.button("Update Status"):
                    cursor = conn.cursor()
                    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id_to_update))
                    conn.commit()
                    st.success(f"Application {app_id_to_update} updated to {new_status}.")
                    st.rerun() 
    conn.close()