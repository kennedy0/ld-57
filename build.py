import subprocess
from pathlib import Path

from potion import pbuild
from potion.utilities.pbuild import AppInfo
from potion.utilities.pbuild import BuildSettings


project_root = Path(__file__).parent
icon = project_root / "icon.png"
builds = project_root / "build"


app_name = "LD57"
script_file = project_root / "main.py"
content_root = project_root / "content"

debug_app_info = AppInfo(
    name=f"{app_name}-debug",
    icon_path=icon,
    script_path=script_file,
    content_root=content_root,
    version="v1",
)

release_app_info = AppInfo(
    name=app_name,
    icon_path=icon,
    script_path=script_file,
    content_root=content_root,
    version="v1",
)

debug_build_settings = BuildSettings(
    one_file=False,
    quiet=True,
    debug=True,
    output_folder=builds,
)

release_build_settings = BuildSettings(
    one_file=False,
    quiet=True,
    debug=False,
    output_folder=builds,
)

print(f"Building {debug_app_info.name}")
pbuild.build(debug_app_info, debug_build_settings)

print(f"Building {release_app_info.name}")
pbuild.build(release_app_info, release_build_settings)

release_build_folder = builds / "release" / app_name
release_zip = builds / f"{app_name}.zip"
cmd = [r"C:\Program Files\7-Zip\7z.exe", "a", "-r", release_zip.as_posix(), f"{release_build_folder.as_posix()}/*"]
proc = subprocess.run(cmd)
