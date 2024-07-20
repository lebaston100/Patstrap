# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='vrc-patpatpat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

import shutil
import os
import logging
logging.info("Copying files and folders into build directory")
isCI = bool(os.getenv("CI"))
serverpath = "server/" if isCI else ""
rootpath = "" if isCI else "../"
shutil.copyfile(f"{serverpath}config.conf", f"{DISTPATH}/config.conf")
shutil.copyfile(f"{serverpath}firewall.bat", f"{DISTPATH}/firewall.bat")
shutil.copyfile(f"{rootpath}README.md", f"{DISTPATH}/README.md")
shutil.copyfile(f"{rootpath}LICENSE", f"{DISTPATH}/LICENSE")
shutil.copytree(f"{rootpath}firmware", f"{DISTPATH}/firmware")
shutil.copytree(f"{rootpath}pcb", f"{DISTPATH}/pcb")
logging.info("Successfully copied all files and folders into build directory")