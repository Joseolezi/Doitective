# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
#texts.py
import utils.style.styles as s
from modules.users.users import get_user_language

localized_texts = {
    "en": {
        "welcome": " " + s.success + "👣 Welcome to Doitective 🔍👀  " + s.version + " by " + s.author + "  \n",
        "license_info": s.info + "» This project is " + s.success + "open source " + s.info + "under the " + s.success + "mit license ",
        "contribution": s.info + "» Feel free to contribute " + s.magenta + "joseolezi.github.io/code" + " 🚀 \n",
        "email_suggestion": s.dim_white + "You can use your e-mail adress to get the best " + s.success + "Doitective and OAPI " + s.info + "performance and support " + s.error + "❤",
        "intro_summary": s.success + " Doitective " + s.dim_white + "will examine all supported files within the"  + s.magenta + "📂[__RAW_DATA__ ]📂 folder 🔍👀\n",
        "step_1": s.success + "» 1 » " + s.dim_white + "Merge all records and " + s.subtitle + "deduplicate " + s.dim_white + "them 🧦",
        "step_2a": s.success + "» 2 » " + s.dim_white + "Batch call weak records to " + s.subtitle + "OpenAlex API [OAPI] " + s.dim_white + "to get the most updated and complete information of each  📚",
        "step_2b": s.success + "» 2 » " + s.subtitle + "Find the best OA option and URL " + s.dim_white + "for each publication, scanning all OAPI open access fields and pdf urls by tier",
        "step_3": s.success + "» 3 » " + s.dim_white + "Screens " + s.success + "🧠 Open Access " + s.dim_white + "from " + s.error + "💸 Restricted access " + s.dim_white + "records and outputs a 3 sheet .xlsx file and 3 .csv files: ↲",
        "output_oa": "    " + s.success + "🧠 Unique_Open_Access (Diamond, Gold, Green)",
        "output_paywall": "    " + s.error + "💸 Unique_Restricted_Access (Hybrid, Bronze, Closed)",
        "output_duplicates": "    " + s.info + "🧦 Duplicated records ",
        "prompt_start": "\n" + s.success + ">>>>> " + s.dim_white + "Enter any key to start using Doitective " + s.success + "➤  ",
        "invalid_input": s.error + "✘ Invalid input. Please try again. ✘",
        "instructions_title": "\t" + s.highlight + " 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 ",
        "instructions_1": s.success + "» 1 » " + s.dim_white + "Place all the files you want to screen inside the folder: " + s.magenta + "📂[__RAW_DATA__ ]📂 🔍👀",
        "formats_supported": s.success + "     ✓ " + s.dim_white + "Supported file formats: " + s.success + ".csv .xls .xlxs \n",
        "known_databases": s.success + "     ✓ " + s.dim_white + "Known databases: " + s.success + "⭐ EBSCO ⭐ PubMed ⭐ Scopus ⭐ World of Sience ⭐ PsyNet ⭐ Cochrane ⭐\n",
        "doi_field_note": s.success + "     ✓ " + s.dim_white + "Doitective only needs the file to have one header named " + s.warning + "'DOI' with valid field values to work at its best 🎯 ",
        "mailto_tip": s.success + "» 2 » " + s.success + "For the best performance, type your email in the .txt file named 'mailto'. You can also create a new one, name it 'mailto' and type your email in",
        "check_output": s.success + "» 3 » " + s.dim_white + "Check the " + s.success + "📂[__SCREENED_DATA__]📂 " + s.dim_white + "folder to find your screened data once Doitective is done processing 🔍👀\n",
        "warning_raw_data": s.warning + " ! " + s.error + "WARNING: " + s.warning + "Make sure all the files with the data you want to merge are " + s.info + "INSIDE THE FOLDER " + s.magenta + "📂[__ RAW_DATA__]📂",
        "reminder_email": s.dim_white + " 💠 " + s.info + "REMEMBER: " + s.dim_white + "You may use your e-mail adress to get the best " + s.success + "Doitective and OAPI performance and show support " + s.error + "❤",
        "start_command": s.warning + "\t>>>> [start] ➤  " + s.dim_white + "Launch the screener",
        "exit_command": s.error + "\t>>>>  [exit] ➤  " + s.dim_white + "Quit and close console \n",
        "prompt_command": s.success + ">>>>> " + s.dim_white + "Enter your command here " + s.success + "➤  ",
        "processing_files": "Processing your files...👀",
        "exiting": "Exiting Doitective 👣🔍👀💼 Goodbye!",
        "error_start_exit": s.error + "✘ Invalid input. Please type 'start' to begin or 'exit' to quit. ✘",
        "loading_files": s.magenta + "Loading and validating files 📂 \n\n",
        "file_read": s.success + "✔ " + s.dim_white + "File loaded successfully: " + s.success + "{file}",
        "origin_detected": s.error + "📌 Detected origin: {origin} — {file}",
        "total_records": s.dim_white + "Total records identified: " + s.success + "{count}",
        "unique_records": s.success + " ✔ {count} Unique records identified",
        "duplicates_found": s.error + "🧦 {count} Duplicated records identified \n",
        "openalex_count": s.magenta + "OpenAlex native records: " + s.success + "{count}",
        "weak_records": s.info + "Weak records: " + s.error + "{count}",
        "enriching_records": s.dim_white + "Enriching " + s.warning + "{count}" + s.dim_white + " weak records with OpenAlex ⚡",
        "enrichment_complete": s.warning + "\r📀 Enrichment completed! " + s.dim_white + "Report: " + s.success + "{enriched}" + s.magenta + "/" + s.info + "{total}" + s.dim_white + " records enriched in " + s.error + "{calls} calls 📞",
        "spinner_progress": s.info + "\r{spinner} Enriched: {enriched} | " + s.error + "📞 API Calls: {calls} ",
        "retry_attempt": "[Attempt {attempt}/{max}]❗ Error fetching batch DOIs ({count}): {error}",
        "waiting_retry": "Waiting {seconds}s before retrying... ⏳",
        "max_retries": "Max retries reached, batch failed 😢",
        "splitting_batches": "Dividing failed batch of {count} into sub-batches of {size}",
        "sub_batch_failed": "Sub-batch of size {size} failed permanently.",
        "invalid_file_ext": "invalid_extension: {ext} in file {file}",
        "file_processing_error": s.error + "❌ Failed to process {file}: {error}",
        "records_parsed": s.success + "📦 Total OpenAlex records parsed from {file}: {count}",
        "file_columns": s.info + "📄 Columns in {file}: {columns}",
        "exported_excel": "Exported Excel to: {path}",
        "exported_csv": "Exported CSVs to folder: {folder}",
        "session_end": "\n\t\t" + s.cyan + " Investigation completed. Your reports are in {folder}. Thank you for trusting doitective 👣🔍👀💼 Goodbye!",
        "start_message": "📂 Scanning input folder and initializing Doitective...",
        "no_valid_files": "⚠️  No valid files found in the input folder.",
        "error_reading_file": "❌ Error reading {file}: {error}",
        "no_data_parsed": "🚫 No records were successfully parsed or normalized.",
        "finished": "\n✅ Processing complete! Results have been exported."
    },
    "es": {
        "welcome": " " + s.success + "👣 Bienvenido a Doitective 🔍👀  " + s.version + " por " + s.author + "  \n",
        "license_info": s.info + "» Este proyecto es " + s.success + "código abierto " + s.info + "bajo la licencia " + s.success + "MIT",
        "contribution": s.info + "» Puedes contribuir en " + s.magenta + "joseolezi.github.io/code" + " 🚀 \n",
        "email_suggestion": s.dim_white + "Puedes usar tu dirección de correo electrónico para obtener el mejor " + s.success + "rendimiento y soporte de Doitective y OAPI " + s.error + "❤",
        "intro_summary": s.success + " Doitective " + s.dim_white + "examinará todos los archivos compatibles dentro de la carpeta"  + s.magenta + "📂[__RAW_DATA__ ]📂 🔍👀\n",
        "step_1": s.success + "» 1 » " + s.dim_white + "Unifica todos los registros y " + s.subtitle + "elimina duplicados " + s.dim_white + "🧦",
        "step_2a": s.success + "» 2 » " + s.dim_white + "Consulta por lotes los registros débiles en " + s.subtitle + "OpenAlex API [OAPI] " + s.dim_white + "para obtener información actualizada y completa de cada uno 📚",
        "step_2b": s.success + "» 2 » " + s.subtitle + "Busca la mejor opción de acceso abierto y URL " + s.dim_white + "para cada publicación, analizando todos los campos de acceso abierto y URLs PDF de OAPI por nivel",
        "step_3": s.success + "» 3 » " + s.dim_white + "Filtra los registros con " + s.success + "🧠 Acceso Abierto " + s.dim_white + "de los de " + s.error + "💸 Acceso Restringido " + s.dim_white + "y genera un archivo .xlsx de 3 hojas y 3 archivos .csv: ↲",
        "output_oa": "    " + s.success + "🧠 Unicos_Acceso_Abierto (Diamante, Oro, Verde)",
        "output_paywall": "    " + s.error + "💸 Unicos_Acceso_Restringido (Híbrido, Bronce, Cerrado)",
        "output_duplicates": "    " + s.info + "🧦 Registros duplicados ",
        "prompt_start": "\n" + s.success + ">>>>> " + s.dim_white + "Pulsa cualquier tecla para comenzar a usar Doitective " + s.success + "➤  ",
        "invalid_input": s.error + "✘ Entrada no válida. Inténtalo de nuevo. ✘",
        "instructions_title": "\t" + s.highlight + " 📄 INSTRUCCIONES 📄 INSTRUCCIONES 📄 INSTRUCCIONES 📄 INSTRUCCIONES 📄 INSTRUCCIONES 📄 ",
        "instructions_1": s.success + "» 1 » " + s.dim_white + "Coloca todos los archivos que quieras analizar dentro de la carpeta: " + s.magenta + "📂[__RAW_DATA__ ]📂 🔍👀",
        "formats_supported": s.success + "     ✓ " + s.dim_white + "Formatos de archivo compatibles: " + s.success + ".csv .xls .xlsx \n",
        "known_databases": s.success + "     ✓ " + s.dim_white + "Bases de datos conocidas: " + s.success + "⭐ EBSCO ⭐ PubMed ⭐ Scopus ⭐ World of Science ⭐ PsyNet ⭐ Cochrane ⭐\n",
        "doi_field_note": s.success + "     ✓ " + s.dim_white + "Doitective solo necesita que el archivo tenga una cabecera llamada " + s.warning + "'DOI' con valores válidos para funcionar correctamente 🎯 ",
        "mailto_tip": s.success + "» 2 » " + s.success + "Para un mejor rendimiento, escribe tu correo en el archivo .txt llamado 'mailto'. También puedes crear uno nuevo con ese nombre e introducir tu email",
        "check_output": s.success + "» 3 » " + s.dim_white + "Revisa la carpeta " + s.success + "📂[__SCREENED_DATA__]📂 " + s.dim_white + "para encontrar tus resultados una vez termine Doitective 🔍👀\n",
        "warning_raw_data": s.warning + " ! " + s.error + "AVISO: " + s.warning + "Asegúrate de que todos los archivos que deseas combinar estén " + s.info + "DENTRO DE LA CARPETA " + s.magenta + "📂[__RAW_DATA__]📂",
        "reminder_email": s.dim_white + " 💠 " + s.info + "RECUERDA: " + s.dim_white + "Puedes usar tu dirección de correo para obtener el mejor rendimiento de Doitective y OAPI y mostrar tu apoyo " + s.error + "❤",
        "start_command": s.warning + "\t>>>> [start] ➤  " + s.dim_white + "Iniciar el análisis",
        "exit_command": s.error + "\t>>>>  [exit] ➤  " + s.dim_white + "Salir y cerrar la consola \n",
        "prompt_command": s.success + ">>>>> " + s.dim_white + "Introduce tu comando aquí " + s.success + "➤  ",
        "processing_files": "Procesando tus archivos...👀",
        "exiting": "Saliendo de Doitective 👣🔍👀💼 ¡Hasta pronto!",
        "error_start_exit": s.error + "✘ Entrada no válida. Escribe 'start' para comenzar o 'exit' para salir. ✘",
        "loading_files": s.magenta + "Cargando y validando archivos 📂 \n\n",
        "file_read": s.success + "✔ " + s.dim_white + "Archivo cargado correctamente: " + s.success + "{file}",
        "origin_detected": s.error + "📌 Origen detectado: {origin} — {file}",
        "total_records": s.info + "Registros totales identificados: " + s.magenta + "{count}",
        "unique_records": s.success + " ✔ {count} registros únicos identificados",
        "duplicates_found": s.error + "🧦 {count} registros duplicados identificados \n",
        "openalex_count": s.magenta + "Registros nativos de OpenAlex: " + s.success + "{count}",
        "weak_records": s.info + "Registros débiles: " + s.error + "{count}",
        "enriching_records": s.dim_white + "Enriqueciendo " + s.warning + "{count}" + s.dim_white + " registros débiles con OpenAlex ⚡",
        "enrichment_complete": s.warning + "\r📀 ¡Enriquecimiento completado! " + s.dim_white + "Informe: " + s.success + "{enriched}" + s.magenta + "/" + s.info + "{total}" + s.dim_white + " registros enriquecidos en " + s.error + "{calls} llamadas 📞",
        "spinner_progress": s.info + "\r{spinner} Enriquecidos: {enriched} | " + s.error + "📞 Llamadas API: {calls} ",
        "retry_attempt": "[Intento {attempt}/{max}]❗ Error al consultar DOIs ({count}): {error}",
        "waiting_retry": "Esperando {seconds}s antes de reintentar... ⏳",
        "max_retries": "Se alcanzó el número máximo de reintentos, el lote ha fallado 😢",
        "splitting_batches": "Dividiendo lote fallido de {count} en sublotes de {size}",
        "sub_batch_failed": "El sublote de tamaño {size} ha fallado permanentemente.",
        "invalid_file_ext": "extensión inválida: {ext} en el archivo {file}",
        "file_processing_error": s.error + "❌ Error al procesar {file}: {error}",
        "records_parsed": s.success + "📦 Total de registros de OpenAlex procesados desde {file}: {count}",
        "file_columns": s.info + "📄 Columnas en {file}: {columns}",
        "exported_excel": "Excel exportado a: {path}",
        "exported_csv": "CSVs exportados a la carpeta: {folder}",
        "session_end": "\n\t\t" + s.cyan + " Investigación completada. Tus informes están en {folder}. Gracias por confiar en Doitective 👣🔍👀💼 ¡Hasta pronto!",
        "start_message": "📂 Escaneando la carpeta de entrada e inicializando Doitective...",
        "no_valid_files": "⚠️  No se han encontrado archivos válidos en la carpeta de entrada.",
        "error_reading_file": "❌ Error al leer {file}: {error}",
        "no_data_parsed": "🚫 No se han podido procesar o normalizar registros.",
        "finished": "\n✅ ¡Procesamiento completado! Los resultados han sido exportados."
  }
}


def t(key: str, **kwargs) -> str:
    lang = get_user_language()
    try:
        text = localized_texts[lang][key]
    except KeyError:
        # Fallback: inglés o clave sin traducir
        text = localized_texts.get("en", {}).get(key, f"[missing key: {key}]")
    return text.format(**kwargs)