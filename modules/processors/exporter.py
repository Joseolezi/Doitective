# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# exporter.py
import os
import pandas as pd
import utils.style.styles as s


def export_results(unique_oa, paywall, duplicates, ineligible, fieldnames, session_folder):
    
    # Asegurarse que la carpeta existe
    os.makedirs(os.path.join(session_folder, 'excel'), exist_ok=True)
    os.makedirs(os.path.join(session_folder, 'csv'), exist_ok=True)

    # Rellenar campos faltantes con string vacío
    for entry in unique_oa + paywall + duplicates + ineligible:
        for field in fieldnames:
            entry.setdefault(field, '')

    # Crear DataFrames ordenados por fieldnames
    df_oa = pd.DataFrame(unique_oa, columns=fieldnames)
    df_paywall = pd.DataFrame(paywall, columns=fieldnames)
    df_dup = pd.DataFrame(duplicates, columns=fieldnames)
    df_inel = pd.DataFrame(ineligible, columns=fieldnames)

    # Exportar Excel con 3 hojas
    excel_path = os.path.join(session_folder, 'excel', 'screened_records.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_oa.to_excel(writer, sheet_name='Unique OA Records', index=False)
        df_paywall.to_excel(writer, sheet_name='Unique Restricted Records', index=False)
        df_dup.to_excel(writer, sheet_name='Duplicates', index=False)
        df_inel.to_excel(writer, sheet_name='Ineligible records', index=False)

    # Exportar CSV separados
    df_oa.to_csv(os.path.join(session_folder, 'csv', 'Unique OA Records.csv'), index=False, encoding='utf-8')
    df_paywall.to_csv(os.path.join(session_folder, 'csv', 'Unique Restricted Records.csv'), index=False, encoding='utf-8')
    df_dup.to_csv(os.path.join(session_folder, 'csv', 'Duplicates.csv'), index=False, encoding='utf-8')
    df_inel.to_csv(os.path.join(session_folder, 'csv', 'Ineligible records.csv'), index=False, encoding='utf-8')

    print(f"Exported Excel to: {excel_path}")
    print(f"Exported CSVs to folder: {os.path.join(session_folder, 'csv')}")
    print(f"\n" + s.cyan + f" Work completed. Your reports are in " + s.magenta + f"{session_folder}\n")
    print(f"\t\t" + s.warning + f"💛 Thank you " + s.dim_white + f"for trusting " + s.success + f"Doitective ╭(ಠ︻ಠ)ノ━◯ \n\n\n")

