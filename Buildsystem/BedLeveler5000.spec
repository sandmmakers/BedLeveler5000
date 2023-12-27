import pathlib

topLevelDir = pathlib.Path(SPECPATH).parent
srcDir = topLevelDir / 'src'
resourcesDir = topLevelDir / 'Resources'
buildDir = topLevelDir / 'Build'
installDir = pathlib.Path(DISTPATH) / specnm
internalDir = installDir / '_internal'

block_cipher = None

BedLeveler5000_a = Analysis(
    [srcDir / 'BedLeveler5000.py'],
    pathex=[],
    binaries=[],
    datas=[(resourcesDir, 'Resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
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
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=(resourcesDir / 'Icon-128x128.png').as_posix(),
    version=(buildDir / 'BedLeveler5000_version.py').as_posix(),
)

PrinterInfoWizard_a = Analysis(
    [srcDir / 'PrinterInfoWizard.py'],
    pathex=[],
    binaries=[],
    datas=[(resourcesDir, 'Resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
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
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=(resourcesDir / 'PrinterInfoWizard-128x128.png').as_posix(),
    version=(buildDir / 'PrinterInfoWizard_version.py').as_posix(),
)

Inspector_G_code_a = Analysis(
    [srcDir / 'InspectorG-code.py'],
    pathex=[],
    binaries=[],
    datas=[(resourcesDir, 'Resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
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
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=(resourcesDir / 'InspectorG-code_Icon_128x128.png').as_posix(),
    version=(buildDir / 'InspectorG-Code_version.py').as_posix(),
)

PrinterTester_a = Analysis(
    [srcDir / 'PrinterTester.py'],
    pathex=[],
    binaries=[],
    datas=[(resourcesDir, 'Resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
PrinterTester_pyz = PYZ(PrinterTester_a.pure, PrinterTester_a.zipped_data, cipher=block_cipher)

PrinterTester_exe = EXE(
    PrinterTester_pyz,
    PrinterTester_a.scripts,
    [],
    exclude_binaries=True,
    name='PrinterTester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=(resourcesDir / 'PrinterTester-128x128.png').as_posix(),
    version=(buildDir / 'PrinterTester_version.py').as_posix(),
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
    PrinterTester_exe,
    PrinterTester_a.binaries,
    PrinterTester_a.zipfiles,
    PrinterTester_a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='BedLeveler5000',
)

# Move Additional files
import shutil
shutil.copytree(topLevelDir / 'Printers', installDir / 'Printers')
shutil.copytree(topLevelDir / 'Third Party', internalDir / 'Third Party')
shutil.copy(topLevelDir / 'LICENSE', internalDir / 'LICENSE')