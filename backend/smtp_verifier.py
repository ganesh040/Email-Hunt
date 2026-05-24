import smtplib
import dns.resolver
from enum import Enum

class VerifyResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"      
    NO_MX = "no_mx_record"   

def get_mx_record(domain: str) -> str | None:
    try:
        records = dns.resolver.resolve(domain, "MX")
        # Pick the one with lowest priority number (highest priority)
        mx = sorted(records, key=lambda r: r.preference)[0]
        return str(mx.exchange).rstrip(".")
    except Exception:
        return None

def verify_email(email: str) -> dict:
    domain = email.split("@")[1]
    
    # Step 1 — get MX record
    mx_host = get_mx_record(domain)
    if not mx_host:
        return {
            "email": email,
            "result": VerifyResult.NO_MX.value,
            "detail": "Domain has no mail server"
        }
    
    # Step 2 — SMTP check
    try:
        with smtplib.SMTP(timeout=10) as smtp:
            smtp.connect(mx_host, 25)
            smtp.helo("check.com")
            smtp.mail("check@check.com")
            code, message = smtp.rcpt(email)
            smtp.quit()
            
            if code == 250:
                return {
                    "email": email,
                    "result": VerifyResult.VALID.value,
                    "detail": "Mail server accepted the address"
                }
            elif code == 550:
                return {
                    "email": email,
                    "result": VerifyResult.INVALID.value,
                    "detail": "Mail server rejected the address"
                }
            else:
                return {
                    "email": email,
                    "result": VerifyResult.UNKNOWN.value,
                    "detail": f"Inconclusive response: {code}"
                }
    except smtplib.SMTPConnectError:
        return {
            "email": email,
            "result": VerifyResult.UNKNOWN.value,
            "detail": "Could not connect to mail server (port 25 blocked)"
        }
    except Exception as e:
        return {
            "email": email,
            "result": VerifyResult.UNKNOWN.value,
            "detail": f"Error: {str(e)}"
        }