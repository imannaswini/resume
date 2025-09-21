🤖 AI-Powered Resume Relevance Checker
An intelligent Streamlit web application designed to automate the tedious process of resume screening. This system calculates a relevance score for a student's resume against a given job description, identifies skill gaps, and provides a streamlined interface for both students and recruiters.

✨ Key Features
Role-Based Access: Separate, secure dashboards for Students and Recruiters.

Persistent Sessions: User sessions are remembered across browser refreshes using secure cookies.

Hybrid Scoring Model: Combines keyword matching (Hard Match) and semantic similarity (Soft Match) for accurate relevance scoring.

👨‍🎓 For Students
View Job Opportunities: Browse jobs posted by recruiters.

Pre-Application Analysis: Upload a resume to check its match score against a job before officially applying.

Instant Feedback: See a detailed breakdown of matching and missing skills.

Application Management: View the status (Pending, Accepted, Rejected) of all submitted applications.

👩‍💼 For Recruiters
Effortless Job Posting: Post new job opportunities by filling a form or by uploading a PDF/DOCX job description file.

Automatic Parsing: The system automatically extracts the job title, description, and required skills from uploaded documents.

Candidate Management: View a list of all applicants for each job, ranked by their resume score.

Accept/Reject Workflow: Update the status of applications, which notifies the student on their dashboard.

🛠️ Tech Stack
Frontend: Streamlit

Backend & Core Logic: Python

Database: SQLite

AI / NLP:

Scikit-learn (TfidfVectorizer, cosine_similarity)

pypdf for PDF parsing

python-docx for DOCX parsing

Authentication & Session: passlib for password hashing, streamlit-extras for cookie management.

📁 Project Structure
/Resume/
├── app.py                     # Main login/signup page
├── database_setup.py          # Script to initialize the database
├── file_parser.py             # Helper for parsing JD files
├── resume_analyzer.py         # Core AI logic for resume scoring
├── requirements.txt           # Project dependencies
├── .gitignore                 # Files to be ignored by Git
├── recruitment.db             # The SQLite database file
└── /pages/
    ├── 1_Student_Dashboard.py
    └── 2_Recruiter_Dashboard.py
    
🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.

Prerequisites
Python 3.9 or higher

pip package manager

Installation & Setup
Clone the repository:

Bash

git clone https://github.com/your-username/Resume.git
cd Resume
Create and activate a virtual environment:

Bash

# Create the environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
Install the required packages:
A requirements.txt file should be in the repository. Use it to install all dependencies.

Bash

pip install -r requirements.txt
Initialize the database:
Run the setup script once to create the recruitment.db file and its tables.

Bash

python database_setup.py
Run the Streamlit application:

Bash

streamlit run app.py
Your browser should open to the application's login page.

Usage
Sign Up: Create a new account by selecting either the "Student" or "Recruiter" role.

Log In: Log in to your account. Your session will be remembered if you refresh the page.

Recruiter Workflow:

Navigate to the "Post a New Job" tab.

Fill out the form manually or upload a JD document to auto-fill the fields.

Click "Post Job".

View applicants in the "View Applications" tab and update their status.

Student Workflow:

Browse jobs in the "Search for Jobs" tab.

Expand a job and upload your resume to see your match score.

If satisfied, click "Confirm and Apply".

Check your application status in the "My Applications" tab.
