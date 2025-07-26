# screening.py

import pandas as pd
import json
from dbs import get_open_access
import style as s
from collections import Counter
language = 'en'  # Default language
EXTENSIONS = ['.csv', '.xls', '.xlsx', '.json']

# Load localization strings
with open('localization.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)

# Define standard output fields
STANDARD_FIELDS = [
    'Doitective', 'DOI','Open Access?', 'Title', 'Year', 'First author', 'Origin database', 
    'Indexed in', 'OpenAlex API', 'Open Access status', 'OA best pdf url', 
    'Cited by count', 'Citation normalized percentile', 'Concepts', 'ISSN', 
    'Authors', 'APA 7 reference', 'Volume', 'Issue', 'Pages', 'Abstract'
]

# ----------- NORMALIZATION -----------
# AQUÍ NORMALIZAMOS EL DOI (sin https) Y GENERAMOS CAMPOS BASE DE FALLBACK FETCHANDO INFORMACIÓN
# DE LOS FILES ORIGINALES
def normalize_entry(entry, origin, filename):
    doi_raw = next(
    (str(value).strip().upper() for key, value in entry.items() if key.lower() == 'doi'), '') 
    doi_url = f"https://doi.org/{doi_raw}" if doi_raw and not doi_raw.startswith('http') else doi_raw
    oa_status, is_oa = get_open_access(entry, origin)
    title = (
    str(entry.get('Title', '')).strip()
    or str(entry.get('Article Title', '')).strip()
    or str(entry.get('DocumentTitle', '')).strip())
    year = (
    str(entry.get('Year', '')).strip()
    or str(entry.get('Publication Year', '')).strip()
    or str(entry.get('PublicationYear', '')).strip())
    f_a = (str(entry.get('First Author', '') or '').strip()
                        or str(entry.get('first author', '') or '').strip()
                        or str(entry.get('Author', '') or '').strip()
                        or str(entry.get('author', '') or '').strip()
                        or str(entry.get('Author(s)', '') or '').strip())
    return {
        'Doitective': '',
        'DOI': doi_url,
        'Open Access?': str(is_oa).lower(),
        'Title': title,
        'Year': year,
        'First author': f_a,
        'Origin database': origin,
        'Indexed in': origin,
        'OpenAlex API': f"https://doi.org/{doi_raw}" if doi_raw else '',
        'Open Access status': str(oa_status).lower(),
        'OA best pdf url': doi_url,
        'Cited by count': str(entry.get('Cited by', '') or '').strip() or str(entry.get('Cited By', '') or '').strip(),
        'Citation normalized percentile': 'Unknown',
        'Concepts': 'Unknown',
        'ISSN': str(entry.get('ISSN', '') or '').strip(),
        'Authors': str(entry.get('Authors', '') or '').strip() or str(entry.get('Author(s)', '') or '').strip(),
        'APA 7 reference': '',
        'Volume': '',
        'Issue': '',
        'Pages': '',
        'Abstract': str(entry.get('Abstract', '') or '').strip() or str(entry.get('abstract', '') or '').strip() 
    }

# ----------- DEDUPLICATION -----------
def deduplicate_by_doi(entries):
    grouped = {}
    for entry in entries:

        doi = entry.get('DOI') or f"no-doi-{entry.get('ISSN', '')}-{len(grouped)}"
        grouped.setdefault(doi, []).append(entry)

    unique, duplicates = [], []
    
    duplication_stats = Counter()
    for group in grouped.values():
        Ndups = len(group)
        duplication_stats[Ndups] += 1
        if Ndups == 1:
            entry = group[0]
            unique.append(entry)
            continue

        # Reunir todas las bases presentes
        origins = [e.get('Origin database', 'Unknown') for e in group]
        dup_in_db = ', '.join(sorted(set(origins)))
        # Anotar el número de duplicados y origen combinado en todos los registros
        for e in group:
            e['Copies'] = f"{Ndups}: {dup_in_db}"
            # Solo se prioriza OpenAlex
        selected = next((e for e in group if e.get('Origin database', '').lower() == 'openalex (native)'), None)
        if not selected:
                selected = group[0]

        unique.append(selected)
        duplicates.extend(e for e in group if e is not selected)
        
    print("\n📊 Duplication Summary:")
    for k in sorted(duplication_stats):
        count = duplication_stats[k]
        if k == 1:
            continue  # opcional: no mostrar los únicos
        label = {
            2: 'Duplicados',
            3: 'Triplicados',
            4: 'Cuadruplicados',
            5: 'Quintuplicados'
        }.get(k, f'{k}-uplicados')
        print(f"   • {label}: {count} grupo(s)")

    return unique, duplicates

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

        oa_status_blocked = {'bronze', 'hybrid', 'blocked'}
        oa_status_open = {'diamond', 'gold', 'green'}

        if is_oa == 'true':
            if oa_status in oa_status_blocked:
                pw_entries.append(entry)
            else:
                oa_entries.append(entry)
        else:
            if oa_status in oa_status_open:
                oa_entries.append(entry)
            else:
                pw_entries.append(entry)

    # Impresión de resumen para depuración
    print("\n🔑 Open Access Status 🔎 Breakdown by Source")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    emoji_map = {
        'diamond': '🏆',
        'gold': '🥇',
        'green': '🥈',
        'hybrid': '🥉',
        'bronze': '🔒',
        'closed': '🚧',
        '[]': '❓'
    }
    for origin, counter in status_by_origin.items():
        print(f"\n📚 {origin}")
        for status, count in counter.items():
            emoji = emoji_map.get(status, '📦')
            print(f"  {emoji} {status.capitalize():<8} → {count:>5} registros")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return oa_entries, pw_entries
# Dump bronze and hybrid

oa_types_to_merge = {'bronze', 'hybrid'}

def is_paywall(record):
    oa_info = record.get('Open Access?', {})
    if not oa_info.get('Open Access?', False):
        return True  # No OA → paywall
    if oa_info.get('Open Access status', '').lower() in oa_types_to_merge:
        return True  # Bronze o Hybrid → paywall
    return False

