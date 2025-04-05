from pathlib import Path

from aseprite_reader import AsepriteFile
from bont import generate_bitmap_font
from sprak import SpritePacker


ASSET_ROOT = Path(__file__).parent / "assets"
CONTENT_ROOT = Path(__file__).parent / "content"
LDTK_ENTITIES = Path(__file__).parent / "ldtk_entities"

packer = SpritePacker()
packer.add_source_folder(ASSET_ROOT / "sprites")
packer.pack(CONTENT_ROOT)

for root, dirs, files in ASSET_ROOT.walk():
    for f in files:
        file = root / f
        if file.suffix == ".aseprite":
            ase = AsepriteFile(file)
            dst = (LDTK_ENTITIES / f).with_suffix(".png")
            dst.unlink(missing_ok=True)
            ase.render(ase.frames[0], dst)

# generate_bitmap_font(ASSET_ROOT / "fonts" / "FONT-NAME.ttf", CONTENT_ROOT / "fonts", 16)
