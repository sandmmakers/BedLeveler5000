block_cipher = None

BedLeveler5000_a = Analysis(
    ['src/BedLeveler5000.py'],
    pathex=[],
    binaries=[],
    datas=[('Printers', 'Printers'),
           ('Resources', 'Resources'),
           ('Third Party', 'Third Party'),
           ('LICENSE', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
BedLeveler5000_pyz = PYZ(BedLeveler5000_a.pure, BedLeveler5000_a.zipped_data, cipher=block_cipher)

BedLeveler5000_exe = EXE(
    BedLeveler5000_pyz,
    BedLeveler5000_a.scripts,
    [],
    exclude_binaries=True,
    name='BedLeveler5000',
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
    icon='Resources/Icon-128x128.png'
)

PrinterInfoWizard_a = Analysis(
    ['src/PrinterInfoWizard.py'],
    pathex=[],
    binaries=[],
    datas=[('Printers', 'Printers'),
           ('Resources', 'Resources'),
           ('Third Party', 'Third Party'),
           ('LICENSE', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
PrinterInfoWizard_pyz = PYZ(PrinterInfoWizard_a.pure, PrinterInfoWizard_a.zipped_data, cipher=block_cipher)

PrinterInfoWizard_exe = EXE(
    PrinterInfoWizard_pyz,
    PrinterInfoWizard_a.scripts,
    [],
    exclude_binaries=True,
    name='PrinterInfoWizard',
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
    icon='Resources/PrinterInfoWizard-128x128.png'
)

Inspector_G_code_a = Analysis(
    ['src/InspectorG-code.py'],
    pathex=[],
    binaries=[],
    datas=[('Printers', 'Printers'),
           ('Resources', 'Resources'),
           ('Third Party', 'Third Party'),
           ('LICENSE', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
Inspector_G_code_pyz = PYZ(Inspector_G_code_a.pure, Inspector_G_code_a.zipped_data, cipher=block_cipher)

Inspector_G_code_exe = EXE(
    Inspector_G_code_pyz,
    Inspector_G_code_a.scripts,
    [],
    exclude_binaries=True,
    name='InspectorG-code',
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
    icon='Resources/InspectorG-code_Icon_128x128.png'
)

coll = COLLECT(
    BedLeveler5000_exe,
    BedLeveler5000_a.binaries,
    BedLeveler5000_a.zipfiles,
    BedLeveler5000_a.datas,
    PrinterInfoWizard_exe,
    PrinterInfoWizard_a.binaries,
    PrinterInfoWizard_a.zipfiles,
    PrinterInfoWizard_a.datas,
    Inspector_G_code_exe,
    Inspector_G_code_a.binaries,
    Inspector_G_code_a.zipfiles,
    Inspector_G_code_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BedLeveler5000',
)
