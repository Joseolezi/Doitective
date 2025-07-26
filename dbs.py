# dbs_py
import os
import pandas as pd
import json
import style as s
language = 'en'  # Default language

with open('localization.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)

EXTENSIONS = ['.csv', '.xls', '.xlsx', '.json']
STANDARD_FIELDS = [
    'Doitective','DOI','Open Access?', 'Title', 'Year', 'First author', 'Origin database', 
    'Indexed in', 'OpenAlex API', 'Open Access status', 'OA best pdf url', 
    'Cited by count', 'Citation normalized percentile', 'Concepts', 'ISSN', 
    'Authors', 'APA 7 reference', 'Volume', 'Issue', 'Pages', 'Abstract'
]

#### detects if json is from OpenAlex ####
def is_openalex_record(r):
    # Campos típicos OpenAlex “muy estrictos”
    required_openalex_fields = [
        'id', 'display_name', 'type', 'open_access',
        'relevance_score', 'primary_location', 'type_crossref',
        'institution_assertions', 'cited_by_percentile_year'
    ]
    return all(k in r for k in required_openalex_fields)

# ----------- FILE LOADING -----------
def load_files_from_raw_folder(folder):
    valid_files = []
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS:
                valid_files.append(full_path)
            else:
                print(f"invalid_extension: {ext} in file {file}")
    return valid_files

# ----------- OPENALEX PARSING -----------
def fetch_openalex_data(data, filename, openalex_stack=None):
    total_loaded = 0
    if openalex_stack is None:
        openalex_stack = []

    try:
        parsed = parse_openalex_json_file(data)
        openalex_stack.extend(parsed)
        total_loaded += len(parsed)
    except Exception as e:
        print(s.error + f"❌ Failed to process {filename}: {e}")
    
    print(s.success + f"📦 Total OpenAlex records parsed from {filename}: {total_loaded}")
    
    return openalex_stack


# ----------- DATABASE DETECTION -----------
def detect_origin(file_path, openalex_stack):
    ext = os.path.splitext(file_path)[1].lower()
    origin = "Unknown"
    records = []

    if ext == '.csv':
        df = pd.read_csv(file_path, dtype=str)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path, dtype=str)
    elif ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'results' in data:
            records = data['results']
        elif isinstance(data, list):
            records = data
        else:
            records = []

        if records and all(is_openalex_record(r) for r in records):
            origin = 'OpenAlex (native)'
            fetch_openalex_data(data, file_path, openalex_stack)
            return records, origin, True  # ⛔ Ya están en openalex_stack

        # Aun si no es OpenAlex, puede tener otros campos...
        origin = 'Unknown'
        return records, origin, False

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Análisis de columnas para CSV y Excel
    print(s.info + f"📄 Columns in {file_path}: {list(df.columns)}")  # DEBUGGING
    if {'NIHMS ID', 'PMID', 'PMCID'}.issubset(df.columns):
        origin = 'PubMed'
    elif 'Source' in df.columns and df['Source'].astype(str).str.contains('scopus', case=False, na=False).any():
        origin = 'Scopus'
    elif 'longDBName' in df.columns:
        origin = "EBSCO"
    elif 'UT (Unique ID)' in df.columns:
        origin = 'WOS'
    elif {'DocumentType', 'DocumentTitle', 'PublicationName'}.issubset(df.columns):
        origin = 'PysNet'
    elif {'CENTRAL ID', 'CINAHL ID', 'ICTRP ID'}.issubset(df.columns):
        origin = 'Cochrane'

    records = df.fillna('').to_dict(orient='records')
    return records, origin, False


# Gets the open_access status depending on origin database #
# Its called within de fallback first fetch #

def get_open_access(entry, origin):
    if origin == 'PubMed':
        pmcid = entry.get('PMCID') or entry.get('PMC')
        if isinstance(pmcid, str) and pmcid.strip():
            return ('Open Access via PMCID', True)
        return (pmcid, False)
    elif origin == 'Scopus':
        oa = str(entry.get('Open Access', '')).lower()
        if 'open' in oa:
            return (oa, True)
        return ('Paywall', False)
    elif origin == 'WOS':
        if 'MOA' in entry and all(entry.get('MOA', '') == ''):
            return ('Manual Open Access', True)
        elif 'MOA' in entry:
                return ('User reported true', True)
        else: return ('Paywall', False)
    elif origin == 'EBSCO':
        oa = str(entry.get('isOpenAccess', '')).lower().strip()
        if oa in {'true', 'yes', 'open', 'diamond', 'gold', 'green'}:
            return ('EBSCO Open Access', True)
        return ('Paywall', False)
    elif origin == 'Cochrane':
        doi = str(entry.get('DOI', '')).strip()
        if not doi:
            pub_type = str(entry.get('Publication Type', '')).strip()
            return (f"It's a ({pub_type})", True)
        return ('Assumed Gold)', True)
    return ('Unknown', False)


