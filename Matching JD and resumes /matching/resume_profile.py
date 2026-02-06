from uuid import uuid4
from typing import Dict


def create_resume_profile(
    parsed_resume: Dict,
    match_score: float,
    is_shortlisted: bool
) -> Dict:
    """
    Creates a standardized resume profile object.

    Args:
        parsed_resume (dict): Output from resume parser
        match_score (float): JDresume similarity score
        is_shortlisted (bool): AI shortlist decision

    Returns:
        dict: Resume profile
    """

    return {
        "resume_id": str(uuid4()),
        "parsed_resume": parsed_resume,
        "matching": {
            "score": round(match_score, 4),
            "is_shortlisted": is_shortlisted
        }
    }
