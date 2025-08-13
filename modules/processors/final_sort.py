# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
#fina_sort.py
import pandas as pd
import os
from pathlib import Path

def summarize_grouped_excel_to_txt(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
    
    # Leer todas las hojas
    xls = pd.ExcelFile(filepath)
    summary_lines = []

    summary_lines.append(f"Resumen de registros por hoja\nArchivo: {os.path.basename(filepath)}\n")
    summary_lines.append("=" * 60)

    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            count = len(df)
            summary_lines.append(f"{sheet_name}: {count} registros")
        except Exception as e:
            summary_lines.append(f"{sheet_name}: ERROR ({e})")

    summary_text = "\n".join(summary_lines)

    # Generar path para guardar el .txt en el mismo directorio
    output_txt = os.path.join(
        os.path.dirname(filepath),
        "SUMMARY_" + os.path.basename(filepath).replace(".xlsx", ".txt")
    )

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"📄 Resumen guardado en: {output_txt}")


def summarize_grouped_excel_to_txt(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
    
    xls = pd.ExcelFile(filepath)
    summary_lines = []

    summary_lines.append(f"Resumen de registros por hoja\nArchivo: {os.path.basename(filepath)}\n")
    summary_lines.append("=" * 60)

    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            count = len(df)
            summary_lines.append(f"{sheet_name}: {count} registros")
        except Exception as e:
            summary_lines.append(f"{sheet_name}: ERROR ({e})")

    summary_text = "\n".join(summary_lines)

    output_txt = os.path.join(
        os.path.dirname(filepath),
        "SUMMARY_" + os.path.basename(filepath).replace(".xlsx", ".txt")
    )

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"📄 Resumen guardado en: {output_txt}")


import pandas as pd
import os
from pathlib import Path

import pandas as pd
import os
from pathlib import Path

def classify_records_from_marked_sheets(input_path):
    """
    Procesa hojas con nombre entre llaves {...} de archivos Excel en un directorio o archivo individual.
    Clasifica los registros según el primer criterio fallido y guarda un Excel + resumen .txt.
    """
    if os.path.isdir(input_path):
        excel_files = list(Path(input_path).glob("*.xlsx"))
        for file in excel_files:
            classify_records_from_marked_sheets(file)
        return

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"No se encontró el archivo: {input_path}")

    xls = pd.ExcelFile(input_path)
    target_sheets = [s for s in xls.sheet_names if s.startswith('{') and s.endswith('}')]
    if not target_sheets:
        raise ValueError("No se encontraron hojas con nombres entre llaves (ej: {unique_oa})")
        

    print(f"🔎 Hojas detectadas: {target_sheets}")

    all_rows = []
    for sheet in target_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        df['Source Sheet'] = sheet
        all_rows.append(df)

    df = pd.concat(all_rows, ignore_index=True)

    # Detectar límites de criterios
    headers = df.columns.tolist()
    try:
        i_start = headers.index('{')
        i_end = headers.index('}')
    except ValueError:
        raise ValueError("No se encontraron columnas delimitadoras '{' y '}'")

    criteria = headers[i_start + 1: i_end]
    num_criteria = len(criteria)

    # Inicializar grupos
    groups = {f"{i+1:02d}_{label}": [] for i, label in enumerate(criteria)}
    groups[f"{num_criteria+1:02d}_PASS_ALL"] = []

    def is_failure(val):
        if pd.isna(val):
            return True
        if isinstance(val, (int, float)) and val == 0:
            return True
        val_str = str(val).strip().lower()
        return val_str in ('', '0', 'false')

    # Clasificación
    for _, row in df.iterrows():
        for i, col in enumerate(criteria):
            if is_failure(row[col]):
                row_copy = row.copy()
                row_copy['Failed Criterion'] = col
                groups[f"{i+1:02d}_{col}"].append(row_copy)
                break
        else:
            row_copy = row.copy()
            row_copy['Failed Criterion'] = ''
            groups[f"{num_criteria+1:02d}_PASS_ALL"].append(row_copy)

    # Guardar Excel
    dirpath, fname = os.path.split(input_path)
    base, _ = os.path.splitext(fname)
    out_path = os.path.join(dirpath, f"DOITECTIVE_FINAL_{base}.xlsx")

    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        for sheet_name, rows in groups.items():
            pd.DataFrame(rows).to_excel(writer, sheet_name=sheet_name[:31], index=False)

    print(f"✅ Clasificación completada: {out_path}")

    # Crear resumen .txt
    summary_path = os.path.join(dirpath, f"SUMMARY_DOITECTIVE_FINAL_{base}.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Resumen de registros clasificados\nArchivo: {os.path.basename(out_path)}\n")
        f.write("=" * 60 + "\n")
        for sheet_name, rows in groups.items():
            label = sheet_name.split('_', 1)[1]
            f.write(f"{label} (n={len(rows)})\n")

    print(f"📄 Resumen guardado en: {summary_path}")


    