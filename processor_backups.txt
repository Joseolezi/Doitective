import os
import csv
import pandas as pd
import json
import re
import httpx
import asyncio
import time
from open_alex_enrich import enrich_with_openalex
language = 'en'  # Default language
EXTENSIONS = ['.csv', '.xls', '.xlsx']

# Load localization strings
with open('localization.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)

# Define standard output fields
STANDARD_FIELDS = [
    'DOI','Title', 'Year', 'First author', 'Found in', 
    'OpenAlex API', 'Indexed in',  'is_oa', 'oa_status', 
    'oa_url', 'pdf url', 'cited by count', 
    'citation normalized percentile (value)', 'Concepts', 
    'ISSN', 'Authors', 'APA reference', 'Abstract'
]

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

# ----------- DATABASE DETECTION -----------
def detect_origin(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path, dtype=str)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path, dtype=str)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Detect origin basado en columnas o nombre archivo
    if 'PMCID' and 'PMID' and 'NIHMS ID' in df.columns:
        origin = 'PubMed'
    elif 'Source' in df.columns and 'Scopus' in df.values:
        origin = 'Scopus'
    elif 'longDBName' and 'shortDBName' in df.columns:
        origin = "EBSCO"
    elif 'UT (Unique ID)' in df.columns:
        origin = 'WOS'
    else:
        origin = 'Unknown'

    # Convertir DataFrame a lista de dicts para normalizar
    records = df.fillna('').to_dict(orient='records')
    return origin, records

# ----------- NORMALIZATION -----------
def normalize_entry(entry, origin, filename):
    def fallback(*fields):
        for f in fields:
            if f in entry and pd.notnull(entry[f]):
                return str(entry[f]).strip()
        return ''

    doi = fallback('DOI')
    title = fallback('Title', 'Article Title')
    abstract = fallback('Abstract')
    authors = fallback('Authors', 'Author(s)')
    year = fallback('Year', 'Publication Year')
    cited = fallback('Cited by', 'Cited By')
    issn = fallback('ISSN')

    oa_status, is_oa = get_open_access(entry, origin)

    # Normalizar DOI como URL clicable
    doi = entry.get('DOI', '').strip()
    if doi and not doi.startswith('http'):
        doi = f"https://doi.org/{doi}"
    else:
        entry['DOI'] = ''
    return {
        'DOI': doi,
        'Title': title,
        'First author': authors,        
        'Year': year,
        'Cited By': cited,
        'Base_Origin': origin,
        'Open Access': oa_status,
        'is_oa': str(is_oa).lower(),
        'ISSN': issn,
        'Authors': authors,
        'OpenAlex API': f"https://api.openalex.org/works/{doi}" if doi else '',
        'Abstract': abstract   
        }

def get_open_access(entry, origin):
    if origin == 'PubMed':
        pmcid = entry.get('PMCID') or entry.get('PMC')
        if isinstance(pmcid, str) and pmcid.strip():
            return ('Open Access via PMCID', True)
        return ('Paywall', False)
    elif origin == 'Scopus':
        oa = str(entry.get('Open Access', '')).lower()
        if 'open' in oa:
            return (entry.get('Open Access', ''), True)
        return ('Paywall', False)
    elif origin == 'WOS':
        moa = str(entry.get('MOA', '')).lower()
        if 'yes' in moa:
            return ('Manual Open Access', True)
        return ('Paywall', False)
    return ('Unknown', False)


# ----------- DEDUPLICATION -----------
def deduplicate_by_doi(entries):
    grouped = {}
    for entry in entries:
        doi = entry.get('DOI') or f"no-doi-{entry.get('ISSN', '')}-{len(grouped)}"
        grouped.setdefault(doi, []).append(entry)

    unique, duplicates = [], []

    for group in grouped.values():
        if len(group) == 1:
            unique.append(group[0])
            continue

        selected = next((e for e in group if e['is_oa'] == 'true'), None)
        if not selected:
            selected = next((e for e in group if e.get('Base_Origin', '').lower() == 'pubmed'), None)
        if not selected:
            selected = group[0]

        unique.append(selected)
        duplicates.extend(e for e in group if e is not selected)

    return unique, duplicates

# ----------- OA SEPARATION -----------
def separate_by_open_access(entries):
    oa_entries = []
    pw_entries = []

    for entry in entries:
        is_oa = str(entry.get('is_oa', '')).lower()
        if is_oa == 'true':
            oa_entries.append(entry)
        else:
            pw_entries.append(entry)
    return oa_entries, pw_entries