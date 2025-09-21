import io # New import
from pypdf import PdfReader # New import to replace fitz
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- THIS IS THE UPDATED FUNCTION ---
def extract_text_from_pdf(file_bytes):
    """Extracts text from an in-memory PDF file using pypdf."""
    try:
        # Wrap the bytes in a file-like object
        pdf_file = io.BytesIO(file_bytes)
        # Create a PDF reader object
        reader = PdfReader(pdf_file)
        text = ""
        # Loop through each page and extract text
        for page in reader.pages:
            text += page.extract_text() or "" # Add 'or ""' to handle empty pages
        return text
    except Exception as e:
        print(f"Error reading PDF with pypdf: {e}")
        return None

# --- THE REST OF THE FILE REMAINS THE SAME ---

def calculate_hard_match(resume_text, jd_keywords):
    """Calculates a score based on keyword presence."""
    found_keywords = []
    missing_keywords = []
    
    if not jd_keywords:
        return 0, [], []
        
    for keyword in jd_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', resume_text, re.IGNORECASE):
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
            
    score = (len(found_keywords) / len(jd_keywords)) * 100
    return score, found_keywords, missing_keywords

def calculate_semantic_similarity(resume_text, jd_text):
    """Calculates cosine similarity between two texts."""
    texts = [resume_text, jd_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return cosine_sim[0][0] * 100
    except ValueError:
        return 0.0

def analyze_resume(resume_bytes, jd_description, required_skills_str):
    """
    The main analysis function that orchestrates the process and returns results.
    """
    resume_text = extract_text_from_pdf(resume_bytes)
    if not resume_text:
        return None 

    # Convert the comma-separated skills string into a list
    jd_keywords = [skill.strip() for skill in required_skills_str.split(',')]
    
    # 1. Perform Hard Match (Keywords)
    hard_match_score, found, missing = calculate_hard_match(resume_text, jd_keywords)
    
    # 2. Perform Semantic Match (Context)
    semantic_score = calculate_semantic_similarity(resume_text, jd_description)
    
    # 3. Calculate Final Weighted Score
    final_score = (0.4 * hard_match_score) + (0.6 * semantic_score)
    
    # 4. Return all results in a dictionary
    return {
        "final_score": final_score,
        "hard_match_score": hard_match_score,
        "semantic_score": semantic_score,
        "found_keywords": found,
        "missing_keywords": missing
    }