"""Cube de calibration avec trou vertical. Valide la chaîne export + contrôles."""

import cadquery as cq

# ---------- Paramètres (mm) ----------
SIZE = 20.0  # côté du cube
HOLE_D = 5.0  # diamètre nominal du trou vertical
HOLE_CLEARANCE = 0.2  # surcote des trous verticaux (ils s'impriment trop petits)
CHAMFER = 0.6  # chanfrein de la face posée sur le plateau (évite la patte d'éléphant)

# ---------- Contrat pour tools/build.py ----------
EXPECTED_BBOX = (SIZE, SIZE, SIZE)
WALLS = {"matière autour du trou": (SIZE - HOLE_D - HOLE_CLEARANCE) / 2}

# ---------- Géométrie ----------
result = (
    cq.Workplane("XY")
    .box(SIZE, SIZE, SIZE, centered=(True, True, False))
    .faces("<Z")
    .edges()
    .chamfer(CHAMFER)
    .faces(">Z")
    .workplane()
    .hole(HOLE_D + HOLE_CLEARANCE)
)
