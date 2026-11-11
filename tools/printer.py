"""Buse montée sur la Bambu A1. Seul endroit à modifier quand tu changes de buse."""

NOZZLE = 0.2  # mm : 0.2, 0.4, 0.6 ou 0.8

# Profils Bambu Studio par buse : (procédé, filament). Le profil machine se déduit du diamètre.
PROFILES = {
    0.2: ("0.10mm Standard @BBL A1 0.2 nozzle", "Bambu PLA Basic @BBL A1 0.2 nozzle"),
    0.4: ("0.20mm Standard @BBL A1", "Bambu PLA Basic @BBL A1"),
    0.6: ("0.30mm Standard @BBL A1 0.6 nozzle", "Bambu PLA Basic @BBL A1"),
    0.8: ("0.40mm Standard @BBL A1 0.8 nozzle", "Bambu PLA Basic @BBL A1"),
}

if NOZZLE not in PROFILES:
    raise SystemExit(f"ÉCHEC : buse {NOZZLE} mm inconnue, choix possibles : {sorted(PROFILES)}")

MACHINE = f"Bambu Lab A1 {NOZZLE} nozzle"
PROCESS, FILAMENT = PROFILES[NOZZLE]
MIN_WALL = round(3 * NOZZLE, 2)  # mm, 3 périmètres
