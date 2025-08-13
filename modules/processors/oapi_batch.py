# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# oapi_fetch.py

from modules.config import common  # si lo tienes como dict Python cargado
import asyncio
import httpx
import utils.style.styles as s
doi_field = common["fields"]["doi"]
doi_field = "DOI" 
from modules.common import get_oa
N_calls = 0
is_enriching = True  # Controla cuándo detener el spinner
N_unique = 0
import asyncio
import sys
import modules.memory as m
import re
from collections import defaultdict
from rich import print
import utils.style.styles as s
async def spinner_task(size):
    import itertools
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while is_enriching:
        sys.stdout.write(s.info + f"\r{next(spinner)} Enriched: {N_unique} | " + s.error + f"📞 API Calls: {N_calls} ")
        sys.stdout.flush()
        await asyncio.sleep(0.1)


############# OPEN ALEX BATCH ENRICHMENT ###############
OPENALEX_BATCH_URL = "https://api.openalex.org/works"
MAILTO = None  # Editable por usuario
MAX_BATCH_SIZE = 25
SUB_BATCH_SIZE = 10
MAX_RETRIES = 3
TIMEOUT = 10

def merge_indexed_in(item, original):
    """
    Combina las fuentes de indexación desde OpenAlex, el campo 'Origin database'
    y el valor previo en 'Indexed in', evitando duplicados y normalizando.
    """
    # Recuperar valores
    existing = original.get('Indexed in', '')
    origin = original.get('Origin database', 'Unknown')
    indexed_raw = item.get('indexed_in', [])

    # Normalizar a minúsculas
    existing_set = {v.strip().lower() for v in existing.split(',') if v.strip()}
    origin_set = {origin.strip().lower()}
    new_oapi_set = {v.strip().lower() for v in indexed_raw if v}

    # Unir y normalizar
    all_sources = existing_set | origin_set | new_oapi_set
    final_list = sorted({s.title() for s in all_sources})  # Ej.: 'Pubmed', 'Scopus'

    return ', '.join(final_list)


def process_item(item, original=None): 
    if item is None:
        return original or {}

    global N_unique
    N_unique += 1    

    doi = (item.get('doi') or '').lower().replace("https://doi.org/", "")
    
    # Autores
    authorships = item.get('authorships') or []
    concepts = item.get('concepts') or []
    concept_names = [c.get('display_name', '') for c in concepts if isinstance(c, dict)]
    authorships = item.get('authorships', [])
    authors_list = [auth.get('author', {}).get('display_name', '') for auth in authorships if isinstance(auth, dict)]
    first_author = authors_list[0] if authors_list else ''
    authors_str = ", ".join(filter(None, authors_list))


    # Biblio info
    biblio = item.get('biblio') or {}
    volume = biblio.get('volume', '') or item.get('volume', '')
    issue = biblio.get('issue', '') or item.get('issue', '')
    pages = biblio.get('pages', '') or item.get('pages', '')


    # PMID
    pmid_raw = item.get('ids', {}).get('pmid', '')
    pmid = ''
    if isinstance(pmid_raw, str):
        match = re.search(r'\d+', pmid_raw)
        if match:
            pmid = match.group()

    # Determinar OA y mejor PDF
    is_oa, oa_url = get_oa(item)

    # Fuente e ISSN
    primary_location = item.get('primary_location') if isinstance(item.get('primary_location'), dict) else {}
    source = primary_location.get('source') if isinstance(primary_location.get('source'), dict) else {}
    issn = source.get('issn', '')
    # UID fallback

    # Percentile
    value = item.get('citation_normalized_percentile', '')
    if isinstance(value, dict):
        citation_percentile = value.get('value', '')
    else:
        citation_percentile = value if value is not None else ''
    
    value = item.get('citation_normalized_percentile')
        
        # Open Access info
    oa_info = item.get('open_access', {}) or {}
    oaid = str(item.get('ids', {}).get('openalex', ''))
    oa_status = oa_info.get('oa_status', 'Unknown').lower()  
    oa_status = oa_info.get('oa_status', 'Unknown').lower()
    citation_percentile = item.get('citation_normalized_percentile')
    oaid = str(item.get('ids', {}).get('openalex',''))
    value = item.get('citation_normalized_percentile')
    if isinstance(value, dict):
        citation_percentile = value.get('value', '')
    else:
        citation_percentile = value if value is not None else ''
    is_oa, oa_url = get_oa(item)
    indexed_raw = item.get('indexed_in')
    if isinstance(indexed_raw, list) and indexed_raw:
        indexed_in = ", ".join(indexed_raw)
    else:
        indexed_in = original.get('Indexed in', '') if original else ''

    entry = original.copy() if original else {}
    entry.update ({
        'Doitective': original.get('Doitective', '') if original else '',
        'DOI': doi or (original.get('DOI') if original else ''),
        'Open Access?': str(is_oa).lower() or str(original.get('Open Access?').lower() if original else ''),
        'Title': item.get('title') or (original.get('Title') if original else ''),
        'Year': item.get('publication_year') or (original.get('Year') if original else ''),
        'First author': first_author or (original.get('First author') if original else ''),
        #'Origin database': ,  # forzado porque viene enriquecido
        'Indexed in': indexed_in,
        # 'Copies': '',  # si lo usas luego puedes añadir fallback aquí también
        'OpenAlex API': f"https://api.openalex.org/works/doi:{doi}" if doi else (original.get('OpenAlex API') if original else ''),
        'Open Access status': str(oa_status).lower() or (original.get('Open Access status') if original else ''),
        'OA best pdf url': oa_url or (original.get('OA best pdf url') if original else ''),
        'Cited by count': item.get('cited_by_count') or (original.get('Cited by count') if original else ''),
        'Citation normalized percentile': citation_percentile or (original.get('Citation normalized percentile') if original else ''),
        'OAID': oaid or (original.get('OAID') if original else ''),
        # 'UID': ,  # esto ya no se toca
        'PMID': pmid or (original.get('PMID') if original else ''),
        'Authors': authors_str or (original.get('Authors') if original else ''),
        # 'APA 7 reference': '', # de momento, no
        'Volume': volume or (original.get('Volume') if original else ''),
        'Issue': issue or (original.get('Issue') if original else ''),
        'Pages': pages or (original.get('Pages') if original else ''),
    })
    entry['Indexed in'] = merge_indexed_in(item, original)    
            #'Abstract': '',       # OpenAlex no siempre provee abstract
    # Abstract: conserva el original si está
    if original and 'abstract' in original:
        entry['Abstract'] = original['abstract']
        
    else:
        entry['Abstract'] = item.get('abstract', '')

    return entry


