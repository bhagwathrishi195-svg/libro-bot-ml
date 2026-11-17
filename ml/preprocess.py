import re
import unicodedata
from datetime import datetime, date
from library_kb import SUBJECTS

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "twenty": 20, "thirty": 30, "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "das": 10,
}

DAY_DICTIONARY = {
    "monday": ["monday", "mon", "somwar"],
    "tuesday": ["tuesday", "tue", "tues", "mangalwar"],
    "wednesday": ["wednesday", "wed", "budhwar"],
    "thursday": ["thursday", "thu", "thur", "thurs", "guruwar"],
    "friday": ["friday", "fri", "shukrawar"],
    "saturday": ["saturday", "sat", "shaniwar"],
    "sunday": ["sunday", "sun", "raviwar"],
}

MONTHS_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def stem_word(w: str) -> str:
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("ss"):
        return w
    if len(w) > 3 and w.endswith("s"):
        return w[:-1]
    return w


def normalize_text(text: str) -> str:
    if not text:
        return ""
    q = unicodedata.normalize("NFKD", str(text).lower())
    q = "".join(ch for ch in q if not unicodedata.combining(ch))
    q = q.replace("₹", " rs ").replace("&", " and ")
    q = re.sub(r"[^a-z0-9]+", " ", q).strip()
    tokens = [stem_word(t) for t in q.split() if t]
    return " ".join(tokens)


def parse_date_from_text(raw: str):
    s = str(raw or "")
    # YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    m = re.search(r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # DD-MM-YYYY / DD/MM/YYYY / DD.MM.YYYY
    m = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2})\b", s)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    # "15 Oct 2026" / "15th October, 2026"
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3})[a-z]*\.?,?\s+(20\d{2})\b", s, re.I)
    if m and m.group(2).lower() in MONTHS_MAP:
        try:
            return date(int(m.group(3)), MONTHS_MAP[m.group(2).lower()], int(m.group(1)))
        except ValueError:
            pass

    # "Oct 15, 2026"
    m = re.search(r"\b([a-z]{3})[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d{2})\b", s, re.I)
    if m and m.group(1).lower() in MONTHS_MAP:
        try:
            return date(int(m.group(3)), MONTHS_MAP[m.group(1).lower()], int(m.group(2)))
        except ValueError:
            pass

    if re.search(r"\btoday\b", s, re.I):
        return datetime.now().date()

    return None


def extract_entities(raw_text: str) -> dict:
    """Extract structured entities for dynamic response generation."""
    s = str(raw_text or "")
    q = normalize_text(s)
    tokens = [str(WORD_NUMBERS[t]) if t in WORD_NUMBERS else t for t in q.split()]
    q_num = " ".join(tokens)

    entities = {}

    # 1. Day of week
    for canonical_day, variants in DAY_DICTIONARY.items():
        if any(re.search(rf"\b{re.escape(v)}\b", q_num) for v in variants):
            entities["day"] = canonical_day
            break

    # 2. "Open now" live check flag
    if re.search(r"\b(now|today|currently|right now)\b", q_num):
        entities["is_now"] = True

    # 3. Floor extraction
    if re.search(r"\bground floor\b", q_num):
        entities["floor"] = "ground"
    elif re.search(r"\b(first|1st) floor\b", q_num):
        entities["floor"] = "first"
    elif re.search(r"\b(second|2nd) floor\b", q_num):
        entities["floor"] = "second"

    # 4. Subject matches (longest key match wins)
    matched_subjects = []
    padded_q = f" {q_num} "
    for subj in SUBJECTS:
        best_len = 0
        for k in subj["keys"]:
            nk = normalize_text(k)
            if nk and f" {nk} " in padded_q:
                best_len = max(best_len, len(nk))
        if best_len > 0:
            matched_subjects.append((best_len, subj))
    if matched_subjects:
        matched_subjects.sort(key=lambda x: x[0], reverse=True)
        top_len = matched_subjects[0][0]
        entities["subjects"] = [
            subj for length, subj in matched_subjects[:3] if length >= top_len - 2
        ]

    # 5. Overdue days & book count
    days_match = re.search(r"\b(\d+)\s*(?:day|d|din)\b", q_num)
    books_match = re.search(r"\b(\d+)\s*(?:book|copy|copies)\b", q_num)
    if days_match:
        entities["days"] = int(days_match.group(1))
    if books_match:
        entities["books"] = max(1, int(books_match.group(1)))

    # 6. Date extraction
    parsed_dt = parse_date_from_text(s)
    if parsed_dt:
        entities["date"] = parsed_dt.isoformat()

    # 7. User category (faculty / book_bank / student)
    if re.search(r"\b(faculty|professor|prof|teacher)\b", q_num):
        entities["category"] = "faculty"
    elif re.search(r"\bbook bank\b", q_num):
        entities["category"] = "book_bank"
    elif re.search(r"\b(student|ug|pg|phd|scholar|staff)\b", q_num):
        entities["category"] = "student"

    return entities
