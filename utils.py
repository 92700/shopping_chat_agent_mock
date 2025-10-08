import re

def parse_budget(text: str):
    t = text.replace('\u20b9','₹')
    m = re.search(r"(under|below)\s*₹?\s*([0-9,]+)k?", t, re.IGNORECASE)
    if m:
        num = m.group(2).replace(',','')
        if 'k' in m.group(0).lower():
            val = int(num) * 1000
        else:
            val = int(num)
        return None, val
    m2 = re.search(r"([0-9,]+)\s*(?:inr|rs|₹)", t, re.IGNORECASE)
    if m2:
        val = int(m2.group(1).replace(',',''))
        return None, val
    m3 = re.search(r"(\d{1,3})k\b", t, re.IGNORECASE)
    if m3:
        return None, int(m3.group(1)) * 1000
    return None, None

BRAND_KEYWORDS = ["google","pixel","oneplus","xiaomi","mi","samsung","realme","vivo","oppo","motorola","poco","iqoo"]

def extract_brands(text: str):
    found = []
    t = text.lower()
    for b in BRAND_KEYWORDS:
        if b in t:
            found.append(b.capitalize())
    return list(set(found))

FEATURE_MAP = {
    'ois': 'OIS', 'eis': 'EIS', 'fast charging': 'fast_charging', 'wireless charging': 'wireless_charging',
    '120hz': '120Hz', '90hz':'90Hz', '5g':'5G', 'ip68':'IP68'
}

def extract_features(text: str):
    t = text.lower()
    found = []
    for k in FEATURE_MAP.keys():
        if k in t:
            found.append(FEATURE_MAP[k])
    return found
