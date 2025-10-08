import re

SENSITIVE_PATTERNS = [r"api[_-]?key", r"secret", r"system prompt", r"private key", r"token", r"ssh key"]
TOXIC_PATTERNS = [r"\b(trash|kill|die|hate)\b"]

def is_sensitive_query(text: str) -> bool:
    t = text.lower()
    for pat in SENSITIVE_PATTERNS:
        if re.search(pat, t):
            return True
    return False

def is_toxic(text: str) -> bool:
    t = text.lower()
    for pat in TOXIC_PATTERNS:
        if re.search(pat, t):
            return True
    return False

def sanitize_llm_output(output: str, context_items: list) -> str:
    ctx_text = str(context_items)
    mentions = re.findall(r"(\d{2,4}\s*(?:mAh|MP))", output)
    for m in mentions:
        if m not in ctx_text:
            return "I cannot confirm that detail; it is not available in the dataset. Here's what I can confirm:\n" + output
    return output
