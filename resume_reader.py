import os
import json
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

load_dotenv()
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

reader = PdfReader("resume.pdf")

text = ""
for page in reader.pages:
    text += page.extract_text()

prompt = f"""
Extract only the technical skills mentioned in this resume text.
Return ONLY a JSON array of strings, nothing else.

Resume text:
{text}
"""

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)
print(response.text)
skills = json.loads(response.text)
print(skills)
print(type(skills))