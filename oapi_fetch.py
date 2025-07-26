# oapi_fetch.py

from apa7 import generate_apa_reference_7
from config import common  # si lo tienes como dict Python cargado
import asyncio
import httpx
import style as s
doi_field = common["fields"]["doi"]
doi_field = "DOI" 
from common import get_oa
N_calls = 0
N_enriched = 0
is_enriching = True  # Controla cuándo detener el spinner
import asyncio
import sys
import g_vars as v

async def spinner_task(unique_N, size):
    import itertools
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while is_enriching:
        sys.stdout.write(s.info + f"\r{next(spinner)} Enriched: {unique_N} | " + s.error + f"📞 API Calls: {N_calls} ")
        sys.stdout.flush()
        await asyncio.sleep(0.1)
    print(s.warning + f"\r📀 Enrichment completed! " + s.dim_white + f"Report: " + s.success + f"{unique_N}" + s.magenta + f"/" + s.info + f"{size}" + s.dim_white + f" records enriched in " + s.error + f"{N_calls} calls 📞")

############# OPEN ALEX BATCH ENRICHMENT ###############
OPENALEX_BATCH_URL = "https://api.openalex.org/works"
MAILTO = None  # Editable por usuario
MAX_BATCH_SIZE = 25
SUB_BATCH_SIZE = 10
MAX_RETRIES = 3
TIMEOUT = 10


                
def format_authors_apa7(authors_str):
    if not authors_str:
        return "Unknown Author"
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]
    formatted_authors = []
    for auth in authors:
        parts = auth.split()
        if len(parts) == 0:
            continue
        last_name = parts[-1]
        initials = [p[0].upper() + "." for p in parts[:-1] if p]
        formatted_author = f"{last_name}, {' '.join(initials)}"
        formatted_authors.append(formatted_author)
    if len(formatted_authors) == 1:
        return formatted_authors[0]
    elif len(formatted_authors) <= 7:
        return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        first_six = ", ".join(formatted_authors[:6])
        last = formatted_authors[-1]
        return f"{first_six}, ... , & {last}"

def sentence_case(text):
    if not text:
        return ""
    return text[0].upper() + text[1:].lower()

import re

def format_authors_apa7_full(authors_str):
    if not authors_str:
        return "Unknown Author"
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]
    formatted_authors = []
    for auth in authors:
        parts = auth.split()
        if len(parts) == 0:
            continue
        last_name = parts[-1]
        initials = [p[0].upper() + "." for p in parts[:-1] if p]
        formatted_author = f"{last_name}, {' '.join(initials)}"
        formatted_authors.append(formatted_author)
    n = len(formatted_authors)
    if n <= 20:
        if n == 1:
            return formatted_authors[0]
        elif n == 2:
            return f"{formatted_authors[0]} & {formatted_authors[1]}"
        else:
            return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        # Más de 20 autores: primeros 19, ..., último autor
        first_19 = ", ".join(formatted_authors[:19])
        last = formatted_authors[-1]
        return f"{first_19}, ... , & {last}"

def sentence_case(text):
    if not text:
        return ""
    # Convertir todo a minúsculas salvo primera letra
    text = text.strip()
    # Manejo básico de nombres propios: no cambiar mayúsculas después del primero (simplificado)
    return text[0].upper() + text[1:].lower()

def title_case(text):
    if not text:
        return ""
    # Lista básica de palabras que no se capitalizan (artículos, conjunciones, preposiciones cortas)
    minor_words = {
        "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
        "at", "by", "in", "of", "on", "to", "up", "via", "as", "per"
    }
    words = re.split(r'(\s+)', text)
    result = []
    for i, word in enumerate(words):
        if word.isspace():
            result.append(word)
            continue
        lower_word = word.lower()
        if i == 0 or i == len(words) - 1 or lower_word not in minor_words:
            # Primera o última palabra o no es minor word => capitalizar
            result.append(word.capitalize())
        else:
            result.append(lower_word)
    return "".join(result)


