# exporter.py
import os
import pandas as pd
import style as s
import asyncio
import itertools
import sys
import time

async def end_anim ():
    await spinner_task ()
    
async def spinner_task(duration=6):
    walk_off = itertools.cycle([
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼   ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼      ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼         ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼            ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼              ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼                   ",
        "👣👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼                      ",
        "👣👣👣👣👣👣👣👣👣👣👣👣🔍👀💼                        ",
        "👣👣👣👣👣👣👣👣👣👣👣🔍👀💼                           ",
        "👣👣👣👣👣👣👣👣👣👣🔍👀💼                             ",
        "👣👣👣👣👣👣👣👣👣🔍👀💼                                ",
        "👣👣👣👣👣👣👣👣🔍👀💼                                   ",
        "👣👣👣👣👣👣👣🔍👀💼                                      ",
        "👣👣👣👣👣👣🔍👀💼                                        ",
        "👣👣👣👣👣🔍👀💼                                           ",
        "👣👣👣👣🔍👀💼                                              ",
        "👣👣👣🔍👀💼                                                 ",
        "👣👣🔍👀💼                                                    ",
        "👣🔍👀💼                                                      ",
        "🔍👀💼                                                         ",
        "👀💼                                                           ",
        "💼                                                              ",
        "                                                                 "
    ])


    start = time.time()
    while time.time() - start < duration:
        frame = next(walk_off)
        sys.stdout.write(f"\r{next(walk_off)}")
        sys.stdout.flush()
        await asyncio.sleep(0.5)

    print("\n🛑 Exiting...")
    exit (0)

def export_results(unique_oa, paywall, duplicates, fieldnames, session_folder):
    # Asegurarse que la carpeta existe
    os.makedirs(os.path.join(session_folder, 'excel'), exist_ok=True)
    os.makedirs(os.path.join(session_folder, 'csv'), exist_ok=True)

    # Rellenar campos faltantes con string vacío
    for entry in unique_oa + paywall + duplicates:
        for field in fieldnames:
            entry.setdefault(field, '')

    # Crear DataFrames ordenados por fieldnames
    df_oa = pd.DataFrame(unique_oa, columns=fieldnames)
    df_paywall = pd.DataFrame(paywall, columns=fieldnames)
    df_dup = pd.DataFrame(duplicates, columns=fieldnames)

    # Exportar Excel con 3 hojas
    excel_path = os.path.join(session_folder, 'excel', 'screened_records.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_oa.to_excel(writer, sheet_name='Unique OA Records', index=False)
        df_paywall.to_excel(writer, sheet_name='PayWall Records', index=False)
        df_dup.to_excel(writer, sheet_name='Duplicates', index=False)

    # Exportar CSV separados
    df_oa.to_csv(os.path.join(session_folder, 'csv', 'unique_records_oa.csv'), index=False, encoding='utf-8')
    df_paywall.to_csv(os.path.join(session_folder, 'csv', 'paywall.csv'), index=False, encoding='utf-8')
    df_dup.to_csv(os.path.join(session_folder, 'csv', 'duplicates.csv'), index=False, encoding='utf-8')

    print(f"Exported Excel to: {excel_path}")
    print(f"Exported CSVs to folder: {os.path.join(session_folder, 'csv')}")
    print(f"\n\t\t" + s.cyan + f" Investigation completed. Your reports are in {session_folder}. Thank you for trusting doitective 👣🔍👀💼 Goodbye!")

