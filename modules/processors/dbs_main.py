# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# dbs_main.py
import os
import modules.memory as m
import utils.style.styles as s
import modules.texts as t
from modules.screening import normalize_entry
from modules.processors.helpers import (
    load_files_from_raw_folder,
    detect_origin, normalize_title,
    get_all_identifiers,
    get_open_access,
    normalize_doi,
    detect_origin)

def set_basic_attributes (f):
    not_arts = []
    initialized = []
    records, origin, meta = detect_origin(f)
    
    doi = ''
    for r in records: 
        batch_tag, doi, pmid = get_all_identifiers(r)
        doi = normalize_doi(doi) if doi else ''
        title = r.get(meta.get('title', ''),'')
        # norti = normalize_title (title) if title else ''
        uid = doi if doi else pmid if pmid else title if title else ''
        if uid == '':
            continue
        oa_status, is_oa, pub_type, is_ar = get_open_access(r, origin)
        
        r.update ({
            # FRONTEND
            'DOI': doi,
            'Origin database': origin,
            'filepath': f,
            'Indexed in': origin, 
            'Copies': '',
            'Open Access status': oa_status,
            'Doitective':  0, 
            'Title': title,
            'First author': '',
            'Open Access?': bool(is_oa),
            'Original OA': oa_status,
            'Year': r.get(meta.get('year', ''),''),
            'Publication type': pub_type,
            'OpenAlex API': f"https://api.openalex.org/works/doi:{doi}" if doi else '',
            'OA best pdf url': '',
            'Cited by count': '', 
            'Citation normalized percentile': '',
            'ISSN': '',
            'PMID': str(pmid).strip() if pmid else '',
            'Authors': r.get(meta.get('authors', ''),''),
            'Abstract': r.get(meta.get('abstract', ''),''),
            'APA 7 reference': '', 
            'Volume': '', 
            'Issue': '', 
            'Pages': '',              
            #BACK END
            'UID': uid,
            'batch_tag': batch_tag,
            'is_ar': is_ar,
            'norti': title          
        })
        if uid == '':
            continue
        if not is_ar:
            not_arts.append(r)
            continue
        r = normalize_entry(r, origin, f)   
        initialized.append(r)
    return initialized, not_arts

def parse_input_data():

    INPUT_PATH = m.get('input_path')
    valid_files = []
    initialized = []
    not_articles = []
    normalized = []
    # LOAD AL VALID FILES WITHIN INPUT FOLDER
    print(s.magenta + "Loading and validating files 📂 \n\n")
    valid_files = load_files_from_raw_folder(INPUT_PATH)
    if not valid_files:
        print(t['no_valid_files'])
        return
    
    for f in valid_files:
        normalized, not_arts = set_basic_attributes(f)
        initialized.extend(normalized)
        not_articles.extend(not_arts)
        
    return initialized, not_articles
    
        
                








