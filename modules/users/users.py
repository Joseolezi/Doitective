# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
# users.py
import json
from pathlib import Path

memory_folder = Path("user_data")
memory_folder.mkdir(exist_ok=True)
memory_file = memory_folder / "user_memory.json"

def get_user_language() -> str:
    memory = load_user_memory()
    return memory.get("lang", "es")  # por defecto inglés

def save_user_memory(data: dict) -> None:
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_user_memory() -> dict:
    if memory_file.exists():
        with open(memory_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}