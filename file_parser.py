import io
import re
from pypdf import PdfReader
import docx

def extract_text_from_pdf_bytes(file_bytes):
    """Extracts text from an in-memory PDF file."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""

def extract_text_from_docx_bytes(file_bytes):
    """Extracts text from an in-memory DOCX file."""
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception:
        return ""

def parse_job_description_text(text):
    """
    A simple heuristic-based parser to extract title, description, and skills.
    This is a best-effort parser and may require manual edits.
    """
    title = "Job Title Not Found"
    skills = ""
    
    # Try to find the title on a line that starts with "Job Title"
    # Otherwise, fallback to the first non-empty line of the document
    title_match = re.search(r"^(Job Title:?)\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
    if title_match:
        title = title_match.group(2).strip()
    else:
        lines = [line for line in text.splitlines() if line.strip()]
        if lines:
            title = lines[0].strip()

    # Try to find skills on lines following keywords like "Skills" or "Requirements"
    skills_keywords = ['skills', 'requirements', 'qualifications', 'must have']
    skills_section = ""
    for keyword in skills_keywords:
        # Search for the keyword at the beginning of a line
        skills_match = re.search(rf"^\s*{keyword}:?\s*\n?(.*)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if skills_match:
            # Grab the text until the next blank line
            skills_section = skills_match.group(1).split('\n\n')[0]
            break # Stop after finding the first match
    
    if skills_section:
        # A simple way to format skills: replace newlines/bullets with commas
        skills = re.sub(r'[\n\-\*•]', ', ', skills_section).strip()
        skills = re.sub(r'(,\s*){2,}', ', ', skills) # Replace multiple commas with one
    
    return {
        "title": title,
        "description": text, # The full text is used as the description
        "skills": skills
    }