N_calls= 0

async def fetch_batch(client, ids, id_type='doi'):
    global N_calls
    N_calls += 1
    cleaned_ids = set()
    for identifier in ids:
        if identifier:
            cleaned = identifier.lower().strip()
            if id_type == 'doi':
                cleaned = cleaned.replace("https://doi.org/", "")
            cleaned_ids.add(cleaned)
            
    filter_value = "|".join(sorted(cleaned_ids))
    mailto = m.get('mailto')
    params = {
        "filter": f"{id_type}:{filter_value}",
        "mailto": mailto
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.get(OPENALEX_BATCH_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[Attempt {attempt}/{MAX_RETRIES}]❗ Error fetching batch {id_type.upper()}s ({len(ids)}): {e}")
            if attempt < MAX_RETRIES:
                wait = 2 ** (attempt - 1)
                print(f"Waiting {wait}s before retrying... ⏳")
                await asyncio.sleep(wait)
            else:
                print("Max retries reached, batch failed 😢")
                return [None, None]

async def enrich_with_openalex(entries, id_type='doi'):
    global is_enriching, N_calls, N_unique
    N_calls = 0
    N_unique = 0
    is_enriching = True

    spinner = asyncio.create_task(spinner_task(len(entries)))

    valid_entries = []
    fallback_entries = []

    for e in entries:
        if id_type == 'doi':
            key_name = 'DOI'
        elif id_type == 'pmid':
            key_name = 'PMID'
        else:
            key_name = None

        key = e.get(key_name, '')
        if key:
            k = key.lower().strip()
            if id_type == 'doi':
                k = k.replace("https://doi.org/", "")
            e['_id_key'] = k
            valid_entries.append(e)
        else:
            fallback_entries.append(e)

    id_to_entry = {e['_id_key']: e for e in valid_entries}
    all_ids = list(id_to_entry.keys())
    batches = [all_ids[i:i + MAX_BATCH_SIZE] for i in range(0, len(all_ids), MAX_BATCH_SIZE)]

    enriched_entries = []
    fallback_from_batches = []

    async def process_batch(batch):
        data = await fetch_batch(client, batch, id_type=id_type)

        if data is None:
            if len(batch) > SUB_BATCH_SIZE:
                print(f"Dividing failed batch of {len(batch)} into sub-batches of {SUB_BATCH_SIZE}")
                enriched = []
                fallback = []
                sub_batches = [batch[i:i + SUB_BATCH_SIZE] for i in range(0, len(batch), SUB_BATCH_SIZE)]
                for sb in sub_batches:
                    sub_enriched, sub_fallback = await process_batch(sb)
                    enriched.extend(sub_enriched)
                    fallback.extend(sub_fallback)
                return enriched, fallback
            else:
                print(f"⚠️ Sub-batch of size {len(batch)} failed permanently.")
                return [], [id_to_entry[i] for i in batch]

        results = data.get('results', [])
        if not results:
            print(f"❓ No results for batch {batch}")
            return [], [id_to_entry[i] for i in batch]

        found_ids = set()
        enriched = []

        for item in results:
            if id_type == 'doi':
                item_id = str(item.get('doi', '')).lower().replace("https://doi.org/", "")
            elif id_type == 'pmid':
                item_id = str(item.get('ids', {}).get('pmid', '')).lower().replace("https://pubmed.ncbi.nin.nih.gov/", "")
            else:
                item_id = normalize_title(str(item.get('title', '')).lower())

            if not item_id:
                print(s.error + f"❌ Failed reinforcing id: {str(id_type)[:60]}")
                continue

            found_ids.add(item_id)
            original_entry = id_to_entry.get(item_id, {})
            enriched_entry = process_item(item, original_entry)
            enriched.append(enriched_entry)

        # Fallback para los que no se encontraron
        missing_ids = set(batch) - found_ids
        fallback = [id_to_entry[mid] for mid in missing_ids if mid in id_to_entry]

        for f in fallback:
            f.update({'Doitective': "1: Doitective wasn't able to enrich this record"})

        return enriched, []

    async with httpx.AsyncClient() as client:
        for batch in batches:
            batch_enriched, batch_fallback = await process_batch(batch)
            enriched_entries.extend(batch_enriched)
            fallback_from_batches.extend(batch_fallback)

    enriched_map = {e.get('_id_key', ''): e for e in enriched_entries if isinstance(e, dict)}
    final_entries = []

    for e in valid_entries:
        k = e['_id_key']
        enriched = enriched_map.get(k)
        final_entries.append(enriched if enriched else e)

    for fe in fallback_entries: # los que no tenían identificador
        fe.update({'Doitective': '1: not enriched (missing DOI and PMID)'})
    for fb in fallback_from_batches:  # los que fallaron en la API
        fb.update({'Doitective': '1: not enriched (not found in OAPI)'})
    
    fallbacks = fallback_entries + fallback_from_batches
    is_enriching = False
    await spinner
    return final_entries, fallbacks

### testing ###
def normalize_title_m(title: str) -> str:
    if not isinstance(title, str):
        return ''
    title = title.lower()
    title = unicodedata.normalize('NFKC', title)  # Menos agresivo que NFKD
    title = title.replace('\n', ' ').replace('\t', ' ')
    title = re.sub(r"\s+", " ", title).strip()
    return title

##################### TITLE INDIVIDUAL CALLS  👈#####################################
def clean_title_for_query(title):
    title = title.strip()
    title = re.sub(r'[\s\–\—]+', ' ', title)  # Normaliza espacios y guiones largos
    title = re.sub(r'[^\w\s]', '', title)     # Elimina signos de puntuación
    return title.lower()


import unicodedata
def normalize_title(title: str) -> str:
    if not isinstance(title, str):
        return ''
    # 1. Pasar a minúsculas
    title = title.lower()
    # 2. Normalizar acentos y caracteres Unicode
    title = unicodedata.normalize('NFKD', title)
    title = ''.join(c for c in title if not unicodedata.combining(c))
    # 3. Eliminar puntuación, símbolos, y guiones largos
    title = re.sub(r"[^\w\s]", "", title)
    # 4. Eliminar espacios redundantes
    title = re.sub(r"\s+", " ", title).strip()

    return title

async def fetch_by_title(client, title):
    global N_calls
    N_calls += 1
    
    clean_title = normalize_title_m(title)
    params = {
        "filter": f'title.search:{clean_title}',
        "per_page": 1,
        "mailto": m.get('mailto')
    }

    # Construir URL final para mostrar (solo para depuración)
    url = httpx.URL("https://api.openalex.org/works", params=params)
    print(f"\n🔎 Searching title:\n   {s.warning}{title}")
    print(f"🔗 URL: {s.dim_white}{url}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[Attempt {attempt}/{MAX_RETRIES}]❗ Error fetching title '{title}': {e}")
            if attempt < MAX_RETRIES:
                wait = 2 ** (attempt - 1)
                print(f"Waiting {wait}s before retrying... ⏳")
                await asyncio.sleep(wait)
            else:
                print("Max retries reached, single title call failed 😢")
                return None


async def enrich_with_openalex_titles(entries):
    enriched_entries = []
    fallback = []
    async with httpx.AsyncClient() as client:
        for i, entry in enumerate(entries):
            norti = entry.get('norti', '').strip()
            print(f"[{i+1}/{len(entries)}] Searching OpenAlex for title: {norti[:60]}")

            if not norti:
                # Título vacío, descartamos o añadimos con marca clara
                print(f"⚠️ Empty title, skipping entry #{i+1}")
                entry.update({'Doitective': "1: Doitective wasn't able to enrich this record"})
                fallback.append(entry)
                continue

            data = await fetch_by_title(client, norti)
            
            if data is None or 'results' not in data or not data['results']:
                # No hay resultados, descartamos o marcamos
                print(s.error + f"❌ No results for title: {norti[:60]}")
                # Si quieres mantener registro, podrías hacer:
                # entry['oa_status'] = 'no results'
                # enriched_entries.append(entry)
                entry.update({'Doitective': "1: Doitective wasn't able to enrich this record"})
                fallback.append(entry)
                continue

            # Solo procesar el primer resultado
            item = data['results'][0]

            # Aquí llamar a la función que mezcla item con entry y devuelve entry enriquecido
            enriched_entry = process_item(item, entry)
            print(s.success + f"✔ Found match for title: {norti[:60]}")
            # Si la función devuelve None o algo inválido, no añadimos
            if enriched_entry:
                enriched_entries.append(enriched_entry)
            else:
                fallback.append(entry)
                print(f"⚠️ Failed to process item for title: {norti[:60]}")

                
    return enriched_entries, fallback


async def enrich_with_openalex_full(to_enrich):
    if not isinstance(to_enrich, list):
        raise TypeError("to_enrich must be a list of records (dicts)")
    enriched = []
    returns = []
    to_enrich = [r for r in to_enrich if r.get('batch_tag') in ('doi', 'pmid')]
    dois = [r for r in to_enrich if r.get("batch_tag") == 'doi']
    pmids = [r for r in to_enrich if r.get("batch_tag") == 'pmid']
    titles = [r for r in to_enrich if r.get("batch_tag") == 'norti']
    
    by_tag = defaultdict(list)
    for r in to_enrich:
        by_tag[r['batch_tag']].append(r)

    print(f"🔍 Enriching:")
    for tag in ('doi', 'pmid', 'norti'):
        print(f"   • {tag.upper()}: {len(by_tag[tag])} records")

    if dois:
        doi_results = await enrich_with_openalex(dois, id_type='doi')
        doi_enrich, doi_fall = doi_results
        print(s.success + f"\r📀 DOI Enrichment completed! " + s.dim_white)
        print(f"   Report: " + s.success + f"{len(doi_enrich)}" + s.magenta + f"/" + s.info + f"{len(dois)}" + s.dim_white + f" records enriched in " + s.error + f"{N_calls} calls 📞")
    if pmids:
        pmid_results = await enrich_with_openalex(pmids, id_type='pmid') 
        pmid_enrich, pmid_fall = pmid_results
        print(s.warning + f"\r📀 DOI Enrichment completed! " + s.dim_white)
        print(f"   Report: " + s.warning + f"{len(pmid_enrich)}" + s.magenta + f"/" + s.info + f"{len(pmids)}" + s.dim_white + f" records enriched in " + s.error + f"{N_calls} calls 📞")
    # if titles:
    #    title_results = await enrich_with_openalex_titles(titles)
     #   tit_enrich, tit_fall = title_results
    #    print(s.warning + f"\r📀 DOI Enrichment completed! " + s.dim_white)
     #   print(f"   Report: " + s.warning + f"{len(tit_enrich)}" + s.magenta + f"/" + s.info + f"{len(titles)}" + s.dim_white + f" records enriched in " + s.error + f"{N_calls} calls 📞")

        
    enriched = doi_enrich + pmid_enrich
    fallback = doi_fall + pmid_fall + titles
    return enriched, fallback



