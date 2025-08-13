# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# main.py
from modules.ui import update_UI
import os
import json
import datetime
from modules.ui import update_UI
import shutil
from modules.processors.exporter import export_results
from modules.processors.oapi_batch import enrich_with_openalex, enrich_with_openalex_full, enrich_with_openalex_titles
import asyncio
from modules.loading_indicator import LoadingIndicator
import utils.style.styles as s
import modules.memory as m
from modules.users.e_mail_validation import verify_email as ve, fetch_variable_in_txt as fvt
import sys
from datetime import datetime
import modules.texts as t
from modules.processors.final_sort import classify_records_from_marked_sheets


log_filename = datetime.now().strftime("logs/log_%Y-%m-%d_%H-%M-%S.txt")
log_file = open(log_filename, "w", encoding="utf-8")
# Redirigir stdout a consola y archivo
class DualOutput:
    def __init__(self, *outputs):
        self.outputs = outputs
    def write(self, text):
        for output in self.outputs:
            output.write(text)
            output.flush()
    def flush(self):
        for output in self.outputs:
            output.flush()

sys.stdout = DualOutput(sys.stdout, log_file)
sys.stderr = sys.stdout  # opcional: captura también errores

# Clean screen without losing info
def soft_clear_to_top():
    lines = shutil.get_terminal_size().lines
    print("\n" * lines)
    6

def getmailto_txt ():
    filename = 'user_settings.txt'
    if os.path.isfile(filename):
        if os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                m.set('mailto', content)
# AutoRef UI MANAGER
# Main entry point for the AutoRef application
def run(key):
    CLASSIFY_FOLDER = m.get("classify_folder")
    next_step = key

    if key not in ['1', 'launch', 'exit', '']:
        # UI loop: continuar hasta recibir un comando válido
        while next_step not in ['1', 'launch', 'exit']:
            next_step = update_UI(next_step)
        
    # Ejecutar acción según el valor final
    if str(next_step) == '1':
        classify_records_from_marked_sheets(CLASSIFY_FOLDER)
    elif next_step == 'launch':
        asyncio.run(main())
    elif next_step == 'exit' or '':
        print("Exiting Doitective 👣🔍👀💼 Goodbye!")
        exit(0)

# Load localization strings
with open('utils/localization/base_loc.json', 'r', encoding='utf-8') as f:
    localization = json.load(f)
    language = localization.get("language", "en")
    l_texts = localization.get(language, {})
soft_clear_to_top ()
print("\t\t" + l_texts["start_message"] + "\n")

# Define input folder

INPUT_FOLDER = localization.get("input_f")
STANDARD_FIELDS = m.get('standard_fields')
def clean_for_export(entries):
    exportable = STANDARD_FIELDS
    for entry in entries:
        exportable.append({k: v for k, v in entry.items() if not k.startswith('_')})
    return exportable
################ MAIN ####################
from modules.screening import (separate_by_open_access,
                            deduplicate_by_ids, classify_records)

from modules.processors.log_machine import export_classification_report as ecr

