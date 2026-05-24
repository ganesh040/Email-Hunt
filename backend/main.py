import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import (
    scrape_website_emails,
    scrape_github_org_emails,
    scrape_github_commit_emails,
    scrape_whois_emails
)
from pattern_engine import detect_pattern, generate_candidates, sort_candidates_by_pattern
from smtp_verifier import verify_email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                    "http://localhost:5174",],
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    first_name: str
    last_name: str
    domain: str

@app.post("/api/find-email")
async def find_email(request: EmailRequest):
    domain = request.domain.lower().strip()
    first = request.first_name.strip()
    last = request.last_name.strip()

    try:
        results = await asyncio.wait_for(
            asyncio.gather(
                scrape_website_emails(domain),
                scrape_github_org_emails(domain),
                scrape_github_commit_emails(domain),
                scrape_whois_emails(domain),
            ),
            timeout=15.0
        )
        website_emails, github_org_emails, github_commit_emails, whois_emails = results
    except asyncio.TimeoutError:
        website_emails, github_org_emails, github_commit_emails, whois_emails = [], [], [], []

    found_emails = list(set(
        website_emails +
        github_org_emails +
        github_commit_emails +
        whois_emails
    ))
    
    detected_pattern = detect_pattern(found_emails, domain)
    candidates = generate_candidates(first, last, domain)

    if detected_pattern:
        candidates = sort_candidates_by_pattern(candidates, detected_pattern)
        
    top_3 = candidates[:3]
    verified = []
    for candidate in top_3:
        result = verify_email(candidate["email"])
        verified.append({
            "email": candidate["email"],
            "pattern": candidate["pattern"],
            "smtp_result": result["result"],
            "detail": result["detail"],
            "is_top_guess": candidate == top_3[0]
        })

    return {
        "domain": domain,
        "found_on_web": found_emails,
        "detected_pattern": detected_pattern,
        "candidates": verified,
        "all_patterns": [c["email"] for c in candidates],
        "sources": {
            "website": website_emails,
            "github_org": github_org_emails,
            "github_commits": github_commit_emails,
            "whois": whois_emails,
        }
    }

@app.get("/")
def root():
    return {"status": "Email finder API is running"}