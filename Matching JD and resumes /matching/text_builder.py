from typing import Dict, List

def build_resume_text(parsed_resume: Dict) -> str:
    """
    Builds semantic text from parsed resume JSON
    for JD resume matching.
    """

    sections: List[str] = []

    # ---------------------------
    # Education
    # ---------------------------
    qualification = parsed_resume.get("qualification")
    university = parsed_resume.get("university")

    if qualification or university:
        sections.append(
            f"Education: {qualification or ''} at {university or ''}".strip()
        )

    # ---------------------------
    # Technical Experience
    # ---------------------------
    experiences = parsed_resume.get("experience", [])
    tech_exp = []

    for exp in experiences:
        if exp.get("type") == "technical":
            line = f"{exp.get('title')} at {exp.get('organization')}"
            if exp.get("description"):
                line += f". {exp.get('description')}"
            tech_exp.append(line)

    if tech_exp:
        sections.append(
            "Technical Experience:\n" + "\n".join(tech_exp)
        )

    # ---------------------------
    # Projects
    # ---------------------------
    projects = parsed_resume.get("projects", [])
    project_lines = []

    for proj in projects:
        line = proj.get("name", "")
        if proj.get("description"):
            line += f": {proj['description']}"
        if proj.get("tech_stack"):
            line += f" | Tech Stack: {proj['tech_stack']}"
        project_lines.append(line)

    if project_lines:
        sections.append(
            "Projects:\n" + "\n".join(project_lines)
        )

    # ---------------------------
    # Coursework
    # ---------------------------
    coursework = parsed_resume.get("coursework_keywords")
    if coursework:
        sections.append(f"Relevant Coursework: {coursework}")

    # ---------------------------
    # Skills
    # ---------------------------
    skills = parsed_resume.get("skills_summary")
    if skills:
        sections.append(f"Technical Skills: {skills}")

    # ---------------------------
    # Profiles 
    # ---------------------------
    github = parsed_resume.get("github_link")
    linkedin = parsed_resume.get("linkedin")

    if github:
        sections.append(f"GitHub profile available.")
    if linkedin:
        sections.append(f"LinkedIn profile available.")

    return "\n\n".join(sections)
