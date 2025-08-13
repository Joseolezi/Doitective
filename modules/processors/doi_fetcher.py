# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# doi_fetcher.py












#### THIS MODULE IS CURRENTLY NOT BEING USED, BUT WILLING TO INTEGRATE SOON ####





























import os
import json
import csv
import re
import pandas as pd

def extract_dois_from_text(text):
    doi_regex = re.compile(r"\b10\.\d{4,9}/[^\s\"\'<>]+", re.IGNORECASE)
    return set(match.group(0).lower().strip().replace("https://doi.org/", "") for match in doi_regex.finditer(text))

def extract_dois_from_file(file_path):
    dois = set()
    _, ext = os.path.splitext(file_path.lower())

    try:
        if ext in ['.csv', '.tsv']:
            with open(file_path, newline='', encoding='utf-8') as f:
                dialect = csv.Sniffer().sniff(f.read(2048))
                f.seek(0)
                reader = csv.DictReader(f, dialect=dialect)
                for row in reader:
                    for val in row.values():
                        if isinstance(val, str):
                            dois.update(extract_dois_from_text(val))

        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path, dtype=str)
            for col in df.columns:
                for val in df[col].dropna().astype(str):
                    dois.update(extract_dois_from_text(val))

        elif ext in ['.json']:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
                json_str = json.dumps(data)
                dois.update(extract_dois_from_text(json_str))

        else:
            # Para todos los demás formatos: .bib, .ris, .txt, .py, etc
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                dois.update(extract_dois_from_text(content))

    except Exception as e:
        print(f"[!] Error leyendo {file_path}: {e}")

    return dois


def extract_dois_from_folder(folder_path):
    all_dois = set()
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_dois = extract_dois_from_file(file_path)
            all_dois.update(file_dois)
    return list(sorted(all_dois))


# Ejemplo de uso:
folder = "drop_your_files_here"
dois = extract_dois_from_folder(folder)
print(f"DOIs encontrados en carpeta {folder}: {len(dois)}")
for d in dois:
    print(d)
