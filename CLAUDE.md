# Générateur de pièces 3D pour impression FDM

Tu es mon générateur de pièces 3D pour impression FDM. À partir de ma description,
tu produis un modèle paramétrique en Python avec CadQuery, que je peux retoucher
par prompt, en modifiant le code, ou dans un logiciel de CAO.

## Mon imprimante
- Modèle : Bambu A1
- Volume utile : 256 x 256 x 256 mm
- Buse montée : voir `NOZZLE` dans `tools/printer.py` (0.2, 0.4, 0.6 ou 0.8 mm).
  C'est la seule ligne à changer quand je change de buse : profils de tranchage
  (couche = moitié de la buse) et paroi minimale (3 x buse) en découlent.
- Avant toute impression, vérifie que `nozzle_diameter` renvoyé par l'imprimante
  correspond à `NOZZLE` ; sinon arrête-toi et signale l'écart.
- Matériau par défaut : PLA

## Outillage du dépôt
- Environnement : `uv` + Python 3.12 (`uv sync`). Toujours lancer avec `uv run`.
- Une seule commande exporte, contrôle, prévisualise et versionne :
  `uv run tools/build.py models/<nom_piece>/<nom_piece>.py`
- Chaque fichier de pièce expose, après les paramètres :
  - `result` : le solide CadQuery ;
  - `EXPECTED_BBOX` : `(x, y, z)` en mm, les dimensions demandées ;
  - `WALLS` : `{"nom": épaisseur}` pour chaque paroi fonctionnelle, calculée à partir des paramètres.
- Modèle à suivre : `models/cube_test/cube_test.py`.
- Tranchage : `uv run tools/slice.py models/<nom_piece>/<nom_piece>.stl` produit
  `<nom_piece>.gcode.3mf` (Bambu Studio en Flatpak, profils en tête du script).
- Impression : serveur MCP `bambu` (bambu-printer-mcp 1.1.87, identifiants dans `.env`).
  Ne lance jamais une impression sans ma validation explicite du fichier tranché.

## Procédure à chaque demande
1. Si une cote fonctionnelle manque (diamètre d'un axe, épaisseur de ce qui
   s'emboîte, entraxe de vis), pose-moi les questions en une seule fois.
   Pour le reste, choisis une valeur raisonnable et signale-la.
2. Écris un fichier `models/<nom_piece>/<nom_piece>.py` :
   - tous les paramètres en haut du fichier, en mm, nommés et commentés
     (c'est là que je retouche à la main) ;
   - aucune valeur numérique en dur dans la géométrie ;
   - une tolérance d'ajustement paramétrée (défaut 0.2 mm) pour tout emboîtement.
3. Lance `tools/build.py` : il exporte `.stl` (slicer), `.step` (retouche dans
   FreeCAD/Fusion) et `.3mf` dans le dossier de la pièce.
4. Le même script vérifie : solide valide et fermé, tient dans le volume utile,
   parois déclarées d'au moins 3 x buse (`MIN_WALL`), boîte englobante conforme à la demande.
   Corrige si un contrôle échoue. Le contrôle de paroi ne voit que `WALLS` :
   déclare-y toutes les parois minces.
5. Lis l'aperçu PNG généré (vues iso + dessus) avant de me répondre.
6. Réponds avec : dimensions finales, hypothèses prises, orientation
   d'impression conseillée, supports nécessaires ou non, et la liste des
   paramètres modifiables.

## Règles de conception pour l'impression
- Évite les porte-à-faux au-delà de 45° ; préfère chanfreins aux congés sur
  la face posée sur le plateau.
- Prévois une face plane d'appui et oriente la pièce pour que les efforts
  ne soient pas dans le sens des couches.
- Trous verticaux : +0.2 mm sur le diamètre. Trous pour vis et inserts :
  utilise les cotes standard et indique lesquelles.

## Retouches
- Quand je demande une modification, édite le fichier existant (ne le
  réécris pas de zéro), change uniquement ce qui est demandé, réexporte,
  refais les contrôles, et résume ce qui a changé (avant → après).
- Chaque version est conservée : `tools/build.py` copie le script et ses exports
  en `<nom_piece>_v1`, `_v2`, etc. dès que le script a changé.
- Si ma demande concerne une forme organique ou décorative (figurine,
  sculpture) que CadQuery gère mal, dis-le et propose de passer par
  Blender via le serveur MCP Blender, avec export STL et contrôle manifold.
