import datetime
import inspect
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import field, dataclass
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


@dataclass
class AppInfo:
    name: str
    version: str
    icon_path: Path
    script_path: Path
    content_root: Path
    company: str = field(default="Andrew Kennedy")

    def copyright(self) -> str:
        return f"Copyright {datetime.datetime.now().year} {self.company}. All rights reserved."


@dataclass
class BuildSettings:
    one_file: bool
    quiet: bool
    debug: bool
    output_folder: Path


def build(app_info: AppInfo, build_settings: BuildSettings) -> int:
    """ Build the application. """
    # Paths
    # The build_path is the folder where the build is run. It gets cleaned up before and after every build.
    build_path = build_settings.output_folder / "build"
    pyinstaller_work_path = build_path / "work"
    pyinstaller_spec_path = build_path / "spec"

    # The dist_path is where the application is built to
    if build_settings.debug:
        dist_path = build_settings.output_folder / "debug"
    else:
        dist_path = build_settings.output_folder / "release"

    # Validation
    _validate_os()
    _validate_icon(app_info.icon_path)
    _validate_content(app_info.content_root)

    # Clean paths
    shutil.rmtree(build_path, ignore_errors=True)
    shutil.rmtree(dist_path, ignore_errors=True)

    # Create paths
    build_settings.output_folder.mkdir(parents=True, exist_ok=True)
    build_path.mkdir(parents=True, exist_ok=True)

    # Write icon file
    icon_file = build_path / "icon.ico"
    _write_icon_file(src=app_info.icon_path, dst=icon_file)

    # Write license file
    license_file = build_path / "LICENSE"
    with license_file.open('w') as fp:
        fp.write(app_info.copyright())

    # Write version file
    version_file = build_path / "version-file.py"
    _write_version_file(version_file, app_info)

    # Zip content
    content_zip = build_path / "content"
    _zip_content(app_info.content_root, content_zip)

    # Create build command
    cmd = ["pyinstaller"]
    cmd += ["--specpath", pyinstaller_spec_path.as_posix()]
    cmd += ["--workpath", pyinstaller_work_path.as_posix()]
    cmd += ["--distpath", dist_path.as_posix()]
    cmd += ["--name", app_info.name]
    cmd += ["--icon", icon_file.as_posix()]
    cmd += ["--version-file", version_file.as_posix()]
    cmd += ["--add-data", f"{license_file.as_posix()}{os.pathsep}."]
    cmd += ["--add-data", f"{content_zip.as_posix()}{os.pathsep}."]

    if build_settings.one_file:
        cmd += ["--onefile"]
    else:
        cmd += ["--onedir"]
        cmd += ["--contents-directory", "data"]

    if not build_settings.debug:
        cmd += ["--noconsole"]

    cmd += ["--collect-binaries", "sdl2dll"]
    cmd += ["--collect-data", "sdl2dll"]

    cmd += [app_info.script_path.as_posix()]

    # Build
    if build_settings.quiet:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    else:
        stdout = sys.stdout
        stderr = sys.stderr

    env = os.environ.copy()
    if build_settings.debug:
        env['PYTHONOPTIMIZE'] = "0"
    else:
        env['PYTHONOPTIMIZE'] = "2"

    proc = subprocess.Popen(cmd, env=env, stdout=stdout, stderr=stderr)
    proc.communicate()

    # Clean paths
    shutil.rmtree(build_path, ignore_errors=True)

    return proc.returncode


def _validate_os() -> None:
    """ Validate the operating system. """
    if platform.system() == "Windows":
        pass
    else:
        raise NotImplementedError(f"{platform.system()} is not a supported system")


def _validate_icon(icon_path: Path) -> None:
    """ Validate that the icon is in the correct format. """
    if not icon_path.suffix.lower() == ".png":
        raise RuntimeError(f"Icon '{icon_path.name}' must be a PNG file")

    with Image.open(icon_path) as im:
        if im.size != (256, 256):
            raise RuntimeError(f"Icon '{icon_path.name}' size must be 256x256 ({im.size[0]}x{im.size[1]} detected)")


def _validate_content(content_path: Path) -> None:
    """ Validate that the content root exists. """
    if not content_path.is_dir():
        raise FileNotFoundError(content_path.as_posix())


def _write_icon_file(src: Path, dst: Path) -> None:
    """ Write the icon file to the build folder. """
    image = Image.open(src)
    sizes = [
        (256, 256),
        (96, 96),
        (80, 80),
        (72, 72),
        (64, 64),
        (60, 60),
        (48, 48),
        (40, 40),
        (36, 36),
        (32, 32),
        (30, 30),
        (24, 24),
        (20, 20),
        (16, 16),
    ]
    image.save(dst, sizes=sizes)


def _write_version_file(file_path: Path, app_info: AppInfo) -> None:
    """ Write a Windows version resource file. """
    version_file_str = f"""
    VSVersionInfo(
      ffi=FixedFileInfo(
        filevers=(0, 0, 0, 0),
        prodvers=(0, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
        ),
      kids=[
        VarFileInfo([VarStruct('Translation', [0, 1200])]), 
        StringFileInfo(
          [StringTable(
            '000004b0',
            [
                StringStruct('CompanyName', '{app_info.company}'),
                StringStruct('FileDescription', '{app_info.name}'),
                StringStruct('FileVersion', '{app_info.version}'),
                StringStruct('InternalName', '{app_info.name}.exe'),
                StringStruct('LegalCopyright', '{app_info.copyright()}'),
                StringStruct('OriginalFilename', '{app_info.name}.exe'),
                StringStruct('ProductName', '{app_info.name}'),
                StringStruct('ProductVersion', '{app_info.version}'),
            ])
        ])
      ]
    )
    """

    # Clean up indents
    version_file_str = inspect.cleandoc(version_file_str)

    # Write file
    with file_path.open('w') as fp:
        fp.write(version_file_str)


def _zip_content(src: Path, dst: Path) -> None:
    """ Zip the content root to a file. """
    files_to_zip = []
    for root, dirs, files in src.walk():
        for f in files:
            files_to_zip.append(root / f)

    with ZipFile(dst, 'w') as zf:
        for file in files_to_zip:
            zf.write(file, arcname=file.relative_to(src))
