import httpx
import re
import asyncio
from bs4 import BeautifulSoup

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

GENERIC_EMAILS = {
    "admin", "support", "info", "abuse", "contact", "hello", "help",
    "noreply", "no-reply", "domain", "registrar", "hostmaster",
    "webmaster", "postmaster", "domainabuse", "security", "privacy"
}

def is_valid_email(email: str, domain: str) -> bool:
    """Exact domain match — prevents dhiwise.com matching when looking for wise.com"""
    local = email.split("@")[0].lower()
    return (
        email.lower().endswith(f"@{domain}") and
        local not in GENERIC_EMAILS
    )

# ─────────────────────────────────────────────
# PHASE 1 — Website scraping
# ─────────────────────────────────────────────

async def fetch_emails_from_url(client: httpx.AsyncClient, url: str, domain: str) -> list[str]:
    try:
        res = await client.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        found = re.findall(EMAIL_REGEX, soup.get_text())
        return [e for e in found if is_valid_email(e, domain)]
    except Exception:
        return []

async def scrape_website_emails(domain: str) -> list[str]:
    pages_to_check = [
        f"https://{domain}",
        f"https://{domain}/contact",
        f"https://{domain}/about",
        f"https://{domain}/team",
    ]
    async with httpx.AsyncClient(timeout=6, follow_redirects=True) as client:
        results = await asyncio.gather(
            *[fetch_emails_from_url(client, url, domain) for url in pages_to_check]
        )
    emails = set()
    for result in results:
        emails.update(result)
    return list(emails)


async def scrape_github_org_emails(domain: str) -> list[str]:
    emails = set()
    company_name = domain.split(".")[0]

    async with httpx.AsyncClient(timeout=6) as client:
        try:
            res = await client.get(
                f"https://api.github.com/search/users?q={company_name}+type:org",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            data = res.json()

            async def get_email(user):
                try:
                    profile = await client.get(user["url"])
                    email = profile.json().get("email", "")
                    if email and is_valid_email(email, domain):
                        return email
                except Exception:
                    pass
                return None

            items = data.get("items", [])[:3]
            results = await asyncio.gather(*[get_email(u) for u in items])
            emails.update(e for e in results if e)
        except Exception:
            pass

    return list(emails)


# ─────────────────────────────────────────────
# PHASE 2 — GitHub commits extractor (improved)
# ─────────────────────────────────────────────

async def scrape_github_commit_emails(domain: str) -> list[str]:
    emails = set()
    company_name = domain.split(".")[0]

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            # Strategy 1 — search users who mention company in their profile
            res1 = await client.get(
                f"https://api.github.com/search/users?q={company_name}+in:company&per_page=20",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            users_from_company = res1.json().get("items", [])

            # Strategy 2 — search users who have company domain in their email
            res2 = await client.get(
                f"https://api.github.com/search/users?q={domain}+in:email&per_page=20",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            users_from_email = res2.json().get("items", [])

            # Combine both lists, deduplicate by login
            all_users = {u["login"]: u for u in users_from_company + users_from_email}

            async def get_commit_emails_for_user(user):
                found = set()
                try:
                    # Check public profile email first
                    profile_res = await client.get(
                        f"https://api.github.com/users/{user['login']}",
                        headers={"Accept": "application/vnd.github.v3+json"}
                    )
                    profile = profile_res.json()
                    profile_email = profile.get("email", "")
                    if profile_email and is_valid_email(profile_email, domain):
                        found.add(profile_email)

                    # Dig into commits
                    repos_res = await client.get(
                        f"https://api.github.com/users/{user['login']}/repos?per_page=10&sort=updated",
                        headers={"Accept": "application/vnd.github.v3+json"}
                    )
                    repos = repos_res.json()
                    if not isinstance(repos, list):
                        return found

                    for repo in repos[:5]:
                        commits_res = await client.get(
                            f"https://api.github.com/repos/{user['login']}/{repo['name']}/commits?per_page=10",
                            headers={"Accept": "application/vnd.github.v3+json"}
                        )
                        commits = commits_res.json()
                        if not isinstance(commits, list):
                            continue

                        for commit in commits:
                            author_email = commit.get("commit", {}).get("author", {}).get("email", "")
                            committer_email = commit.get("commit", {}).get("committer", {}).get("email", "")
                            for email in [author_email, committer_email]:
                                if email and is_valid_email(email, domain):
                                    found.add(email)

                except Exception:
                    pass
                return found

            results = await asyncio.gather(
                *[get_commit_emails_for_user(u) for u in list(all_users.values())[:15]]
            )
            for result in results:
                emails.update(result)

        except Exception:
            pass

    return list(emails)


# ─────────────────────────────────────────────
# PHASE 2 — WHOIS lookup
# ─────────────────────────────────────────────

async def scrape_whois_emails(domain: str) -> list[str]:
    emails = set()

    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        try:
            res = await client.get(
                f"https://www.whois.com/whois/{domain}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            text = res.text
            found = re.findall(EMAIL_REGEX, text)
            for e in found:
                if is_valid_email(e, domain):
                    emails.add(e)
        except Exception:
            pass

    return list(emails)