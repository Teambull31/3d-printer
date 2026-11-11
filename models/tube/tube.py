"""Tube droit, imprimé debout (axe du trou vertical)."""

import cadquery as cq

# ---------- Paramètres (mm) ----------
OUTER_D = 13.0  # diamètre extérieur
HOLE_D = 6.5  # diamètre nominal du trou
LENGTH = 76.0  # longueur du tube
HOLE_CLEARANCE = 0.2  # surcote du trou vertical (il s'imprime trop petit)
CHAMFER = 0.4  # chanfrein extérieur de la face posée sur le plateau (évite la patte d'éléphant)

# ---------- Contrat pour tools/build.py ----------
EXPECTED_BBOX = (OUTER_D, OUTER_D, LENGTH)
WALLS = {"paroi du tube": (OUTER_D - HOLE_D - HOLE_CLEARANCE) / 2}

# ---------- Géométrie ----------
result = (
    cq.Workplane("XY")
    .circle(OUTER_D / 2)
    .extrude(LENGTH)
    .faces("<Z")
    .edges()
    .chamfer(CHAMFER)
    .faces(">Z")
    .workplane()
    .hole(HOLE_D + HOLE_CLEARANCE)
)
