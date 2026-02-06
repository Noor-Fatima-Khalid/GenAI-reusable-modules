from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict
from .config import SIMILARITY_THRESHOLD

# Load model
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def match_resume_to_jd(jd_text: str, resume_text: str) -> Dict:
    """
    Computes similarity between JD and resume text.

    Args:
        jd_text (str): Job description text
        resume_text (str): Resume text built from parsed JSON

    Returns:
        dict: {"score": float, "is_shortlisted": bool}
    """

    # Embed JD and Resume
    jd_embedding = MODEL.encode([jd_text])
    resume_embedding = MODEL.encode([resume_text])

    # Cosine similarity
    score = cosine_similarity(jd_embedding, resume_embedding)[0][0]

    # Shortlist decision
    is_shortlisted = bool(score >= SIMILARITY_THRESHOLD)

    return {
        "score": round(float(score), 4),
        "is_shortlisted": is_shortlisted
    }
