Copyright (c) 2025 Jose Fandos. All Rights Reserved.
## DOITECTIVE 

## STATEMENT
Doitective is a source-available project started by a psychology student as part of his master's degree final project. Please review the license conditions below or in `LICENSE.txt` for details about your rights to use, modify, and distribute Doitective.

## Current state and future
This version is mostly hardcoded and unfinished, as it has been designed to meet very specific needs as quickly as possible. The current commit is a stable build, but a more polished and minimal stable version is planned soon.

## How to use Doitective
Doitective supports `.csv`, `.xls`, and `.xlsx` data input. It is the user's responsibility to follow the guidelines to prevent malfunction.

There are two main modes. You must set the `mode=x` variable in `user_settings.txt` before running Doitective:
- Replace `x` with `1` (sort file data) or `2` (group, deduplicate, enrich, and separate OA, restricted, duplicates, and ineligible entries).
- Optionally, add your email to improve OpenAlex API performance by adding `mailto=youremail@example.com` to `user_settings.txt`.

If the file `user_settings.txt` is missing, you can create one with these lines:
---
mode=x
mailto=youremail@example.com
---

### Mode 1: Sort File Data
**Requirements:**  
Place at least one supported file inside the `_FINAL_SORT_` folder with a header named `{` and another named `}`. Between these, you may include any number of alphanumeric headers.  
If your file is an Excel workbook and you have multiple sheets to include, their names must be alphanumeric and surrounded with `{}`. All files and sheets in the batch must have the same headers in the same order between `{` and `}`.

**Flow:**  
Doitective will:
1. Divide entries into groups based on the headers between `{` and `}` plus one extra group.
2. Output:
   - An `.xlsx` file with a sheet for each group.
   - A `.txt` file summarizing the number of entries per group.
3. Output location: `_FINAL_SORT_`.

---

### Mode 2: Group, Deduplicate, Enrich
**Requirements:**  
Place at least one supported file inside `_RAW_DATA_`.  
Doitective expects each file to have **at least one** of these fields with valid data per entry: DOI, PMID, or title. It is recommended to mark these fields when exporting from databases. Recognized databases include: EBSCOhost, Web of Science, PubMed, Scopus, and PsyNet.

**Flow:**  
Doitective will:
1. Merge entries into a single normalized dataset.
2. Detect and label origin databases.
3. Mark as **ineligible**:
   - Entries with “Not an Article” in the corresponding field.
   - Entries missing DOI, PMID, and title.
4. Identify duplicates and trace “found in”, “indexed in”, “N copies”, and “copied in” fields.
5. Use the OpenAlex API to enrich entries (e.g., best OA PDF URL).
6. Separate OA unique entries from restricted ones.
7. Export:
   - 4 `.csv` files and 1 `.xlsx` file (OA unique, restricted unique, duplicates, ineligible).
8. Output location: `_SCREENED_DATA_`.

## License

This repository is **source-available for evaluation only** under the
*Doitective Source-Available Evaluation-Only License (DSA-EOL) v1.0*.

- Allowed without permission: **viewing/browsing** the code (downloading only as technically required to view it locally).
- Not allowed without prior written permission: **running, compiling, modifying, redistributing, hosting, forking**, academic or commercial use, or any other use beyond viewing/evaluation.
- Explicitly forbidden: use by entities that profit from restricting access to scientific knowledge or that sell access to data/tools without open access to their datasets.

For any permission (personal, academic, or commercial), contact **jose.f2@outlook.es**.  
See full terms in [`LICENSE.txt`](LICENSE.txt).



