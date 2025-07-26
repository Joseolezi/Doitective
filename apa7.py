import re

############# APA 7 Reference Generator ###############

def format_authors_apa7(authors_str):
    if not authors_str:
        return "Unknown Author"
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]
    formatted_authors = []
    for auth in authors:
        parts = auth.split()
        if len(parts) == 0:
            continue
        last_name = parts[-1]
        initials = [p[0].upper() + "." for p in parts[:-1] if p]
        formatted_author = f"{last_name}, {' '.join(initials)}"
        formatted_authors.append(formatted_author)
    n = len(formatted_authors)
    if n <= 20:
        if n == 1:
            return formatted_authors[0]
        elif n == 2:
            return f"{formatted_authors[0]} & {formatted_authors[1]}"
        else:
            return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        # Más de 20 autores: primeros 19, ..., último autor
        first_19 = ", ".join(formatted_authors[:19])
        last = formatted_authors[-1]
        return f"{first_19}, ... , & {last}"

def sentence_case(text):
    if not text:
        return ""
    text = text.strip()
    return text[0].upper() + text[1:].lower()

def title_case(text):
    if not text:
        return ""
    minor_words = {
        "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
        "at", "by", "in", "of", "on", "to", "up", "via", "as", "per"
    }
    words = re.split(r'(\s+)', text)
    result = []
    for i, word in enumerate(words):
        if word.isspace():
            result.append(word)
            continue
        lower_word = word.lower()
        if i == 0 or i == len(words) - 1 or lower_word not in minor_words:
            result.append(word.capitalize())
        else:
            result.append(lower_word)
    return "".join(result)

def generate_apa_reference_7(entry):
    authors = format_authors_apa7(entry.get('Authors', ''))
    year = entry.get('Year', '')
    year_text = f"({year})" if year else "(n.d.)"
    title = sentence_case(entry.get('Title', '').strip())
    journal = title_case(entry.get('Indexed in', '').strip())
    volume = entry.get('Volume', '').strip()
    issue = entry.get('Issue', '').strip()
    pages = entry.get('Pages', '').strip()
    doi = entry.get('DOI', '').strip()

    vol_issue = ""
    if volume:
        vol_issue = volume
        if issue:
            vol_issue += f"({issue})"
    pages_text = f", {pages}" if pages else ""

    ref = f"{authors} {year_text}. {title}. "
    if journal:
        ref += f"*{journal}*"
        if vol_issue:
            ref += f", *{vol_issue}*"
        ref += pages_text + ". "
    else:
        ref += ". "
    if doi:
        ref += f"https://doi.org/{doi}"
    return ref.strip()
