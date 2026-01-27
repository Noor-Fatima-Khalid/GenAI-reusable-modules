from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
from google.colab import userdata

# api key setup
os.environ["GOOGLE_API_KEY"] = userdata.get("GOOGLE_API_KEY")

# embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# split resume into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_text(text)

# vector database (faiss)
vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": len(chunks)})

# model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# prompt
prompt_template = """
You are a precise and structured resume parser designed to extract technical information accurately.

From the given resume context, extract the following details:
- Full name
- Contact information (phone number, email)
- GitHub profile link (look for any text starting with 'github.com' or containing 'GitHub')
- LinkedIn profile link
- Qualification and university
- Technical experience (jobs, internships, interns, research, technical roles)
- Projects (name, description, and tech stack)
- Coursework (if any heading named 'Coursework' or 'Relevant Coursework')
- Technical skills and tools
- Extracurricular or leadership experience (roles that are **not primarily technical**, such as MLSA Lead, GDSC Lead, Event Organizer, Club Coordinator, etc.)

Guidelines:
- If a role clearly involves programming, software, research, data, AI, or engineering, classify it under **experience** — even if the title includes 'Lead'.
- Only move to **extracurricular** if it is mainly about community, coordination, or event management.
- Do not omit any experience entries that mention technical skills or projects.
- Preserve chronological order if visible.

Context:
{context}

Question:
{question}

Return ONLY a valid JSON object with these keys:
name, contact_info, github_link, linkedin, qualification, university, experience, projects, coursework_keywords, skills_summary, extracurricular.

If a field doesn’t exist, set it to null.
"""



prompt = PromptTemplate(
     template=prompt_template,
     input_variables=["context", "question"]
      )

# rag chain
chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# ask the chain for keywords
query = "Extract all the details from this resume including name, qualification, university, contact info, github, linkedin, projects, experience, and technical keywords."
result = chain.invoke({"query": query})

print(result["result"])
