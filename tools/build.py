"""Exporte, contrôle, prévisualise et versionne une pièce CadQuery.

Usage : uv run tools/build.py models/<nom>/<nom>.py

Le fichier de pièce doit exposer :
  result         solide CadQuery (cq.Workplane)
  EXPECTED_BBOX  (x, y, z) en mm, dimensions demandées
  WALLS          {"nom": épaisseur_mm} pour chaque paroi fonctionnelle
"""

import runpy
import shutil
import sys
from pathlib import Path

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BUILD_VOLUME = (256.0, 256.0, 256.0)  # Bambu A1, mm
from printer import MIN_WALL  # dépend de la buse : tools/printer.py
BBOX_TOL = 0.01  # mm
EXPORTS = (".stl", ".step", ".3mf")


def check(part, mesh):
    """Retourne la liste des contrôles échoués (vide = tout passe)."""
    errors = []
    if not part["result"].val().isValid():
        errors.append("solide invalide (isValid)")
    if not mesh.is_watertight:
        errors.append("maillage non fermé (non watertight)")

    size = mesh.extents
    for axis, got, limit in zip("XYZ", size, BUILD_VOLUME):
        if got > limit:
            errors.append(f"{axis} = {got:.2f} mm dépasse le volume utile ({limit} mm)")
    for axis, got, want in zip("XYZ", size, part["EXPECTED_BBOX"]):
        if abs(got - want) > BBOX_TOL:
            errors.append(f"{axis} = {got:.2f} mm, attendu {want:.2f} mm")

    # shortcut: contrôle les parois déclarées, pas l'épaisseur réelle du solide ;
    # passer à une mesure par lancer de rayons si une pièce a des parois non paramétrées.
    for name, thickness in part["WALLS"].items():
        if thickness < MIN_WALL:
            errors.append(f"paroi « {name} » = {thickness:.2f} mm < {MIN_WALL} mm")
    return errors


def preview(mesh, png):
    """Vues iso + dessus."""
    normals = mesh.face_normals
    light = np.array([0.4, -0.5, 0.75])
    shade = 0.35 + 0.65 * np.clip(normals @ (light / np.linalg.norm(light)), 0, 1)
    colors = np.outer(shade, [0.35, 0.6, 0.9])

    fig = plt.figure(figsize=(12, 6))
    for i, (title, elev, azim) in enumerate([("Iso", 30, -60), ("Dessus", 90, -90)]):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=colors))
        lo, hi = mesh.bounds
        ax.set_xlim(lo[0], hi[0]), ax.set_ylim(lo[1], hi[1]), ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect(tuple(mesh.extents))
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X"), ax.set_ylabel("Y"), ax.set_zlabel("Z")
        ax.set_title(title)
    fig.suptitle("{} — {:.1f} x {:.1f} x {:.1f} mm".format(png.stem, *mesh.extents))
    fig.savefig(png, dpi=110, bbox_inches="tight")
    plt.close(fig)


def snapshot(script):
    """Copie script + exports en _vN. Même script que la dernière version = même N."""
    stem, folder = script.stem, script.parent
    numbers = sorted(
        int(p.stem.rsplit("_v", 1)[1])
        for p in folder.glob(f"{stem}_v*.py")
        if p.stem.rsplit("_v", 1)[1].isdigit()
    )
    n = numbers[-1] if numbers else 0
    if n == 0 or (folder / f"{stem}_v{n}.py").read_bytes() != script.read_bytes():
        n += 1
    for ext in (".py", ".png", *EXPORTS):
        shutil.copyfile(folder / f"{stem}{ext}", folder / f"{stem}_v{n}{ext}")
    return n


def main():
    script = Path(sys.argv[1]).resolve()
    part = runpy.run_path(str(script))
    base = script.with_suffix("")

    for ext in EXPORTS:
        cq.exporters.export(part["result"], f"{base}{ext}")
    mesh = trimesh.load_mesh(f"{base}.stl")

    errors = check(part, mesh)
    if errors:
        print("ÉCHEC :")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    preview(mesh, base.with_suffix(".png"))
    n = snapshot(script)
    print("OK   {:.2f} x {:.2f} x {:.2f} mm, volume {:.0f} mm3".format(*mesh.extents, mesh.volume))
    print(f"     version v{n} : {script.parent}")


if __name__ == "__main__":
    main()
