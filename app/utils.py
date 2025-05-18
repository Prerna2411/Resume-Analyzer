import re
def compute_overlap(keywords1, keywords2):
    return len(set(keywords1) & set(keywords2)) / max(len(set(keywords1)), 1)

def parse_experience(text):
    matches = re.findall(r'(\d+)\+?\s+years?', text.lower())
    years = [int(m) for m in matches]
    return max(years) if years else 0