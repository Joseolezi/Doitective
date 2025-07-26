# main.py
from ui import update_UI
import os
import json
import datetime
from ui import update_UI
import shutil
from exporter import export_results, end_anim
from oapi_fetch import enrich_with_openalex
import asyncio
from loading_indicator import LoadingIndicator
import style as s
import g_vars as v
# Clean screen without losing info
def soft_clear_to_top():
    lines = shutil.get_terminal_size().lines
    print("\n" * lines)
    6

def getmailto_txt ():
    filename = 'mailto.txt'
    if os.path.isfile(filename):
        if os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                v.set_var('mailto', content)

# AutoRef UI MANAGER
# Main entry point for the AutoRef application
def run(key):
    next_step = key
    while next_step not in ['start', 'exit']:
        next_step = update_UI(next_step)
    if next_step == 'start':    
        asyncio.run(main())
    if next_step == 'exit':
        exit(0)

# Load localization strings
with open('localization.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)
    language = localization.get("language", "en")
    texts = localization.get(language, {})
soft_clear_to_top ()
print("\t\t" + texts["start_message"] + "\n")

# Define input folder
INPUT_FOLDER = localization.get("input_f")

################ MAIN ####################
from screening import normalize_entry, deduplicate_by_doi, separate_by_open_access, split_for_enrichment
from dbs import load_files_from_raw_folder, detect_origin, last_security_check

async def main():
    print(texts['start_message'])
    print(s.magenta + "Loading and validating files 📂 \n\n")

    # Step 1: Load valid files
    valid_files = load_files_from_raw_folder(INPUT_FOLDER)
    if not valid_files:
        print(texts['no_valid_files'])
        return

    openalex_stack = []
    all_normalized = []
    # Step 2: Detect origin and process files
    for file_path in valid_files:
        try:
            records, origin, is_openalex = detect_origin(file_path, openalex_stack)    
            print(s.error + f"📌 Detected origin: {origin} — {os.path.basename(file_path)}")

            if is_openalex:
                continue # ya fue agregado a openalex_stack
            
            filename = os.path.basename(file_path)
            for record in records:
                assert isinstance(record, dict), f"❌ record is not a dict: {record}" # DEBBUGING
                normalized = normalize_entry(record, origin, filename) #!! SOLUCIÓN SALOMÓNICA
                all_normalized.append(normalized)

        except Exception as e:
            print(texts['error_reading_file'].format(file=os.path.basename(file_path), error=str(e)))
        
    # Agregamos OpenAlex ya normalizado
    all_normalized.extend(openalex_stack)

    if not all_normalized:
        print(texts['no_data_parsed'])
        return
    # Añadimos default entry data
    # Step 4: Deduplicate
    unique, duplicates = deduplicate_by_doi(all_normalized)
    N_dups = len(duplicates)
    N_unique = len (unique)
    print(s.success + f" ✔  {N_unique} Unique records identified")
    print(s.error + f"🧦 {len(duplicates)} Duplicated records identified \n")

    # Step 4.5: Separate openalex unique from poor unique
    from_openalex, to_enrich = split_for_enrichment(unique)
    for entry in from_openalex:
        doi = entry.get('DOI', '')
        if doi and not doi.startswith('http'):
            entry['DOI'] = f'https://doi.org/{doi}'
    # Step 5: Enrichment with OpenAlex  
    print(s.magenta + f"OpenAlex native records: " + s.success + f"{len(from_openalex)}")
    print(s.info + f"Weak records: " + s.error + f"{len(to_enrich)}")  
        # Empieza la animación
    unique_final = [] 
    paywall = []
    indicator = LoadingIndicator()
    L_to_enrich = len(to_enrich)
    try:
        indicator.update_message(s.dim_white + f"Enriching " + s.warning + f"{L_to_enrich}" + s.dim_white + f" weak records with OpenAlex ⚡")
        print(s.dim_white + f"Enriching " + s.warning + f"{L_to_enrich}" + s.dim_white + f" weak records with OpenAlex ⚡")
        unique_final = from_openalex + await enrich_with_openalex(to_enrich, L_to_enrich) 

    finally:
        await indicator.stop()  # Detiene el spinner
        print(texts['finished']) 
        # Último check de seguridad
       # unique_final = last_security_check(unique_final)
        N_unique = len(unique_final)  
    

    # Step 7: Separar OA vs Paywall usando info actualizada
    unique_oa, paywall = separate_by_open_access(unique_final)
    N_oa = len(unique_oa)
    N_pw = len(paywall)

    # Esto los contea y displayea en la consola - ES MIERDA DE FEO
    #from collections import Counter
    #summary = Counter([e.get("base_origin", "Unknown") for e in unique_final])
    #print(summary)
    
    print(s.success + f"🧠 Unique Open Access records: {N_oa}")
    print(s.error + f"💸 Unique PayWall records: {N_pw}")
    print(s.warning + f"🧦  Duplicates dumped: {N_dups} \n")
    # Step 8: Export everything
    print(s.magenta + "\t\t     🎁 Packaging final data 🎁\n")
    from screening import STANDARD_FIELDS
    OUTPUT_FOLDER = localization.get("output_folder")
    SESSION_FOLDER = os.path.join(OUTPUT_FOLDER + f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

    export_results(unique_oa, paywall, duplicates, fieldnames=STANDARD_FIELDS , session_folder=SESSION_FOLDER)
    end_anim ()

if __name__ == '__main__':
    from exporter import end_anim
    getmailto_txt ()
    run('w')  # Start with the welcome screen
    # This will trigger the UI update and start the application flow