### parse_openalex_json_files ###
def normalize_doi(doi_raw):
    """
    Devuelve un DOI en minúsculas, sin prefijos como 'https://doi.org/' o 'doi:'.
    """
    if not isinstance(doi_raw, str):
        return ''
    doi = doi_raw.strip().lower()
    for prefix in ['https://doi.org/', 'http://doi.org/', 'doi:']:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi

from common import get_oa
from apa7 import generate_apa_reference_7

def parse_openalex_json_file(json_data):
    """Parses a local OpenAlex JSON structure into normalized entries compatible with STANDARD_FIELDS."""
    parsed_entries = []

    for item in json_data.get("results", []):
        doi = normalize_doi(item.get('doi', ''))

        authorships = item.get('authorships', [])
        authors_list = [auth.get('author', {}).get('display_name', '') for auth in authorships if isinstance(auth, dict)]
        first_author = authors_list[0] if authors_list else ''
        authors_str = ", ".join(filter(None, authors_list))
        # Extraer volumen, issue y páginas si están (OpenAlex puede tener 'volume', 'issue', y 'biblio' para páginas)
       
        value = item.get('citation_normalized_percentile')
        volume = item.get('biblio', {}).get('volume', '') or item.get('volume', '')
        issue = item.get('biblio', {}).get('issue', '') or item.get('issue', '')
        pages = item.get('biblio', {}).get('pages', '') or item.get('pages', '')
        oa_info = item.get('open_access', {}) or {}
        oa_status = oa_info.get('oa_status', 'Unknown').lower()
        citation_percentile = item.get('citation_normalized_percentile')
        value = item.get('citation_normalized_percentile')
        if isinstance(value, dict):
            citation_percentile = value.get('value', '')
        else:
            citation_percentile = value if value is not None else ''
        is_oa, oa_url = get_oa(item)
        entry = {
            'Doitective': '',
            'DOI': doi,
            'Open Access?': str(is_oa).lower(),
            'Title': item.get('title', ''),
            'Year': item.get('publication_year', ''),
            'First author': first_author,
            'Origin database': 'OpenAlex (native)',
            'Indexed in': ", ".join(item.get('indexed_in', [])),
            #'Copies': '',
            'OpenAlex API': f"https://api.openalex.org/works/doi:{doi}",      
            'Open Access status': str(oa_status).lower(),
            'OA best pdf url': oa_url,
            'Cited by count': item.get('cited_by_count', ''),
            'Citation normalized percentile': citation_percentile,
            'Concepts': ", ".join([c.get('display_name', '') for c in item.get('concepts', [])]),
            'ISSN': item.get('host_venue', {}).get('issn_l', ''),
            'Authors': authors_str,
            'APA 7 reference': '',  # puedes rellenarlo luego con generate_apa_reference_7()
            'Volume': volume,
            'Issue': issue,
            'Pages': pages,
            #'Abstract': '',       # OpenAlex no siempre provee abstract

        }
        entry['APA reference'] = generate_apa_reference_7(entry)
        parsed_entries.append(entry)

    return parsed_entries

# Asegurar formato DOI estándar y eliminar duplicados
def last_security_check (unique_final):
    seen_dois = set()
    cleaned_final = []
    for entry in unique_final:
        raw_doi = entry.get("DOI", "").replace("https://doi.org/", "").strip().lower()
        full_doi = f"https://doi.org/{raw_doi}"
        if raw_doi and raw_doi not in seen_dois:
            entry["DOI"] = full_doi
            cleaned_final.append(entry)
            seen_dois.add(raw_doi)

    unique_final = cleaned_final
    diccionario = {k: v for d in unique_final for k, v in d.items()}
    return diccionario

