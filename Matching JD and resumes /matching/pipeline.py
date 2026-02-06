from typing import Dict
from .resume_profile import create_resume_profile
from .text_builder import build_resume_text
from .matcher import match_resume_to_jd
from .cache import CACHE
from parser.resume_parser import parse_resume  


def process_resume(file_path: str, jd_text: str) -> Dict:
    """
    Complete pipeline for a single resume:
    parse -> build text -> match -> create profile -> save to cache.

    Args:
        file_path (str): Path to resume file
        jd_text (str): Job description text

    Returns:
        dict: Resume profile
    """

    # ---------------------------
    # 1️⃣ Parse resume
    # ---------------------------
    parsed_resume = parse_resume(file_path)

    # ---------------------------
    # 2️⃣ Build text for matching
    # ---------------------------
    resume_text = build_resume_text(parsed_resume)

    # ---------------------------
    # 3️⃣ Match against JD
    # ---------------------------
    match_result = match_resume_to_jd(jd_text, resume_text)

    # ---------------------------
    # 4️⃣ Create resume profile
    # ---------------------------
    resume_profile = create_resume_profile(
        parsed_resume=parsed_resume,
        match_score=match_result["score"],
        is_shortlisted=match_result["is_shortlisted"]
    )

    # ---------------------------
    # 5️⃣ Save to cache
    # ---------------------------
    CACHE[resume_profile["resume_id"]] = resume_profile

    return resume_profile


def process_resume_batch(file_paths: list, jd_text: str) -> list:
    """
    Process multiple resumes sequentially.

    Args:
        file_paths (list): List of resume file paths
        jd_text (str): Job description

    Returns:
        list: List of resume profiles
    """
    profiles = []

    for file_path in file_paths:
        profile = process_resume(file_path, jd_text)
        profiles.append(profile)

    return profiles