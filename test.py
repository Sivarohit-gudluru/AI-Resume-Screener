<<<<<<< HEAD
import os
import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text.lower()

def extract_keywords(text):
    skills = [
        "python", "sql", "machine learning", "fastapi",
        "pandas", "numpy", "rest api", "apis"
    ]

    text = text.lower()

    found_skills = []

    for skill in skills:
        if skill in text:
            found_skills.append(skill)

    return set(found_skills)

def load_job_description():
    with open("job_description.txt", "r") as f:
        return f.read().lower()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_score(resume_text, job_text):
    documents = [resume_text, job_text]

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    # keep keyword extraction for display
    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_text)
    matched = resume_words.intersection(job_words)

    return score, matched

resume_folder = "resumes"
job_text = load_job_description()

results = []

for file in os.listdir(resume_folder):
    if file.endswith(".pdf"):
        path = os.path.join(resume_folder, file)

        resume_text = extract_text_from_pdf(path)
        score, matched = calculate_score(resume_text, job_text)

        results.append((file, score, matched))

results.sort(key=lambda x: x[1], reverse=True)

print("\n===== 📊 Resume Ranking =====\n")

for i, (file, score, matched) in enumerate(results):
    print(f"{i+1}. {file} → Match Score: {score:.2f}%")
    print(f"Matched Skills: {list(matched)[:10]}")
=======
import os
import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text.lower()

def extract_keywords(text):
    skills = [
        "python", "sql", "machine learning", "fastapi",
        "pandas", "numpy", "rest api", "apis"
    ]

    text = text.lower()

    found_skills = []

    for skill in skills:
        if skill in text:
            found_skills.append(skill)

    return set(found_skills)

def load_job_description():
    with open("job_description.txt", "r") as f:
        return f.read().lower()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_score(resume_text, job_text):
    documents = [resume_text, job_text]

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    # keep keyword extraction for display
    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_text)
    matched = resume_words.intersection(job_words)

    return score, matched

resume_folder = "resumes"
job_text = load_job_description()

results = []

for file in os.listdir(resume_folder):
    if file.endswith(".pdf"):
        path = os.path.join(resume_folder, file)

        resume_text = extract_text_from_pdf(path)
        score, matched = calculate_score(resume_text, job_text)

        results.append((file, score, matched))

results.sort(key=lambda x: x[1], reverse=True)

print("\n===== 📊 Resume Ranking =====\n")

for i, (file, score, matched) in enumerate(results):
    print(f"{i+1}. {file} → Match Score: {score:.2f}%")
    print(f"Matched Skills: {list(matched)[:10]}")
>>>>>>> e79958e (final update with gap analysis + reports)
    print("-" * 50)