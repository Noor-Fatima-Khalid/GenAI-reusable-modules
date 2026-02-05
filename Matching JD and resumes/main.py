from matching.pipeline import process_resume_batch

jd_text = """We are looking for a Junior Software Engineer.

Required skills:
Python, Data Structures, REST APIs, Git, SQL.

Responsibilities:
Develop backend services using Python.
Work with APIs and databases.
Collaborate with cross-functional teams.
Write clean and maintainable code.

Qualification:
Bachelor’s degree in Computer Science or Software Engineering."""

resume_files = ["resumes/noor.pdf", "resumes/john.docx"]

profiles = process_resume_batch(resume_files, jd_text)

# CACHE now contains all profiles keyed by resume_id
print(profiles[0])
