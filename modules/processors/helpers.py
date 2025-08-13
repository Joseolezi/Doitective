# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# helpers_py
import os
import pandas as pd
import json
import utils.style.styles as s
from modules import memory as m
import re
language = 'en'  # Default language
import unicodedata

with open('utils/localization/base_loc.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)

EXTENSIONS = ['.csv', '.xls', '.xlsx', '.json']
STANDARD_FIELDS = m.get('standard_fields')
#### detects if json is from OpenAlex ####

### normalize title ####

import unicodedata

def normalize_title(title) -> str:
    if not isinstance(title, str) or pd.isna(title) or not title.strip():
        return ''

    # 1. Pasar a minúsculas
    title = title.lower()

    # 2. Normalizar acentos y caracteres Unicode
    title = unicodedata.normalize('NFKD', title)
    title = ''.join(c for c in title if not unicodedata.combining(c))

    # 3. Eliminar puntuación y símbolos (conservando letras y números Unicode)
    title = re.sub(r"[^\w\s]", "", title, flags=re.UNICODE)

    # 4. Eliminar espacios redundantes
    title = re.sub(r"\s+", " ", title).strip()

    return title




### parse_openalex_json_files ###
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
def detect_origin(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    origin = "Unknown"
    records = []
    print(s.dim_white + f"🔎 Parsing ({file_path}")
    if ext == '.csv':
        df = pd.read_csv(file_path, dtype=str)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path, dtype=str)    
    else:
        raise ValueError(f"Unsupported file type: {ext}")        
    n_pubs = m.get('npubs') + len(df)
    m.set('npubs', n_pubs)
    # Análisis de columnas para CSV y Excel
    if {'NIHMS ID', 'PMID', 'PMCID'}.issubset(df.columns):
        origin = 'PubMed'
    elif {'DocumentTitle', 'DocumentType', 'PublisherCity'}.issubset(df.columns):
        origin = 'PsyNet'
    elif 'Source' in df.columns and df['Source'].astype(str).str.contains('scopus', case=False, na=False).any():
        origin = 'Scopus'
    elif 'longDBName' in df.columns:
        origin = "EBSCO"
    elif 'UT (Unique ID)' in df.columns:
        origin = 'WOS'
    elif {'CENTRAL ID', 'CINAHL ID', 'ICTRP ID'}.issubset(df.columns):
        origin = 'Cochrane'

    database_sources = m.get("database_sources")
    if origin not in database_sources:
        database_sources.append(origin)
        m.set("database_sources", database_sources)

    records = df.fillna('').to_dict(orient='records')
    for entry in records: 
        entry['Origin database'] = origin

    def detect_field(possibles):
        for col in possibles:
            if col in df.columns:
                return col
        return None
    meta = {
        'title': detect_field(['Title', 'DocumentTitle', 'Article Title', 'title']),
        'year': detect_field(['Year', 'Publication Year']),
        'authors': detect_field(['Authors', 'Author(s)']),
        'abstract': detect_field(['Abstract', 'Resumen']),
        }
    if origin is not 'Unknown':
        print(s.error + f"📌 Detected origin: {origin}")
    else: 
        print(s.error + f" ❌ Doitective can't detect {file_path} origin database. Invalid files can cause malfunction")
    print(s.dim_white + f"📄 Parsing ({file_path}: {n_pubs} records from {origin}")  # DEBUGGING
    print(s.info + f"📚 Raw data stacked: " + s.success + f"{n_pubs}") 
    return records, origin, meta
        
# Gets the open_access status depending on origin database #
# Its called within de fallback first fetch #
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


def get_field_case_insensitive(entry, possible_keys):
    for key in possible_keys:
        for entry_key in entry.keys():
            if entry_key.lower() == key.lower():
                return entry[entry_key]
    return ''

def is_article_record(entry, origin='Unknown'):
    NON_ARTICLE_TERMS = [
        'short survey', 'book chapter', 'book', 'conference',
        'meeting abstract', 'case reports', 'case report',
        'dissertation/thesis', 'awarded grant', 'proceedings paper'
    ]

    def get_field_case_insensitive(entry, possible_keys):
        entry_keys_lower = {k.lower(): k for k in entry.keys()}
        for key in possible_keys:
            lower_key = key.lower()
            if lower_key in entry_keys_lower:
                return entry[entry_keys_lower[lower_key]]
        return ''

    # Detectar campo relevante por origen
    if origin == 'PubMed':
        field = get_field_case_insensitive(entry, ['PublicationType', 'Publication Type'])
    elif origin == 'Scopus':
        field = get_field_case_insensitive(entry, ['Document Type'])
    elif origin == 'EBSCO':
        field = get_field_case_insensitive(entry, ['docTypes'])
    elif origin == 'WOS':
        field = get_field_case_insensitive(entry, ['Document Type'])
    elif origin == 'Cochrane':
        field = get_field_case_insensitive(entry, ['Publication Type'])
    elif origin == 'PsyNet':
        field = get_field_case_insensitive(entry, ['DocumentType'])
    else:
        field = get_field_case_insensitive(entry, ['Document Type', 'docTypes', 'Publication Type'])

    field_str = str(field).strip().lower()

    # Si coincide con alguno de los términos excluyentes → no es artículo
    if any(term in field_str for term in NON_ARTICLE_TERMS) and 'article' not in field_str:
        return (field_str, False)

    # Por defecto → es artículo
    return (field_str or 'unknown', True)


def get_best_identifier(entry):
    doi_raw = get_field_case_insensitive(entry, ['DOI'])
    doi = normalize_doi(doi_raw) if doi_raw else ''
    if doi:
        return 'doi', doi
    pmid = get_field_case_insensitive(entry, ['PMID', 'Pubmed Id', 'PubMed ID'])
    if pmid and str(pmid).strip():
        return 'pmid', str(pmid).strip()
    title = get_field_case_insensitive(entry, ['Title', 'DocumentTitle', 'TI'])
    if title and str(title).strip():
        return 'title', str(title).strip()
    return 'missing', ''
############################################ testing
def clean_pmid(pmid_raw):
    if not pmid_raw:
        return ''
    pmid_str = str(pmid_raw).strip()
    # Quita cualquier carácter que no sea dígito
    pmid_clean = ''.join(c for c in pmid_str if c.isdigit())
    return pmid_clean

def get_all_identifiers(entry):
    doi_raw = get_field_case_insensitive(entry, ['DOI'])
    doi = normalize_doi(doi_raw)

    pmid_raw = get_field_case_insensitive(entry, ['PMID', 'Pubmed Id', 'PubMed ID'])
    pmid = clean_pmid(pmid_raw)

    title = get_field_case_insensitive(entry, ['Title', 'DocumentTitle', 'TI'])
    norti = normalize_title(title) if title else ''
    
    batch_tag = 'doi' if doi else 'pmid' if pmid else 'norti' if norti else 'missing'
    
    return batch_tag, doi, pmid
##################################################



def get_open_access(entry, origin):

    pub_type, is_art = is_article_record(entry, origin)

    if origin == 'PubMed':
        pmcid = entry.get('PMCID')
        is_oa = bool(pmcid and str(pmcid).strip())
        return ('Open Access via PMCID', is_oa, pub_type, is_art)

    elif origin == 'Scopus':
        oa = str(entry.get('Open Access', '')).lower()
        is_oa = 'open' in oa
        return (oa if is_oa else 'Closed', is_oa, pub_type, is_art)

    elif origin == 'WOS':
        if 'MOA' in entry:
            moa = entry['MOA']
            if moa == '':
                return ('Unknown', False, pub_type, is_art)
            else:
                return ('User reported true', True, pub_type, is_art)
        else:
            return ('Closed', False, pub_type, is_art)

    elif origin == 'EBSCO':
        oa = str(entry.get('isOpenAccess', '')).lower().strip()
        is_oa = oa in {'true', 'yes', 'open', 'diamond', 'gold', 'green'}
        return ('EBSCO Open Access' if is_oa else 'Unknown', is_oa, pub_type, is_art)

    elif origin == 'Cochrane':
        if not entry.get('DOI'):
            pub_type = str(entry.get('Publication Type', '')).strip()
            return (f"It's a ({pub_type})", True, pub_type, is_art)
        return ('Assumed Gold', True, pub_type, is_art)

    elif origin == 'PsyNet':
        return ('Unknown', False, pub_type, is_art)

    return ('Unknown', False, pub_type, is_art)

def classify_records(records):

    dois_batch = []
    pmids_batch = []
    titles_batch = []
    error = []
    for entry in records:
        # Si ya viene de OpenAlex enriquecido
        # Revisar etiquetas ya predefinidas en la normalización
        id_kind = (entry.get('batch_tag') or '').lower()
        if id_kind == 'doi':
            dois_batch.append(entry)
        elif id_kind == 'pmid':
            pmids_batch.append(entry)
        elif id_kind == 'norti':
            titles_batch.append(entry)
        else:
            error.append(entry)

    return dois_batch, pmids_batch, titles_batch, error


from modules.common import get_oa
from modules.processors.utils import generate_apa_reference_7

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
        oaid = str(entry.get('ids',{}).get('openalex',''))
        value = item.get('citation_normalized_percentile')
        if isinstance(value, dict):
            citation_percentile = value.get('value', '')
        else:
            citation_percentile = value if value is not None else ''
        is_oa, oa_url = get_oa(item)
        entry = {
            'Doitective': 0,
            'DOI': doi,
            'Open Access?': str(is_oa).lower(),
            'Title': item.get('title', ''),
            'Year': item.get('publication_year', ''),
            'First author': first_author,
            #'Origin database': 'OpenAlex (native)',
            'Indexed in': ", ".join(item.get('indexed_in', [])),
            #'Copies': '',
            'OpenAlex API': f"https://api.openalex.org/works/doi:{doi}",      
            'Open Access status': str(oa_status).lower(),
            'OA best pdf url': oa_url,
            'Cited by count': item.get('cited_by_count', ''),
            'Citation normalized percentile': citation_percentile,
            'Concepts': ", ".join([c.get('display_name', '') for c in item.get('concepts', [])]),
            'OAID': oaid,
            'UID': item.get('primary_location', {}).get('source', '').get('issn',''),
            'PMID'
            'Authors': authors_str,
            'APA 7 reference': '',  # puedes rellenarlo luego con generate_apa_reference_7()
            'Volume': volume,
            'Issue': issue,
            'Pages': pages,
            #'Abstract': '',       # OpenAlex no siempre provee abstract

        }
        
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

