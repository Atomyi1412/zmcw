# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import sys
try:
    import bcrypt as _bcrypt_pkg
except Exception:
    _bcrypt_pkg = None

# Platform-specific icon handling
if sys.platform == 'darwin':
    EXE_ICON = 'assets/app.icns'
    BUNDLE_ICON = 'assets/app.icns'
elif sys.platform == 'win32':
    EXE_ICON = 'assets/app.ico'
    BUNDLE_ICON = None
else:
    EXE_ICON = None
    BUNDLE_ICON = None

# bcrypt binary extension name per platform
_bcrypt_ext = None
if _bcrypt_pkg:
    base_dir = os.path.dirname(_bcrypt_pkg.__file__)
    if sys.platform == 'win32':
        cand = os.path.join(base_dir, '_bcrypt.abi3.pyd')
        if os.path.exists(cand):
            _bcrypt_ext = (cand, 'bcrypt')
    else:
        cand = os.path.join(base_dir, '_bcrypt.abi3.so')
        if os.path.exists(cand):
            _bcrypt_ext = (cand, 'bcrypt')

extra_datas = [('assets', 'assets')] + (collect_data_files('bcrypt') if True else [])
if _bcrypt_ext:
    extra_datas.append(_bcrypt_ext)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=extra_datas,
    hiddenimports=collect_submodules('bcrypt') + ['user_auth'],
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
    [],
    exclude_binaries=True,
    name='DesktopPet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[EXE_ICON] if EXE_ICON else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DesktopPet',
)
# Create .app bundle only on macOS
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='DesktopPet.app',
        icon=BUNDLE_ICON,
        bundle_identifier='com.desktoppet.app',
        info_plist={
            'LSUIElement': True,
            'CFBundleName': 'DesktopPet',
            'CFBundleDisplayName': '桌面宠物',
            'CFBundleVersion': '1.4.2',
            'CFBundleShortVersionString': '1.4.2',
            'NSHighResolutionCapable': True,
            'NSSupportsAutomaticGraphicsSwitching': True,
        },
    )
