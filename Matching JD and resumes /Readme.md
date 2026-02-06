## Resume–Job Description Matching Module
This module is responsible for matching a batch of parsed resumes against a provided job description as part of the AI Interviewer system. Parsed resumes are first converted into structured semantic representations, which are then compared with the job description using sentence embeddings and cosine similarity to compute relevance scores. All candidates are ranked and categorized into shortlisted and non-shortlisted groups based on configurable thresholds, with results temporarily stored in a cache to enable human-in-the-loop review. HR 
personnel can inspect, override, or adjust the automated decisions before proceeding to interview scheduling, ensuring transparency, explainability, and controlled decision-making within the recruitment pipeline.

## System Architecture
Upload Resumes <br>
      ↓ <br>
Parse <br>
      ↓ <br>
Match against JD → update cache <br>
      ↓<br>
Show Shortlisted + Rejected to HR <br>
      ↓ <br>
HR overrides <br>
      ↓ <br>
Persist final decisions (store to db at this stage) <br>
      ↓ <br> 
Schedule interviews <br>

### This repo contains code till Match ALL against JD → update cache. The parser module is in the other folder in this repo.
