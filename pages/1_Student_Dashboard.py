import streamlit as st
import sqlite3
import pandas as pd
from resume_analyzer import analyze_resume

def get_db_connection():
    return sqlite3.connect('recruitment.db')

# --- UI ---
st.set_page_config(page_title="Student Dashboard", layout="wide")

if not st.session_state.get('logged_in'):
    st.error("You must be logged in to view this page.")
    st.stop()

with st.sidebar:
    st.title(f"Welcome, {st.session_state['user_info']['full_name']}!")
    if st.button("Logout 🚪"):
        st.session_state.clear()
        st.switch_page("app.py")

st.title("🎓 Student Dashboard")

tab1, tab2 = st.tabs(["Search for Jobs", "My Applications"])

# --- TAB 1: SEARCH FOR JOBS (UPDATED) ---
with tab1:
    st.header("Available Job Opportunities")
    conn = get_db_connection()
    jobs_df = pd.read_sql_query("SELECT j.id, j.title, j.description, j.required_skills, u.full_name as recruiter_name FROM jobs j JOIN users u ON j.recruiter_id = u.id", conn)
    conn.close()

    if jobs_df.empty:
        st.info("No jobs posted yet. Check back later!")
    else:
        for index, row in jobs_df.iterrows():
            job_id = row['id']
            with st.expander(f"**{row['title']}** posted by {row['recruiter_name']}"):
                st.write("**Description:**")
                st.write(row['description'])
                st.write(f"**Skills Required:** {row['required_skills']}")
                st.markdown("---")

                # Step 1: Resume Upload
                st.subheader("Step 1: Check Your Match Score")
                uploaded_resume = st.file_uploader("Upload your resume to see your score", type="pdf", key=f"resume_{job_id}")

                # When a file is uploaded, analyze it and store results in session state
                if uploaded_resume:
                    if st.button("Analyze My Resume", key=f"analyze_{job_id}"):
                        with st.spinner("Analyzing..."):
                            resume_bytes = uploaded_resume.getvalue()
                            results = analyze_resume(resume_bytes, row['description'], row['required_skills'])
                            # Store results in session state to use in the next step
                            st.session_state[f'analysis_results_{job_id}'] = results

                # Step 2: Display score and ask for confirmation
                if f'analysis_results_{job_id}' in st.session_state:
                    results = st.session_state[f'analysis_results_{job_id}']
                    st.subheader("Step 2: Review and Apply")
                    st.success("Analysis Complete!")
                    st.metric("Your Resume Match Score", f"{results['final_score']:.2f}%")
                    st.write(f"**✅ Matching Skills:** {', '.join(results['found_keywords'])}")
                    st.warning(f"**❌ Missing Skills:** {', '.join(results['missing_keywords'])}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm and Apply", key=f"confirm_{job_id}", type="primary"):
                            with st.spinner("Submitting your application..."):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                student_id = st.session_state['user_info']['id']
                                try:
                                    cursor.execute("""
                                        INSERT INTO applications (job_id, student_id, resume_score, matching_skills, missing_skills, status)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    """, (job_id, student_id, results['final_score'], ','.join(results['found_keywords']), ','.join(results['missing_keywords']), 'Pending'))
                                    conn.commit()
                                    st.success("Application submitted successfully!")
                                    # Clean up session state for this job
                                    del st.session_state[f'analysis_results_{job_id}']
                                except sqlite3.IntegrityError:
                                    st.error("You have already applied for this job.")
                                finally:
                                    conn.close()
                    with col2:
                        if st.button("Cancel", key=f"cancel_{job_id}"):
                            # Clean up session state for this job and rerun to reset the view
                            del st.session_state[f'analysis_results_{job_id}']
                            st.rerun()

# --- TAB 2: MY APPLICATIONS ---
with tab2:
    st.header("Your Application Status")
    student_id = st.session_state['user_info']['id']
    conn = get_db_connection()
    my_apps_df = pd.read_sql_query(f"""
        SELECT j.title, a.status, a.resume_score 
        FROM applications a 
        JOIN jobs j ON a.job_id = j.id 
        WHERE a.student_id = {student_id}
    """, conn)
    conn.close()

    if my_apps_df.empty:
        st.info("You haven't applied to any jobs yet.")
    else:
        st.dataframe(my_apps_df, use_container_width=True)