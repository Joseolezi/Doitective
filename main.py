# main.py
from ui import update_UI
import os
import json
import datetime
from ui import update_UI
import shutil
from exporter import export_results
from open_alex_enrich import enrich_with_openalex
import asyncio
from loading_indicator import LoadingIndicator
import style as s
# Clean screen without losing info
def soft_clear_to_top():
    lines = shutil.get_terminal_size().lines
    print("\n" * lines)
    6
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
INPUT_FOLDER = localization.get("input_folder")

################ MAIN ####################
from processor import (
    load_files_from_raw_folder,
    detect_origin,
    normalize_entry,
    deduplicate_by_doi,
    separate_by_open_access,
)


async def main():
    
    print(texts['start_message'])
    print(s.magenta + "Loading and validating files 📂 \n\n")
    # Step 1: Load valid files
    valid_files = load_files_from_raw_folder(INPUT_FOLDER)
    if not valid_files:
        print(texts['no_valid_files'])
        return

    # Step 2–3: Read, detect origin, normalize and aggregate all records
    print(s.info + "Normalizing data 📄 \n\n")
    all_normalized = []
    for file_path in valid_files:
        try:
            detected_origin, records = detect_origin(file_path)
            filename = os.path.basename(file_path)
            for record in records:
                normalized = normalize_entry(record, detected_origin, filename)
                all_normalized.append(normalized)
        except Exception as e:
            print(texts['error_reading_file'].format(file=os.path.basename(file_path), error=str(e)))

    if not all_normalized:
        print(texts['no_data_parsed'])
        return

    # Step 4: Deduplicate
    print(s.error + "Deduplicating..." + s.warning + "(priorizing richest records) 🧦 \n\n")
    unique, duplicates = deduplicate_by_doi(all_normalized)

    # Step 5: Enrichment with OpenAlex    
        # Empieza la animación
    indicator = LoadingIndicator()
    try:
        indicator.update_message(s.warning + "Enriching with OpenAlex ⚡")
        unique_rich = await enrich_with_openalex(unique)  # tu proceso real
    finally:
        await indicator.stop()  # Detiene el spinner
        print(texts['finished'])   
        # Asegurarse de que todos tengan referencia APA, aunque OpenAlex no haya devuelto nada
    print(s.info + "Generating APA references 💡")
    from apa7 import generate_apa_reference_7
    for entry in unique_rich:
        if not entry.get("APA reference"):
            entry["APA reference"] = generate_apa_reference_7(entry)

    # Step 7: Separar OA vs Paywall usando info actualizada
    
    unique_oa, paywall = separate_by_open_access(unique_rich)
    N_oa = len(unique_oa)
    N_pw = len(paywall)
    N_dups = len(duplicates)
    print(s.success + f"\n🧠 Unique Open Access records: {N_oa}")
    print(s.error + f"🔒 Unique PayWall records: {N_pw}")
    print(s.warning + f"🧦 Duplicates dumped: {N_dups} \n")
    # Step 8: Export everything
    print(s.magenta + "\t\t🎁 Packaging final data 🎁\n")
    from processor import STANDARD_FIELDS
    OUTPUT_FOLDER = localization.get("output_folder")
    SESSION_FOLDER = os.path.join(OUTPUT_FOLDER + f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

    export_results(unique_oa, paywall, duplicates, fieldnames=STANDARD_FIELDS , session_folder=SESSION_FOLDER)


if __name__ == '__main__':
    run('w')  # Start with the welcome screen
    # This will trigger the UI update and start the application flow
