import os
import json
import re
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import requests
import streamlit as st

st.set_page_config(page_title="Candidate Intelligence Platform", page_icon="🔍", layout="wide")
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="stMetric"] {
        background-color: #1c1f26;
        border: 1px solid #2d323c;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #2d323c;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #f0f2f6;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

st.title("🔍 AI Candidate Intelligence Platform")
st.caption("Cross-referencing resume claims against real GitHub activity — because talk is cheap, code isn't.")


@st.cache_data
def get_github_languages(username):
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    data = response.json()
    language_counts = {}
    for repo in data:
        language = repo["language"]
        if language in language_counts:
            language_counts[language] += 1
        else:
            language_counts[language] = 1
    return language_counts


@st.cache_data
def extract_skills(resume_text):
    prompt = f"""
    Extract only the technical skills mentioned in this resume text.
    Return ONLY a JSON array of strings, nothing else.

    Resume text:
    {resume_text}
    """
    gemini_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return json.loads(gemini_response.text)


@st.cache_data
def evaluate_candidate(resume_skills, github_languages, required_skills):
    required_text = ", ".join(required_skills) if required_skills else "Not specified"

    evaluation_prompt = f"""
    You are evaluating a job candidate. Compare their claimed resume skills against their actual GitHub language usage.
    The recruiter requires these specific skills: {required_text}

    Resume claimed skills: {resume_skills}
    GitHub language distribution: {github_languages}

    Return ONLY a JSON object with this exact structure, nothing else:
    {{
        "confidence_score": <a number from 0 to 100>,
        "reasoning": "<a short explanation of the score>",
        "mismatches": ["<skill claimed but not evidenced in GitHub>", ...],
        "required_skills_match": ["<which required skills ARE evidenced on GitHub>"],
        "required_skills_missing": ["<which required skills are NOT evidenced on GitHub>"],
        "interview_questions": ["<question 1>", "<question 2>", "<question 3>"]
    }}
    """
    evaluation_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=evaluation_prompt
    )
    return json.loads(evaluation_response.text)


st.sidebar.header("Candidate Input")
resume_files = st.sidebar.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
required_skills_input = st.sidebar.text_input("Required Skills (comma-separated)", placeholder="e.g. Python, React, AWS")
required_skills = [s.strip() for s in required_skills_input.split(",") if s.strip()]

if resume_files:
    all_candidates = []

    with st.spinner(f"Analyzing {len(resume_files)} candidate(s)..."):
        for resume_file in resume_files:
            reader = PdfReader(resume_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            match = re.search(r"github\.com/([A-Za-z0-9\-]+)", text)
            username = match.group(1) if match else None

            if username:
                language_counts = get_github_languages(username)
                skills = extract_skills(text)
                evaluation = evaluate_candidate(skills, language_counts, required_skills)

                all_candidates.append({
                    "filename": resume_file.name,
                    "username": username,
                    "text": text,
                    "skills": skills,
                    "language_counts": language_counts,
                    "evaluation": evaluation
                })
            else:
                st.warning(f"⚠️ Couldn't find a GitHub username in **{resume_file.name}** — skipped.")

    if all_candidates:
        all_candidates.sort(key=lambda c: c["evaluation"]["confidence_score"], reverse=True)

        st.divider()
        st.subheader("🏆 Candidate Ranking")

        for rank, candidate in enumerate(all_candidates, start=1):
            score = candidate["evaluation"]["confidence_score"]
            st.write(f"**#{rank} — {candidate['username']}** ({candidate['filename']}) — Confidence Score: {score}/100")

        st.divider()
        st.subheader("📋 Detailed Candidate Reports")

        for rank, candidate in enumerate(all_candidates, start=1):
            with st.expander(f"#{rank} — {candidate['username']} ({candidate['evaluation']['confidence_score']}/100)"):
                st.write(candidate["evaluation"]["reasoning"])

                if required_skills:
                    st.write("**Required Skills Matched:**", ", ".join(candidate["evaluation"].get("required_skills_match", [])) or "None")
                    st.write("**Required Skills Missing:**", ", ".join(candidate["evaluation"].get("required_skills_missing", [])) or "None")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("📊 GitHub Language Distribution")
                    st.bar_chart(candidate["language_counts"])
                with col2:
                    st.write("📄 Resume-Claimed Skills")
                    st.json(candidate["skills"])

                st.write("⚠️ Mismatches")
                for m in candidate["evaluation"]["mismatches"]:
                    st.markdown(f"- {m}")

                st.write("🎯 Suggested Interview Questions")
                for q in candidate["evaluation"]["interview_questions"]:
                    st.markdown(f"- {q}")