N_calls= 0
async def fetch_batch(client, dois):
    # Limpiar y normalizar DOIs antes de la query
 
    global N_calls
    N_calls += 1
    cleaned_dois = set()
    for doi in dois:
        if doi:
            cleaned = doi.lower().strip().replace("https://doi.org/", "")
            cleaned_dois.add(cleaned)
    dois = sorted(cleaned_dois)
    # Generar los parámetros para la llamada batch
    filter_value = "|".join(dois)
    params = {
        "filter": f"doi:{filter_value}",
        "mailto": v.get_var('mailto')
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.get(OPENALEX_BATCH_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[Attempt {attempt}/{MAX_RETRIES}]❗ Error fetching batch DOIs ({len(dois)}): {e}")
            if attempt < MAX_RETRIES:
                wait = 2 ** (attempt - 1)
                print(f"Waiting {wait}s before retrying... ⏳")
                await asyncio.sleep(wait)
            else:
                print("Max retries reached, batch failed 😢")
                return None
           
def update_enrichment_counter(n):
    print(f"🔄 " + s.warning + f"Enriched records: " + s.info + f"{n}", end='', flush=True)

async def enrich_with_openalex(entries, size):
    doi_to_entry = {e['DOI'].replace("https://doi.org/", "").lower(): e for e in entries if e.get('DOI')}
    enriched_entries = []
    global is_enriching, N_calls, N_enriched
    N_calls = 0
    N_enriched = 0
    is_enriching = True

    spinner = asyncio.create_task(spinner_task(len(entries), size))
    
    async with httpx.AsyncClient() as client:
        doi_to_user_base = {e['DOI'].replace("https://doi.org/", "").lower(): e.get('base_origin', '') for e in entries if e.get('DOI')}
        all_dois = list(doi_to_user_base.keys())
        
        batches = [all_dois[i:i+MAX_BATCH_SIZE] for i in range(0, len(all_dois), MAX_BATCH_SIZE)]

        async def process_batch(batch):
            data = await fetch_batch(client, batch)
            if data is None:
                if len(batch) > SUB_BATCH_SIZE:
                    print(f"Dividing failed batch of {len(batch)} into sub-batches of {SUB_BATCH_SIZE}")
                    sub_batches = [batch[i:i+SUB_BATCH_SIZE] for i in range(0, len(batch), SUB_BATCH_SIZE)]
                    results = []
                    for sb in sub_batches:
                        res = await process_batch(sb)
                        results.extend(res)
                    return results
                else:
                    print(f"Sub-batch of size {len(batch)} failed permanently.")
                    return [doi_to_entry(doi, doi_to_user_base.get(doi, '')) for doi in batch]
                
            
            found_dois = set()
            enriched = []
            for item in data.get('results', []):
                doi = item.get('doi', '').lower().replace("https://doi.org/", "")
                found_dois.add(doi)
                global N_enriched
                N_enriched += 1
                authors_list = [auth.get('author', {}).get('display_name', '') for auth in item.get('authorships', [])]
                authors_str = ", ".join(filter(None, authors_list))
                base_origin = doi_to_user_base.get(doi, 'Unknown')
                # Extraer volumen, issue y páginas si están (OpenAlex puede tener 'volume', 'issue', y 'biblio' para páginas)
                volume = item.get('biblio', {}).get('volume', '') or item.get('volume', '')
                issue = item.get('biblio', {}).get('issue', '') or item.get('issue', '')
                pages = item.get('biblio', {}).get('pages', '') or item.get('pages', '')
                oa_info = item.get('open_access', {})
                oa_status = oa_info.get('oa_status', 'Unknown').lower
                
                is_oa, oa_url = get_oa(item)
                value = item.get('citation_normalized_percentile')
                if isinstance(value, dict):
                    citation_percentile = value.get('value', '')
                else:
                    citation_percentile = value if value is not None else ''
                    
                entry = {
                    #'Doitective notes': ''
                    'DOI': doi,
                    'Open Access?': str(is_oa).lower(),
                    'Title': item.get('title', ''),
                    'Year': item.get('publication_year', ''),
                    'First author': item.get('authorships', [])[0].get('author', {}).get('display_name', '') if item.get('authorships') else '',
                    # 'Origin database': # NO LO TOQUES
                    'Indexed in': ", ".join(item.get('indexed_in', [])),
                    #'Copies': '',
                    'OpenAlex API': f"{OPENALEX_BATCH_URL}?filter=doi:{doi}",                    
                    'Open Access status': item.get('open_access', {}).get('oa_status', 'Unknown').capitalize(),
                    'OA best pdf url': oa_url,
                    'Cited by count': item.get('cited_by_count', ''),
                    'Citation normalized percentile': citation_percentile,
                    'Concepts': ", ".join([c.get('display_name', '') for c in item.get('concepts', [])]),
                    'ISSN': item.get('host_venue', {}).get('issn_l', ''),
                    'Authors': ", ".join([item.get('author').get('display_name', '') for item in item.get('authorships', [])]),
                    'APA 7 reference': '',  # Se genera abajo
                    'Volume': volume,
                    'Issue': issue,
                    'Pages': pages,
                    # 'Abstract' se conserva del original, no se sobrescribe aquí // 'Abstract': item.get('abstract', ''),
                    
                }   
                entry['APA reference'] = generate_apa_reference_7(entry)
                entry['Open Access'] = oa_status
                enriched.append(entry)

            missing_dois = set(batch) - found_dois
            for doi in missing_dois:
                original_entry = doi_to_entry.get(doi)
                if original_entry:
                    enriched.append(original_entry) 

            return enriched

        for batch in batches:
            batch_enriched = await process_batch(batch)
            enriched_entries.extend(batch_enriched)

    enriched_map = {e['DOI'].lower(): e for e in enriched_entries}
    final_entries = []
    for original in entries:
        doi = original.get('DOI', '').replace("https://doi.org/", "").lower()
        enriched = enriched_map.get(doi)
        if enriched:
            combined = {**original, **enriched}  # enriquecidos sobrescriben originales
            final_entries.append(combined)
        else:
            final_entries.append(original)

    is_enriching = False
    await spinner  # Espera a que el spinner termine
    return final_entries