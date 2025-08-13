# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# screening.py

import pandas as pd
import json
from modules.processors.helpers import get_open_access, is_article_record, get_best_identifier, classify_records
import utils.style.styles as s
from collections import Counter

language = 'en'  # Default language
EXTENSIONS = ['.csv', '.xls', '.xlsx', '.json']



# Load localization strings
with open('utils/localization/base_loc.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)

# Define standard output fields
def deduplicate_by_uiad(records):
    seen = set()
    unique = []
    duplicates = []

    for r in records:
        uid = r.get('UID')
        if not uid or uid in seen:
            duplicates.append(r)
        else:
            seen.add(uid)
            unique.append(r)

    return unique, duplicates

# ----------- NORMALIZATION -----------
# AQUÍ NORMALIZAMOS EL DOI (sin https) Y GENERAMOS CAMPOS BASE DE FALLBACK FETCHANDO INFORMACIÓN
# DE LOS FILES ORIGINALES
def normalize_entry(entry, origin, file):
    doi_raw = next((str(value).strip().upper() for key, value in entry.items() if key.lower() == 'doi'), '')
    doi_url = f"https://doi.org/{doi_raw}" if doi_raw and not doi_raw.startswith('http') else doi_raw

    title = (
        str(entry.get('Title', '')).strip()
        or str(entry.get('Article Title', '')).strip()
        or str(entry.get('DocumentTitle', '')).strip()
        or str(entry.get('title', '')).strip()
    )

    year = (
        str(entry.get('Year', '')).strip()
        or str(entry.get('Publication Year', '')).strip()
        or str(entry.get('PublicationYear', '')).strip()
    )

    f_a = (
        str(entry.get('First Author', '')).strip()
        or str(entry.get('first author', '')).strip()
        or str(entry.get('Author', '')).strip()
        or str(entry.get('author', '')).strip()
        or str(entry.get('Author(s)', '')).strip()
    )

    issn = (
        str(entry.get('ISSN', '')).strip()
        or str(entry.get('issn', '')).strip()
        or str(entry.get('issns', '')).strip()
    )

    pmid = (
        str(entry.get('PubMed ID', '')).strip()
        or str(entry.get('Pubmed Id', '')).strip()
    )

    authors = (
        str(entry.get('Authors', '')).strip()
        or str(entry.get('Author(s)', '')).strip()
    )

    abstract = (
        str(entry.get('Abstract', '')).strip()
        or str(entry.get('abstract', '')).strip()
    )

    # Solo actualizar campos si están vacíos o no existen
    entry.setdefault('Doitective', 0)
    entry.setdefault('DOI', doi_raw)
    entry.setdefault('OpenAlex API', f"https://api.openalex.org/works/doi:{doi_raw}" if doi_raw else '')
    entry.setdefault('OA best pdf url', doi_url)
    entry.setdefault('Cited by count', 'Unknown')
    entry.setdefault('Citation normalized percentile', 'Unknown')
    entry.setdefault('ISSN', issn)
    entry.setdefault('PMID', pmid)
    entry.setdefault('Authors', authors)
    entry.setdefault('Abstract', abstract)
    entry.setdefault('APA 7 reference', '')
    entry.setdefault('Volume', '')
    entry.setdefault('Issue', '')
    entry.setdefault('Pages', '')
    entry.setdefault('Title', title)
    entry.setdefault('Year', year)
    entry.setdefault('First author', f_a)
    entry.setdefault('Indexed in', origin)
    entry.setdefault('Copies', '')
    entry.setdefault('Origin database', origin)
    entry.setdefault('Open Access?', False)
    entry.setdefault('Open Access status', '')
    entry.setdefault('Original OA', '')
    entry.setdefault('Publication type', '')
    entry.setdefault('norti', '')

    return entry

# ----------- DEDUPLICATION -----------

from collections import Counter, defaultdict

def deduplicate_by_best_identifier(entries):
    grouped = defaultdict(list)
    no_id_entries = []

    for entry in entries:
        best_id = entry.get('UID', '').strip().lower()

        if best_id in {'UID'}:
            grouped[best_id].append(entry)
        else:
            no_id_entries.append(entry)

    unique, duplicates = [], []
    duplication_stats = Counter()

    for group in grouped.values():
        Ndups = len(group)
        duplication_stats[Ndups] += 1

        origins = [e.get('Origin database', 'Unknown') for e in group]
        dup_in_db = ', '.join(sorted(set(origins)))

        for e in group:
            e['Copies'] = f"{Ndups}: {dup_in_db}"

        # Priorizamos OpenAlex si está disponible
        selected = next((e for e in group if e.get('Origin database', '').lower() == 'openalex (native)'), None)
        if not selected:
            selected = next((e for e in group if e.get('Open Access?', '') == 'true'), None)
        if not selected:
            selected = group[0]

        unique.append(selected)
        duplicates.extend(e for e in group if e is not selected)

    unique.extend(no_id_entries)

    print("\n📊 Duplicates Summary (by best identifier):")
    for k in sorted(duplication_stats):
        count = duplication_stats[k]
        label = {
            1: 'Unique',
            2: 'Duplicated',
            3: 'Triplicates',
            4: 'Cuadrupled',
            5: 'Quintuples'
        }.get(k, f'{k}-uplicates')
        print(f"   • {label}: {count} grupo(s)")

    return unique, duplicates




def deduplicate_by_oaid (entries):
    grouped = {}
    no_uid_entries = []  # para guardar entradas sin PMID válido
    unique, duplicates = [], []
    for entry in entries:
        oaid = entry.get('OAID')
        if oaid and isinstance(oaid, str) and oaid.strip() != '':
            grouped.setdefault(oaid.strip(), []).append(entry)
        else:
            no_uid_entries.append(entry)
    unique, duplicates = deduplicate_group ('OAID', grouped, unique, duplicates, no_uid_entries)
    grouped = {}
    return 

from collections import Counter

def deduplicate_group(id, grouped, unique, duplicates):
    duplication_stats = Counter()
    
    for group in grouped.values():
        N = len(group)
        duplication_stats[N] += 1
        
        if N == 1:
            entry = group[0]
            origin = entry.get('Origin database', 'Unknown')
            entry['Copies'] = f"1: {origin}"
            unique.append(entry)
        else:
            # Combinar origenes
            origins = [e.get('Origin database', 'Unknown') for e in group]
            origin_set = set(o.strip().lower() for o in origins)
            dup_in_db = ', '.join(sorted(set(origins)))

            for e in group:
                e['Copies'] = f"{N}: {dup_in_db}"

            selected = group[0]

            # Mezclar 'Indexed in'
            indexed_raw = selected.get('Indexed in', '')
            previous = [v.strip().lower() for v in indexed_raw.split(',') if v.strip()]
            full_set = sorted(set(previous).union(origin_set))
            capitalized = [o.norti() for o in full_set]
            selected['Indexed in'] = ', '.join(capitalized)

            unique.append(selected)
            duplicates.extend(e for e in group if e is not selected)

    print(f"\n📊 {id} duplication Summary:")
    for k in sorted(duplication_stats):
        if k == 0:
            continue
        label = {
            1: 'Unique',
            2: 'Duplicated',
            3: 'Triplicates',
            4: 'Cuadrupled',
            5: 'Quintuples'
        }.get(k, f'{k}-uplicados')
        print(f"   • {label}: {duplication_stats[k]} grupo(s)")

    return unique, duplicates


def deduplicate_by_uid(entries):
    remaining = entries[:]
    all_unique = []
    all_duplicates = []

    # Paso 1: deduplicar por DOI
    grouped = {}
    next_remaining = []
    for e in remaining:
        doi = e.get('DOI')
        if doi and isinstance(doi, str) and doi.strip():
            grouped.setdefault(doi.strip(), []).append(e)
        else:
            next_remaining.append(e)
    unique, duplicates = deduplicate_group('DOI', grouped, [], [])
    all_unique.extend(unique)
    all_duplicates.extend(duplicates)
    remaining = next_remaining

    # Paso 2: deduplicar por PMID
    grouped = {}
    next_remaining = []
    for e in remaining:
        pmid = e.get('PMID')
        if pmid and isinstance(pmid, str) and pmid.strip():
            grouped.setdefault(pmid.strip(), []).append(e)
        else:
            next_remaining.append(e)
    unique, duplicates = deduplicate_group('PMID', grouped, [], [])
    all_unique.extend(unique)
    all_duplicates.extend(duplicates)
    remaining = next_remaining

    # Paso 3: deduplicar por Title
    grouped = {}
    next_remaining = []
    for e in remaining:
        norti = e.get('norti')
        if norti and isinstance(norti, str) and norti.strip():
            grouped.setdefault(norti.strip(), []).append(e)
        else:
            next_remaining.append(e)
    unique, duplicates = deduplicate_group('norti', grouped, [], [])
    all_unique.extend(unique)
    all_duplicates.extend(duplicates)
    remaining = next_remaining  # Estos no tienen ningún UID útil

    return all_unique, all_duplicates, remaining


# --- SPLIT OPENALEX UNIQUE FROM OTHER UNIQUE ----#
def split_for_enrichment(entries):
    from_openalex = []
    to_enrich = []
    for entry in entries:
        origin = entry.get('Origin database', '').lower()
        if origin == 'openalex (native)':
            from_openalex.append(entry)
        else:
            to_enrich.append(entry)

    return from_openalex, to_enrich

from collections import defaultdict, Counter
# ----------- OA SEPARATION -----------
def separate_by_open_access(entries):
    oa_entries = []
    pw_entries = []
    unk_entries = []
    status_by_origin = defaultdict(Counter)

    for entry in entries:
        # Extraer los campos, forzando a str y minúsculas, usar valores por defecto claros
        is_oa_raw = entry.get('Open Access?', '')
        oa_status_raw = entry.get('Open Access status', '')
        origin = entry.get('Origin database', 'Unknown')

        is_oa = str(is_oa_raw).strip().lower()
        oa_status = str(oa_status_raw).strip().lower()

        # Para conteo de estados (útil para depuración)
        status_by_origin[origin][oa_status or '[blank]'] += 1

        # Heurística flexible para detectar OA:
        # 1) Si 'Open Access?' es 'true', asumimos OA (salvo estado bloqueado)
        # 2) Si estado está vacío o desconocido, pero Open Access? es True, asumimos OA
        # 3) Si 'Open Access?' no está definido o no es 'true', intentar deducir por estado:
        #    - 'gold', 'diamond', 'green' son OA típicos
        #    - 'hybrid', 'bronze', 'blocked' se consideran paywall o no OA
        # 4) Si no hay info clara, clasificar como paywall para no perder registros en OA.

        oa_status_closed= {'closed'}
        oa_status_open = {'diamond', 'gold', 'hybrid', 'bronze', 'green', 'Open access via pmcid'}

        if is_oa == 'true':
            if oa_status in oa_status_closed:
                pw_entries.append(entry)
            else:
                oa_entries.append(entry)
        elif is_oa == 'false':
            if oa_status in oa_status_open:
                oa_entries.append(entry)
            else:
                pw_entries.append(entry)
        else: 
            unk_entries.append(entry)

    # Impresión de resumen para depuración
    print("\n🔑 Open Access Status 🔎 Breakdown by Source")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    emoji_map = {
        'diamond': '💎',
        'gold': '💛',
        'green': '💚',
        'hybrid': '💙',
        'Open access via pmcid': '💠',
        'bronze': '🤎',
        'closed': '🚫',
        '[]': '❓'
    }
    
    custom_order = ['diamond', 'gold', 'green', 'hybrid', 'Open access via pmcid', 'bronze', 'closed', '[]']
    priority_map = {k: i for i, k in enumerate(custom_order)}

    for origin, counter in status_by_origin.items():

        print(f"\n📚 {origin}: Unique records: {sum(counter.values())}")
        sorted_items = sorted(counter.items(), key=lambda x: priority_map.get(x[0], 999))

        for status, count in sorted_items:
            emoji = emoji_map.get(status, '📦')
            print(f"  {emoji} {status.capitalize():<8} → {count:>5} records")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return oa_entries, pw_entries, unk_entries
# Dump bronze and hybrid

oa_types_to_merge = {'Closed'}

def is_paywall(record):
    oa_info = record.get('Open Access?', {})
    if not oa_info.get('Open Access?', False):
        return True  # No OA → paywall
    if oa_info.get('Open Access status', '').lower() in oa_types_to_merge:
        return True  # Bronze o Hybrid → paywall
    return False





from collections import defaultdict, Counter

def deduplicate_by_ids(entries):
    from collections import defaultdict, Counter

    id_to_group = {}
    groups = defaultdict(list)
    group_index = 0
    remain = []  # 👈 para registros sin identificadores

    for entry in entries:
        doi = entry.get('DOI', '').strip().lower()
        pmid = entry.get('PMID', '').strip().lower()
        norti = entry.get('norti', '').strip().lower()
        keys = [k for k in (doi, pmid, norti) if k]
        
        if not keys:
            remain.append(entry)
            continue  # 👈 saltamos este registro, no tiene con qué agrupar

        matched_group = None
        for key in keys:
            if key in id_to_group:
                matched_group = id_to_group[key]
                break

        if matched_group is None:
            matched_group = group_index
            group_index += 1

        groups[matched_group].append(entry)

        for key in keys:
            id_to_group[key] = matched_group

    # Ahora procesamos los grupos 
    unique, duplicates = [], [] 
    duplication_stats = Counter()

    for group in groups.values(): # 👈
        N = len(group)
        duplication_stats[N] += 1

        if N == 1:
            entry = group[0]
            origin = entry.get('Origin database', 'Unknown')
            entry['Copies'] = f"1: {origin}"
            unique.append(entry) # 👈 Si es 1 se queda en Unique
        else:
            origins = [e.get('Origin database', 'Unknown') for e in group]
            origin_set = {o.strip().lower() for o in origins}
            dup_in_db = ', '.join(sorted(set(origins)))
            for e in group:
                e['Copies'] = f"{N}: {dup_in_db}" # 👈 Se actualiza el campo copies en todas las entradas que hacen match

            selected = group[0]

            # Combinar 'Indexed in'
            indexed_raw = selected.get('Indexed in', '')
            existing_set = {v.strip().lower() for v in indexed_raw.split(',') if v.strip()}
            full_set = existing_set.union(origin_set)
            selected['Indexed in'] = ', '.join(sorted({v.title() for v in full_set})) # 👈 Se actualiza 'indexed in'

            unique.append(selected) # 👈 La entrada más rica va a unique
            duplicates.extend(e for e in group if e is not selected) # 👈 Duplicados aquí

    print(f"\n📊 Global Deduplication Summary:")
    for k in sorted(duplication_stats):
        label = {
            1: 'Unique',
            2: 'Duplicated',
            3: 'Triplicates',
            4: 'Cuadrupled',
            5: 'Quintuples',
            6: 'Six or more'
        }.get(k, f'{k}-uplicados')
        print(f"   • {label}: {duplication_stats[k]} groups") # 👈 Se imprimen en consola y en logs todas las estadísticas

    if remain:
        print(f"⚠️  {len(remain)} records could not be grouped due to missing DOI, PMID and Title.") # 👈 Manejo de errores si no se encuentra DOI, PMID y título

    return unique, duplicates, remain # 👈 Devuelve grupos unique, duplicates y 'remain' (manejo de errores)