async def main():

    # Step 1: Load valid files
    from modules.processors.dbs_main import parse_input_data
    
    all_normalized, not_articles = parse_input_data ()
   
        # Mostrar resumen
    print(f"\n" + s.info + f"Total records identified: " + s.magenta + f"{len(all_normalized)}")
    print(f"{s.dim_white}Discarted non-articles: {len(not_articles)}")
    if not all_normalized:
        print(l_texts['no_data_parsed'])
        return
    ######################################################################
    total_raw = len(all_normalized) + len(not_articles)
    # Step 4: Deduplicate
    unique, duplicates, remaining = deduplicate_by_ids(all_normalized)
    N_dups = len(duplicates)
    N_unique = len(unique)
    print(s.success + f" ✔ {N_unique} Unique records identified")
    print(s.error + f"🧦 {len(duplicates)} Duplicated records detected \n")
    remaining_l = len(remaining)
    # Step 4.5: Separate openalex unique from poor unique
    oat, closedt, not_known = separate_by_open_access(unique)
    oa_b4 = len(oat)
    closed_b4 = len(closedt)
    
    doi_group, pmid_group, title_group, errors = classify_records (unique)
    
    errors_l = len(errors)
    not_articles_l = len(not_articles)
    print(f"Preliminary scan result:")
    print(f"NOT ARTICLES: {not_articles_l}")
    print(f"ERRORS: {errors_l}")
    print(f"REMAINING: {remaining_l} \n")
    print(s.warning + f"valid ID quality breakdown")
    print(s.info + f"DOI: " + s.success + f"{len(doi_group)}")    
    print(s.info + f"PMID: " + s.warning + f"{len(pmid_group)}")    
    print(s.info + f"Title: " + s.error + f"{len(title_group)}")    
    # Agrupar según mejor identificador
    for d in duplicates: 
        d.update({'Doitective': "0: Ineligible: Duplicated"})
    for e in errors:
        e.update({'Doitective': '0: Ineligible: Unkown valid ID'})
    for na in not_articles:
        na.update({'Doitective': "0: Ineligible: 'matches exclusion criteria: not an Article'"})
    for r in remaining: 
        r.update({'Doitective': "0: Doitective couldn't resolve this mistery"})
    ineligible = not_articles + errors + remaining
    
    ######################################################################
    pre_title_group = title_group
    indicator = LoadingIndicator()
    try:
        indicator.update_message(s.dim_white + f"Enriching " + s.warning + f"{len(doi_group + pmid_group + title_group)}" + s.dim_white + f" weak records with OpenAlex ⚡")
        doi_group_result = await enrich_with_openalex(doi_group, 'doi')
        pmid_group_result = await enrich_with_openalex(pmid_group, 'pmid')
        # title_group_result = await enrich_with_openalex_titles(title_group)
        doi_group, fb_dois = doi_group_result
        pmid_group, fb_pmids = pmid_group_result
     #   title_group, fb_titles = title_group_result
    finally:
        await indicator.stop()
        print(l_texts['finished'])
    fallback_final = fb_dois + fb_pmids # + fb_titles
    unique_final = doi_group + pmid_group + title_group + fallback_final
    print(s.warning + f"OAPI batchcalling breakdown")
    print(s.dim_white + f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'» Enriched records by ' + s.success + f'DOI: {len(doi_group)}/' + s.dim_white + f'{len(doi_group+fb_dois)}')
    print(f'» Enriched records by ' + s.warning + f'PMID: {len(pmid_group)}/' + s.dim_white + f'{len(pmid_group+fb_pmids)}')
  #  print(f'» Enriched records by ' + s.error + f'title: {len(title_group)}/' + s.dim_white + f'{len(title_group+fb_titles)}')

    total_enriched = len(doi_group) + len(pmid_group) + len(title_group)
    base_enriched = total_enriched + len(fallback_final)

            # Último check de seguridad: OAID
        # unique_final = last_security_check(unique_final)
    
        # Step 7: Separar OA vs Paywall usando info actualizadr
    unique_oa, paywall, unk_entries = separate_by_open_access(unique_final)
    N_oa = len(unique_oa)
    N_pw = len(paywall)
    N_dups = len(duplicates)
    N_no_art = len(not_articles)
    N_errors = len(errors)
    db_sources = m.get("database_sources")
    db_sources = ",".join(sorted(db_sources))
    doit_version = m.get("doit_version")
    prisma_dict = {
    "database_sources": db_sources,
    "other_sources": "",
    "duplicates_removed": N_dups,
    "records_screened": N_unique,
    "records_excluded": "",
    "full_texts_assessed": "",
    "full_texts_excluded": "",
    "full_texts_exclusion_reasons": "",
    "studies_included": "",
    "reports_included": "",
    "final_included": "",
    "notes": "",
    "date_exported": datetime.now().strftime("%S-%M-%H_%d-%m-%Y"),
    "doitective_version": doit_version,
    "user_id": "Main investigator",
    "project_name": "Doitective default",
    "flow_comment": ""
}
    not_articles += errors + remaining + unk_entries
    N_identified = N_unique - N_errors
    # Esto los contea y displayea en la consola 
    #from collections import Counter
    #summary = Counter([e.get("base_origin", "Unknown") for e in unique_final])
    #print(summary)
    print("\n" + s.title + f"     >> " + s.dim_white + "FINAL STATS REPORT " + s.title + f"<<")
    print(s.dim_white+ f"📂 All records extracted from raw folder: {total_raw}")
    print(s.title + f"🧦 Duplicates: " + s.title + f"{N_dups}")
    print(s.error + f"📰 Not " + s.dim_white + f"articles: " + s.error + f"{N_no_art}")
    print(s.dim_white+ f"🔎 Unique records scoped: " + s.info + f"{N_unique}")
    print(s.dim_white + f"🤔 Unknown records: {N_errors}\n")
    print(s.dim_white+ f"\t📌 Unique records successfully identified: " + s.info + f"{len(unique_final)}")
    print(s.dim_white+ f"\t📀 Unique records enriched: " + s.warning + f"{total_enriched}" + s.dim_white + " / " + f"{base_enriched}")
    print(s.success + f"\t🔑 Unique Open Access " + s.dim_white + f"records: {oa_b4} >> " + s.success + f"{N_oa}")
    print(s.warning + f"\t🚧 Unique Restricted " + s.dim_white + f"records: {closed_b4} >> " + s.warning + f"{N_pw}\n")

    
    # Step 8: Export everything
    print(s.dim_white + f"\t🎁 Packaging final data 🎁\n")
    
    SESSION_FOLDER = os.path.join(OUTPUT_FOLDER, datetime.now().strftime("Doitective_works__%Y-%m-%d_%H-%M-%S"))
    STANDARD_FIELDS = m.get('standard_fields')
    export_results(unique_oa, paywall, duplicates, ineligible, fieldnames=STANDARD_FIELDS , session_folder=SESSION_FOLDER)


if __name__ == '__main__':
    mode_key = 'w'
    OUTPUT_FOLDER = localization.get("output_folder")

 
        # Crear archivo con marca de tiempo
    log_filename = os.path.join(datetime.now().strftime("logs/log_%Y-%m-%d_%H-%M-%S.txt"))
    log_file = open(log_filename, "w", encoding="utf-8")

    txt_path = 'user_settings.txt'
    txt_key = 'mailto'
    mode_key = 'mode'
    txt_value = fvt(txt_path, txt_key)
    mode = fvt(txt_path, mode_key)
    if txt_value is not None:
        print(f"El valor de '{txt_key}' es: {txt_value}")
        m.set('mailto', txt_value) 
    else:
        print(f"La variable '{txt_key}' no fue encontrada en el archivo.")
        m.set('mailto', None)   
    if mode == '2':
        entry_key = 'w'
    elif mode == '1':
        entry_key = '1'
    
    run(entry_key)  # Start with the welcome screen
    # This will trigger the UI update and start the application flow


