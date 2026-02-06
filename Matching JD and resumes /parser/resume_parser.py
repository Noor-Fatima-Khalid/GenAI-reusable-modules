
import os
import json
import fitz  # PyMuPDF
from docx import Document
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# -------------------------------
# File Readers
# -------------------------------
def read_pdf_with_links(path: str) -> str:
    doc = fitz.open(path)
    content = []

    for page in doc:
        text = page.get_text("text")
        links = page.get_links()

        urls = [link.get("uri") for link in links if link.get("uri")]
        if urls:
            text += "\n\n[EXTRACTED LINKS]\n" + "\n".join(urls)

        content.append(text)

    return "\n\n".join(content)


def read_docx(path: str) -> str:
    document = Document(path)
    return "\n".join([para.text for para in document.paragraphs])


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# -------------------------------
# Unified Resume Text Loader
# -------------------------------
def load_resume_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return read_pdf_with_links(path)
    elif ext == ".docx":
        return read_docx(path)
    elif ext == ".txt":
        return read_txt(path)
    else:
        raise ValueError(f"Unsupported resume format: {ext}")


# -------------------------------
# MAIN PARSER FUNCTION
# -------------------------------
def parse_resume(path: str) -> dict:
    """
    Parses resume (.pdf, .docx, .txt) and returns structured JSON.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume not found: {path}")

    resume_text = load_resume_text(path)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

    prompt = PromptTemplate(
        input_variables=["resume"],
        template="""
You are an expert resume parser.

IMPORTANT:
- Use exact URLs found in the resume text or under [EXTRACTED LINKS]
- Do NOT infer or fabricate GitHub or LinkedIn URLs
- If no explicit URL exists, return null

Extract:
- Full name
- Contact info (email, phone)
- GitHub link
- LinkedIn link
- Highest qualification
- University
- Experience (chronological, label technical vs non-technical)
- Projects (name, description, tech stack)
- Coursework keywords
- Technical skills summary
- Extracurricular / leadership experience

Rules:
- Preserve chronological order
- Output ONLY a JSON object
- Use exactly these keys:
{{
  "name",
  "contact_info",
  "github_link",
  "linkedin",
  "qualification",
  "university",
  "experience",
  "projects",
  "coursework_keywords",
  "skills_summary",
  "extracurricular"
}}
- Set missing fields to null

Resume:
{resume}

JSON:
"""
    )

    response = llm.invoke(prompt.format(resume=resume_text))
    return safe_json_parse(response.content)

import json
import re

def safe_json_parse(text: str) -> dict:
    """
    Extracts and parses JSON object from LLM output.
    Raises clear error if JSON not found.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in LLM response")

    json_str = match.group()
    return json.loads(json_str)
