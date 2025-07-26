# loading_indictaor.py

import asyncio
import itertools
import sys
import style as s
class LoadingIndicator:
    def __init__(self):
        self.running = False
        self.message = "Processing"
        self._task = None

    def update_message(self, new_message):
        self.message = new_message

    async def _spinner(self):
        spinner = itertools.cycle(['\t🕛', '\t🕐', '\t🕑', '\t🕒', '\t🕓', '\t🕔', '\t🕕', '\t🕖', '\t🕗', '\t🕘', '\t🕙', '\t🕚'])
        while self.running:
            sys.stdout.write(f"\r{next(spinner)} {self.message}... ")
            sys.stdout.flush()
            await asyncio.sleep(0.3)
        sys.stdout.write("\r✅ Done.                     \n")
        sys.stdout.flush()

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._spinner())

    async def stop(self):
        self.running = False
        if self._task:
            await self._task

N_calls = 0
N_enriched = 0
stop_spinner = False

# Spinner de actividad
async def progress_spinner():
    global N_calls, N_enriched, stop_spinner
    spinner = itertools.cycle(['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚'])
    
    while not stop_spinner:
        symbol = next(spinner)
        sys.stdout.write(
            f"\r{symbol} Enriched records: {N_enriched} | API calls: {N_calls} {symbol} "
        )
        sys.stdout.flush()
        await asyncio.sleep(0.15)

# Simulación de llamadas a la API
async def fetch_batch_simulated(dois):
    global N_calls, N_enriched
    await asyncio.sleep(0.3)  # Simula el tiempo de red
    N_calls += 1
    N_enriched += len(dois)
    return [f"Enriched {d}" for d in dois]

# Función principal que lanza ambos procesos
async def enrich_with_spinner(all_dois):
    spinner_task = asyncio.create_task(progress_spinner())

    # Procesamos por lotes (simulado)
    batch_size = 10
    for i in range(0, len(all_dois), batch_size):
        batch = all_dois[i:i+batch_size]
        await fetch_batch_simulated(batch)

    global stop_spinner
    stop_spinner = True
    await spinner_task  # Esperamos a que acabe el spinner limpio

    print(s.warning + f"\n📀 Enrichment completed!")
