#!/usr/bin/env python

from PyInstaller.utils.win32.versioninfo import FixedFileInfo
from PyInstaller.utils.win32.versioninfo import StringFileInfo
from PyInstaller.utils.win32.versioninfo import StringTable
from PyInstaller.utils.win32.versioninfo import StringStruct
from PyInstaller.utils.win32.versioninfo import VarFileInfo
from PyInstaller.utils.win32.versioninfo import VarStruct
from PyInstaller.utils.win32.versioninfo import VSVersionInfo
import argparse
import datetime
import importlib.util
import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.as_posix())
from Tag import Tag

def main(source, outputDir, tag):
    sys.path.append(source.parent.as_posix())
    sourceSpec = importlib.util.spec_from_file_location('sourceName', source)
    sourceModule = importlib.util.module_from_spec(sourceSpec)
    sys.modules['sourceName'] = sourceModule
    sourceSpec.loader.exec_module(sourceModule)

    executableName = f'{source.stem}.exe'
    description = sourceModule.DESCRIPTION
    versonFile = outputDir / f'{source.stem}_version.py'

    # Verify the output file
    if versonFile.exists():
        print('Output file already exists.', file=sys.stderr)
        sys.exit(1)

    if tag is None:
        version = (0, 0, 0, 0)
    else:
        version = Tag(tag).asTuple(4)
    versionString = '.'.join(str(x) for x in version)

    currentYear = datetime.date.today().year
    copyRightRange = '2023'
    if currentYear > 2023:
        copyRightRange += f'-{currentYear}'

    stringTable = StringTable(u'040904b0', # 0409 = en-us, 04b0 = Unicode
                              [StringStruct(u'CompanyName', u'S&M Makers, LLC'),
                              StringStruct(u'FileDescription', description),
                              StringStruct(u'FileVersion', versionString),
                              StringStruct(u'InternalName', executableName),
                              StringStruct(u'LegalCopyright', f'Copyright (C) {copyRightRange} S&M Makers, LLC, All rights reserved.'),
                              StringStruct(u'OriginalFilename', executableName),
                              StringStruct(u'ProductName', u'Bed Leveler 5000 Software Suite'),
                              StringStruct(u'ProductVersion', versionString)])

    vsVersionInfo = VSVersionInfo(ffi=FixedFileInfo(filevers=version,
                                                    prodvers=version),
                                  kids=[StringFileInfo([stringTable]),
                                        VarFileInfo([VarStruct(u'Translation', [0x0409, 1200])])])

    with open(versonFile, 'wb') as file:
        file.write(str(vsVersionInfo).encode())

if __name__ == '__main__':
    parser = argparse.ArgumentParser('CreateVersionFile')
    parser.add_argument('source', type=pathlib.Path, help='source file')
    parser.add_argument('output', type=pathlib.Path, help='output directory')
    parser.add_argument('-t', '--tag', default=None, help='version tag')

    args = parser.parse_args()
    main(args.source, args.output, args.tag)