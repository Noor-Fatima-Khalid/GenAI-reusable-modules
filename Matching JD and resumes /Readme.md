### Resume–Job Description Matching Module
This module is responsible for matching a batch of parsed resumes against a provided job description as part of the AI Interviewer system. Parsed resumes are first converted into 
structured semantic representations, which are then compared with the job description using sentence embeddings and cosine similarity to compute relevance scores. All candidates are 
ranked and categorized into shortlisted and non-shortlisted groups based on configurable thresholds, with results temporarily stored in a cache to enable human-in-the-loop review. HR 
personnel can inspect, override, or adjust the automated decisions before proceeding to interview scheduling, ensuring transparency, explainability, and controlled decision-making 
within the recruitment pipeline.

### System Architecture
Upload Resumes
      ↓
Parse ALL → store parsed JSONs in cache
      ↓
Match ALL against JD → update cache
      ↓
Show Shortlisted + Rejected to HR
      ↓
HR overrides (optional)
      ↓
Persist final decisions
      ↓
Schedule interviews
