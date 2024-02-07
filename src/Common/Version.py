import json
import pathlib
import re
import subprocess
import sys

def gitHash():
    if hasattr(sys, '_MEIPASS'):
        with open(pathlib.Path(sys._MEIPASS)/ 'GIT_HASH', 'r') as file:
            gitHash = file.read().strip()
            if re.fullmatch('[0-9A-F]{40}(-dirty)?', gitHash) is None:
                raise IOError('Invalid GIT_HASH file detected.')
            return gitHash

    command = ['git', 'describe', '--always', '--dirty', '--abbrev=40', '--match=\'NoTagWithThisName\'']

    try:
        result = subprocess.run(command, capture_output=True)
    except FileNotFoundError as exception:
        raise IOError(f'Failed to find the {command[0]} executable.')
    if result.returncode != 0 or len(result.stdout) < 41:
        raise IOError('Failed to get git hash.')

    raw = result.stdout.decode().strip()
    return raw[0:40].upper() + raw[40:]

def _releaseFile():
    try:
        with open(pathlib.Path(sys._MEIPASS) / 'RELEASE_VERSION', 'r') as file:
            return json.load(file)
    except (AttributeError, FileNotFoundError):
        return {}

def majorVersion(): return _releaseFile().get('major')
def minorVersion(): return _releaseFile().get('minor')
def patchVersion(): return _releaseFile().get('patch')

def version():
    if None in [majorVersion(), minorVersion(), patchVersion()]:
        return None
    return f'v{majorVersion()}.{minorVersion()}.{patchVersion()}'

def displayVersion():
    if version() is not None:
        return version()
    else:
        return gitHash()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser('Bed Leveler 5000 version utility')
    parserGroup = parser.add_mutually_exclusive_group(required=True)
    parserGroup.add_argument('-a', '--all', action='store_true', help='display all')
    parserGroup.add_argument('-g', '--git-hash', action='store_true', help='git hash')
    parserGroup.add_argument('-M', '--major', action='store_true', help='major version')
    parserGroup.add_argument('-m', '--minor', action='store_true', help='minor version')
    parserGroup.add_argument('-p', '--patch', action='store_true', help='patch version')
    parserGroup.add_argument('-f', '--full', action='store_true', help='full version')
    parserGroup.add_argument('-d', '--display', action='store_true', help='display version')

    args = parser.parse_args()

    try:
        if args.git_hash:
            print(gitHash())
        elif args.major:
            print(majorVersion())
        elif args.minor:
            print(minorVersion())
        elif args.patch:
            print(patchVersion())
        elif args.full:
            print(version())
        elif args.display:
            print(displayVersion())
        else:
            print(f'Git hash: {gitHash()}')
            print(f'Major: {majorVersion()}')
            print(f'Minor: {minorVersion()}')
            print(f'Patch: {patchVersion()}')
            print(f'Version: {version()}')
            print(f'Display version: {displayVersion()}')
    except IOError as exception:
        print(exception, file=sys.stderr)
        sys.exit(1)