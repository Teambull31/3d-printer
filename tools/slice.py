"""Tranche un STL pour la Bambu A1 avec Bambu Studio (Flatpak) en ligne de commande.

Usage : uv run tools/slice.py models/<nom>/<nom>.stl
Sortie : <nom>.gcode.3mf à côté du STL, prêt à valider puis à envoyer à l'imprimante.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FLATPAK_APP = "com.bambulab.BambuStudio"
PROFILES = Path.home() / ".local/share/flatpak/app" / FLATPAK_APP / "current/active/files/share/BambuStudio/profiles/BBL"
from printer import FILAMENT, MACHINE, PROCESS  # buse et profils : tools/printer.py

BED_TYPE = "Textured PEI Plate"  # plateau livré avec l'A1 ; "Cool Plate" = 35 °C au lieu de 65 °C


def flatten(kind, name):
    """Profil complet : parents (« inherits ») puis inclusions (« include ») puis le profil lui-même.

    Le CLI de Bambu Studio ne résout pas l'héritage : un profil système passé tel quel
    tranche avec les valeurs génériques (couche 0.2, G-code de démarrage non A1).
    """
    own = json.loads((PROFILES / kind / f"{name}.json").read_text())
    merged = flatten(kind, own["inherits"]) if own.get("inherits") else {}
    for included in own.get("include", []):
        merged |= flatten(kind, included)
    merged |= own
    merged.pop("inherits", None), merged.pop("include", None)
    return merged


def main():
    stl = Path(sys.argv[1]).resolve()
    # Le Flatpak ne voit que le dossier personnel : /tmp lui est invisible.
    if not stl.is_file() or not stl.is_relative_to(Path.home()):
        sys.exit(f"ÉCHEC : {stl} doit exister et se trouver sous {Path.home()}")
    name = f"{stl.stem}.gcode.3mf"

    with tempfile.TemporaryDirectory(dir=stl.parent) as tmp:
        for kind, profile in (("machine", MACHINE), ("process", PROCESS), ("filament", FILAMENT)):
            Path(tmp, f"{kind}.json").write_text(json.dumps(flatten(kind, profile)))
        run = subprocess.run(
            [
                "flatpak", "run", "--user", "--command=bambu-studio", FLATPAK_APP,
                "--slice", "0", "--arrange", "1",
                "--curr-bed-type", BED_TYPE,
                "--load-settings", f"{tmp}/machine.json;{tmp}/process.json",
                "--load-filaments", f"{tmp}/filament.json",
                "--outputdir", tmp, "--export-3mf", name, str(stl),
            ],
            capture_output=True, text=True,
        )
        report = Path(tmp, "result.json")
        result = json.loads(report.read_text()) if report.exists() else {}
        if run.returncode or result.get("return_code") != 0 or not Path(tmp, name).exists():
            sys.exit(f"ÉCHEC : {result.get('error_string') or run.stdout[-800:] + run.stderr[-800:]}")
        shutil.move(Path(tmp, name), stl.with_name(name))

    plate = result["sliced_plates"][0]
    size = plate["objects"][0]["bbox"]
    print(f"OK   {stl.with_name(name)}")
    print("     {:.1f} x {:.1f} x {:.1f} mm, {:.0f} min, couche {:.2f} mm, remplissage {:.0f} %, {} parois".format(
        size["width"], size["depth"], size["height"], plate["total_predication"] / 60,
        result["layer_height"], result["sparse_infill_density"], result["wall_loops"]))
    print(f"     {MACHINE} | {PROCESS} | {FILAMENT} | {BED_TYPE}")
    if plate["warning_message"]:
        print("     AVERTISSEMENT :", plate["warning_message"])


if __name__ == "__main__":
    main()
