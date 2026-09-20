# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the game itself -> build\\dist\\RecklessDriving\\RecklessDriving.exe.

One-folder (not one-file): a one-file build unpacks ~40 MB to a temp folder on every launch,
which is a visible delay for something the player opens to press START RUN. The folder is
zipped into the installer afterwards, so the player never sees it either way.

pywebview's WebView2 interop DLLs and pythonnet are pulled in by the bundled hooks
(hook-webview / hook-clr / hook-clr_loader), so nothing needs listing by hand here.
"""
from pathlib import Path

ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / 'app' / 'main.py')],
    pathex=[str(ROOT / 'app')],
    binaries=[],
    # The game is one self-contained HTML file with the fonts embedded - this single entry is
    # the whole game.
    datas=[(str(ROOT / 'carCrash.html'), '.')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'pytest', 'PIL'],   # used by the installer/tools, never by the game
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RecklessDriving',
    debug=False,
    strip=False,
    upx=False,
    console=False,                            # no console window behind the game
    icon=str(ROOT / 'assets' / 'recklessdriving.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='RecklessDriving',
)
