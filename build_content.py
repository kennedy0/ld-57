from pathlib import Path

from bont import generate_bitmap_font
from sprak import SpritePacker


ASSET_ROOT = Path(__file__).parent / "assets"
CONTENT_ROOT = Path(__file__).parent / "content"

packer = SpritePacker()
packer.add_source_folder(ASSET_ROOT / "sprites")
packer.pack(CONTENT_ROOT)

# generate_bitmap_font(ASSET_ROOT / "fonts" / "FONT-NAME.ttf", CONTENT_ROOT / "fonts", 16)
