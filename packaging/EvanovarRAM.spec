# -*- mode: python ; coding: utf-8 -*-

import _ssl
from pathlib import Path

from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.win32.winutils import get_windows_dir


PROJECT_ROOT = Path(SPECPATH).resolve().parent
SOURCE_ROOT = PROJECT_ROOT / "src"
ASSETS_ROOT = PROJECT_ROOT / "assets"
VERSION_INFO_PATH = PROJECT_ROOT / "build" / "version_info.txt"
PYTHON_DLLS_ROOT = Path(_ssl.__file__).resolve().parent
WINDOWS_ICU_PATH = Path(get_windows_dir()) / "System32" / "icuuc.dll"

if not VERSION_INFO_PATH.is_file():
    raise FileNotFoundError("Run scripts/build.py to generate version information.")

datas = [
    (str(ASSETS_ROOT / "icon.ico"), "assets"),
    (str(ASSETS_ROOT / "discordlogo.png"), "assets"),
]
# Explicit inputs take precedence over native dependencies discovered on PATH.
binaries = [
    (str(PYTHON_DLLS_ROOT / "libssl-*.dll"), "."),
    (str(PYTHON_DLLS_ROOT / "libcrypto-*.dll"), "."),
    (str(WINDOWS_ICU_PATH), "."),
]
hiddenimports = [
    "requests",
    "Crypto",
    "win32event",
    "win32api",
    "win32crypt",
    "msvcrt",
    "psutil",
    "websockets",
]

# Python modules and Qt files the app never loads. Keeping them out makes the
# one-file exe smaller and faster to start, since it unpacks everything at launch.
# The app drives browsers through WebDriver only: Selenium's DevTools/BiDi
# modules (and trio, which only they import) are never used.
EXCLUDED_MODULES = [
    "selenium.webdriver.common.devtools",
    "selenium.webdriver.common.bidi.cdp",
    "trio", "trio_websocket", "outcome", "sniffio", "sortedcontainers", "wsproto", "h11",
    "cffi", "pycparser", "attr", "attrs",
    "setuptools", "pkg_resources", "_distutils_hack",
    "tkinter", "_tkinter", "pydoc", "pydoc_data", "_pyrepl", "lib2to3",
]
# Destination prefixes, lower case with forward slashes.
EXCLUDED_FILES = (
    "selenium/webdriver/common/macos/",
    "selenium/webdriver/common/linux-",
    "pyside6/translations/",
    "pyside6/opengl32sw.dll",
    "pyside6/plugins/platforminputcontexts/",
    "pyside6/plugins/imageformats/qpdf.dll",
    "pyside6/plugins/imageformats/qicns.dll",
    "pyside6/plugins/imageformats/qtga.dll",
    "pyside6/plugins/imageformats/qwbmp.dll",
    "pyside6/qt6pdf.dll",
    "pyside6/qt6virtualkeyboard.dll",
    "pyside6/qt6quick.dll",
    "pyside6/qt6qml.dll",
    "pyside6/qt6qmlmodels.dll",
    "pyside6/qt6qmlmeta.dll",
    "pyside6/qt6qmlworkerscript.dll",
    "pyside6/qt6opengl.dll",
)


def _is_excluded_module(name):
    return any(name == module or name.startswith(module + ".") for module in EXCLUDED_MODULES)


def _keep_file(entry):
    destination = entry[0].replace("\\", "/").lower()
    return not destination.startswith(EXCLUDED_FILES)


selenium_data, selenium_binaries, selenium_imports = collect_all("selenium")
datas += selenium_data
binaries += selenium_binaries
hiddenimports += [name for name in selenium_imports if not _is_excluded_module(name)]


a = Analysis(
    [str(SOURCE_ROOT / "main.py")],
    pathex=[str(SOURCE_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDED_MODULES,
    noarchive=False,
    optimize=0,
)
a.binaries = [
    entry for entry in a.binaries
    if entry[0].lower() != "icuuc.dll" and _keep_file(entry)
]
a.datas = [entry for entry in a.datas if _keep_file(entry)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PurpleMulti",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(VERSION_INFO_PATH),
    icon=[str(ASSETS_ROOT / "icon.ico")],
)
