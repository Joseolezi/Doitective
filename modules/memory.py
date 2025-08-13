# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# memory.py

_global = {
    "mailto": None,
    "value": None,
    "other": None,
    "input_path": "[__RAW_DATA__]",
    "output_path": "[__SCREENED_DATA__]/", 
    "npubs": 0,
    "mode": '2',
    "classify_folder": "[_FINAL_SORT_]",
    "database_sources": [],
    "doit_version": "1.0.1",
    "standard_fields": 
    [
    'DOI', 
    'Origin database', 
    'Indexed in', 
    'Copies', 
    'Open Access status',
    'OA best pdf url',   
    'Doitective', 
    'Title', 
    'First author', 
    'Open Access?', 
    'Original OA',
    'Year',
    'Publication type',
    'OpenAlex API',     
    'Cited by count', 
    'Citation normalized percentile', 
    'ISSN',
    'PMID',
    'Authors',
    'Abstract',  
    'APA 7 reference', 
    'Volume', 
    'Issue', 
    'Pages'
]
}

def set(name, value):
    _global[str(name)] = value

def get(name):
    return _global.get(name)

def get_all():
    return dict(_global)  # devuelve una copia

def reset_all():
    """Resetea todas las claves a None, excepto standard_fields"""
    for key in _global:
        if key != "standard_fields":
            _global[key] = None





