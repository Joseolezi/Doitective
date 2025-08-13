# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
common = {
    "input_folder": "[__ RAW_DATA__]",
    "output_folder": "[__SCREENED_DATA__]",
    "language": "en",
    "fields": {
        "Doitective notes": '',
        "doi": "DOI",
        "oa?": 'Open Access?',
        "ti": "Title",
        "yr": "Year",
        "1a": "First author",
        "ob": "Origin database",
        "indexed": "Indexed in",
        "oapi": "OpenAlex API",
        "oa_status": "Open Access status",
        "oa_url": "OA best pdf url",
        "cit_by": "Cited by count",
        "cit%": "Citation normalized percentile",
        "Conc": "Concepts",        
        "issn": "ISSN",
        "authors": "Authors",
        "apa": "APA 7 reference",
        "vol": "Volume",
        "issue": "Issue",
        "pp": "Pages",
        "ab": "Abstract",
    }}

texts = {
    "en": {
        "file_not_found": "File not found: {file}",
        "invalid_extension": "Invalid file extension: {ext}",
        "processing_file": "Processing file: {file}",
        "data_loaded": "Data loaded successfully from {file}",
        "data_normalized": "Data normalized successfully",
        "data_saved": "Data saved to {file}",
        "error_saving_data": "Error saving data to {file}",
        "start_message": "📂 Scanning input folder and initializing Doitective...",
        "no_valid_files": "⚠️  No valid files found in the input folder.",
        "error_reading_file": "❌ Error reading {file}: {error}",
        "no_data_parsed": "🚫 No records were successfully parsed or normalized.",
        "finished": "\n✅ Processing complete! Results have been exported.",
        "enriching_openalex": "Querying OpenAlex data...",
        "invalid_file_format": "Invalid file format: {file}"
    },
    "es": {
        "file_not_found": "Archivo no encontrado: {file}",
        "invalid_extension": "Extensión de archivo no válida: {ext}",
        "processing_file": "Procesando archivo: {file}",
        "data_loaded": "Datos cargados exitosamente desde {file}",
        "data_normalized": "Datos normalizados exitosamente",
        "data_saved": "Datos guardados en {file}",
        "error_saving_data": "Error al guardar los datos en {file}",
        "start_message": "📂 Escaneando la carpeta de entrada e iniciando Doitective...",
        "no_valid_files": "⚠️  No se encontraron archivos válidos en la carpeta de entrada.",
        "error_reading_file": "❌ Error al leer {file}: {error}",
        "no_data_parsed": "🚫 No se pudo analizar ni normalizar ningún registro.",
        "finished": "\n✅ ¡Procesamiento completo! Los resultados han sido exportados.",
        "enriching_openalex": "Consultando datos de OpenAlex...",
        "invalid_file_format": "Formato de archivo no válido: {file}"
    }
    }
