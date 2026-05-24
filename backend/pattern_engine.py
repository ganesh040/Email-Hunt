import re
from collections import Counter

GENERIC_LOCALS = {
    "admin", "support", "info", "abuse", "contact", "hello", "help",
    "noreply", "no-reply", "domain", "registrar", "hostmaster",
    "webmaster", "postmaster", "domainabuse", "security", "privacy"
}

def classify_local(local: str) -> list[str]:
    """
    Given a local part (before @), return ALL possible patterns it could match.
    Returns a list because some locals are ambiguous.

    Examples:
        john          → ["firstname"]
        smith         → ["lastname"]
        john.smith    → ["firstname.lastname"]
        j.smith       → ["f.lastname"]
        jsmith        → ["flastname", "firstnamelastname"]  ← ambiguous!
        johnsmith     → ["firstnamelastname"]
    """
    patterns = []

    # Has a dot
    if "." in local:
        parts = local.split(".")
        if len(parts) == 2:
            a, b = parts
            if len(a) == 1 and len(b) == 1:
                patterns.append("f.l")
            elif len(a) == 1:
                patterns.append("f.lastname")       
            elif len(b) == 1:
                patterns.append("firstname.l")       # john.s
            else:
                patterns.append("firstname.lastname") # john.smith
        return patterns

    # No dot — single word
    if local.isalpha():
        length = len(local)

        if length <= 3:
            patterns.append("firstname")            

        elif length <= 6:
            # Could be firstname OR flastname (e.g. "jsmith" = j+smith)
            # If first char looks like initial (single consonant), lean flastname
            if local[0] in "bcdfghjklmnpqrstvwxyz" and length >= 4:
                patterns.append("flastname")         # jsmith
                patterns.append("firstnamelastname") # ambiguous
            else:
                patterns.append("firstname")         # john, anna

        else:
            # Long local — likely firstnamelastname or flastname
            patterns.append("firstnamelastname")     # johnsmith
            patterns.append("flastname")             # juhrich (ambiguous)

    return patterns


def detect_pattern(emails: list[str], domain: str) -> str | None:
    """
    Analyze found emails and detect the company's email pattern.
    Uses voting — the pattern seen most across all emails wins.
    """
    if not emails:
        return None

    votes = Counter()

    for email in emails:
        local = email.split("@")[0].lower()

        # Skip generic emails
        if local in GENERIC_LOCALS:
            continue

        # Skip emails not from this domain
        if domain not in email:
            continue

        possible_patterns = classify_local(local)
        for pattern in possible_patterns:
            # Each ambiguous pattern gets fractional vote
            votes[pattern] += 1 / len(possible_patterns)

    if not votes:
        return None

    return votes.most_common(1)[0][0]


def generate_candidates(first: str, last: str, domain: str) -> list[dict]:
    """
    Generate all possible email candidates.
    Ordered by real-world frequency of each pattern.
    """
    f = first.lower()
    l = last.lower()

    patterns = [
        {"email": f"{f}.{l}@{domain}",   "pattern": "firstname.lastname"},
        {"email": f"{f}{l}@{domain}",     "pattern": "firstnamelastname"},
        {"email": f"{f[0]}{l}@{domain}",  "pattern": "flastname"},
        {"email": f"{f[0]}.{l}@{domain}", "pattern": "f.lastname"},
        {"email": f"{f}@{domain}",        "pattern": "firstname"},
        {"email": f"{l}.{f}@{domain}",    "pattern": "lastname.firstname"},
        {"email": f"{l}@{domain}",        "pattern": "lastname"},
        {"email": f"{f}.{l[0]}@{domain}", "pattern": "firstname.l"},
    ]
    return patterns


def sort_candidates_by_pattern(candidates: list[dict], detected_pattern: str) -> list[dict]:
    """
    Put the candidate matching detected pattern first.
    """
    return sorted(
        candidates,
        key=lambda c: c["pattern"] == detected_pattern,
        reverse=True
    )