\# 🔍 AI Candidate Intelligence Platform



Cross-references a candidate's resume claims against their real GitHub activity to flag unverified skills — because talk is cheap, code isn't.



🔗 \*\*Live Demo:\*\* \[Try it here](https://ai-candidate-intelligence-platform-psdkfyvwpycffbsc9ynahu.streamlit.app/)



\## What it does



Recruiters are flooded with resumes padded with keyword-stuffed skills that are hard to verify. This tool:



1\. Extracts technical skills from an uploaded resume PDF using LLM-based parsing (Gemini)

2\. Auto-detects the candidate's GitHub username from the resume text

3\. Pulls their live repository language data via the GitHub REST API

4\. Cross-references claimed vs. demonstrated skills and generates an \*\*Evidence Confidence Score\*\*

5\. Supports \*\*multiple resumes at once\*\*, ranking candidates against recruiter-specified required skills

6\. Generates targeted, gap-specific interview questions for each candidate



\## Tech Stack



Python, Streamlit, Google Gemini API, GitHub REST API, PyPDF



\## How it works



\- \*\*PDF parsing\*\* — `pypdf` extracts raw text from uploaded resumes

\- \*\*LLM prompting\*\* — structured prompts force Gemini to return clean JSON (skills list, evaluation object)

\- \*\*GitHub API integration\*\* — fetches public repo data and computes language frequency using hash maps

\- \*\*Caching\*\* — `st.cache\_data` avoids redundant API calls on Streamlit reruns

\- \*\*Ranking\*\* — candidates are sorted by confidence score using Python's `sort()` with a custom key



\## Running locally



```bash

git clone https://github.com/shamal2005/ai-candidate-intelligence-platform.git

cd ai-candidate-intelligence-platform

pip install -r requirements.txt

```



Create a `.env` file with:

GEMINI\_API\_KEY=your\_key\_here



Then run:

```bash

streamlit run app.py

```



\## Known Limitations



\- Only public GitHub repositories are visible to the tool — private work isn't counted

\- Relies on the resume explicitly containing a GitHub profile link for auto-detection

