import sqlite3

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# 1. Create Users Table
# role: 1 for Student, 2 for Recruiter
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role INTEGER NOT NULL 
);
''')

# 2. Create Jobs Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT,
    FOREIGN KEY (recruiter_id) REFERENCES users(id)
);
''')

# 3. Create Applications Table
# status: Pending, Accepted, Rejected
cursor.execute('''
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    resume_score REAL,
    matching_skills TEXT,
    missing_skills TEXT,
    status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);
''')

print("Database and tables created successfully!")

conn.commit()
conn.close()