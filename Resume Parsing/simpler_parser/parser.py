import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# -------------------------------
# 1. Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# -------------------------------
# 2. Read PDF with link extraction
# -------------------------------
def read_pdf_with_links(path: str) -> str:
    doc = fitz.open(path)
    content = []

    for page in doc:
        text = page.get_text("text")

        links = page.get_links()
        urls = []

        for link in links:
            uri = link.get("uri")
            if uri:
                urls.append(uri)

        if urls:
            text += "\n\n[EXTRACTED LINKS]\n" + "\n".join(urls)

        content.append(text)

    return "\n\n".join(content)

# -------------------------------
# 3. Path to resume PDF (LOCAL)
# -------------------------------
PDF_PATH = "resume.pdf" 

if not os.path.exists(PDF_PATH):
    raise FileNotFoundError(f"Resume not found: {PDF_PATH}")

resume_text = read_pdf_with_links(PDF_PATH)

# -------------------------------
# 4. Gemini model
# -------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

# -------------------------------
# 5. Prompt (STRICT JSON)
# -------------------------------
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

# -------------------------------
# 6. Run extraction
# -------------------------------
response = llm.invoke(prompt.format(resume=resume_text))

print("\n=== RAW OUTPUT ===\n")
print(response.content)
