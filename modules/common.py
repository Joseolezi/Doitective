# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# common.py

def default_entry_data(doi, user_base_origin):
    return {
        'Doitective': 0,
        'DOI': doi,
        'Title': 'Unknown',
        'Year': 'Unknown',
        'First author': 'Unknown',
        'Base_origin': user_base_origin, 
        'Indexed in': 'Unknown',
        'Copies': '1',
        'OpenAlex API': 'Not Found by Doitective',
        'is_oa': 'Unknown',
        'Open Access': 'Unknown',
        'OA best pdf url': 'Unknown',
        'cited by count': 'Unknown',
        'citation normalized percentile (value)': 'Unknown',
        'Concepts': 'Unknown',
        'ISSN': 'Unknown',
        'Authors': 'Unknown',
        'APA reference': 'Unknown', 
        'Volume': 'Unknown',
        'Issue': 'Unknown',
        'Pages': 'Unknown',
    }


def get_oa(item):
    best_location = item.get('best_oa_location', {}) or {}
    oa_info = item.get('open_access', {}) or {}
    primary = item.get('primary_location', {}) or {}

    is_oa = oa_info.get('is_oa')
    best_is_oa = best_location.get('is_oa')
    # Prioridad de URL
    pdf_url = best_location.get('pdf_url')
    pdf_landing = primary.get('landing_page_url')
    
    oa_url = oa_info.get('oa_url')
    doi_url = f"https://doi.org/{item.get('doi')}" if item.get('doi') else None
    landing_url = oa_info.get('landing_page_url')

    # Determinar mejor URL disponible
    best_url = pdf_url or pdf_landing or oa_url or doi_url or landing_url or None
    best_oa = best_is_oa or is_oa or False
    return best_oa, best_url


