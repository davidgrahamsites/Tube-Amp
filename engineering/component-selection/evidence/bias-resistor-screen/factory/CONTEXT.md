# Bias resistor screen factory

Input:16 saved bias capacitor decks and the shared ngspice runtime adapter.
Process: `run.py` computes original-case resistor powers and explicit high-source corner decks; zero-voltage initial capacitors use UIC for phase-sensitive turn-on.
Output: sibling `runs/results.json` and `runs/ngspice.log` only.
Human check: compare original16 maxima against prior dossier and inspect source hashes before relying on extended results.
