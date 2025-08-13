# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""




## CURRENTLY NOT IN USE ##











#log_machine


def export_classification_report(output_path, openalex_stack, dois_batch, pmids_batch, titles_batch, not_articles):
    from datetime import datetime

    total = sum(map(len, [openalex_stack, dois_batch, pmids_batch, titles_batch, not_articles]))
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = [
        f"📄 Classification Report — {now}",
        "=" * 60,
        f"🟢 OpenAlex enriched records:  {len(openalex_stack)}",
        f"🔵 DOI-based batch:           {len(dois_batch)}",
        f"🟠 PMID-based batch:          {len(pmids_batch)}",
        f"🟣 Title-based batch:         {len(titles_batch)}",
        f"🔴 Not articles / no ID:      {len(not_articles)}",
        "-" * 60,
        f"📊 Total records processed:   {total}",
        "",
        "🔎 Sample Titles:",
    ]

    def get_title(entry): return entry.get("Title") or entry.get("DocumentTitle") or "—"

    for group_name, group in [
        ("OpenAlex", openalex_stack),
        ("DOIs", dois_batch),
        ("PMIDs", pmids_batch),
        ("Titles", titles_batch),
        ("Not Articles", not_articles)
    ]:
        lines.append(f"\n[{group_name}] — {len(group)} entries")
        for entry in group[:3]:
            lines.append("  • " + get_title(entry))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
