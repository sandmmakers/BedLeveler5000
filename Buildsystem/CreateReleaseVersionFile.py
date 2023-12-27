#!/usr/bin/env python

import argparse
import json
import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.as_posix())
from Tag import Tag

parser = argparse.ArgumentParser('Release version utility')
parser.add_argument('tag', help='version tag')
parser.add_argument('output', type=pathlib.Path, help='output directory')

args = parser.parse_args()

try:
    version = Tag(args.tag).asDict()

    outputFilePath = args.output / 'RELEASE_VERSION'
    if outputFilePath.exists():
        raise IOError(f'{outputFilePath} already exists.')

    with open(outputFilePath, 'w') as file:
        json.dump(version, file)

except IOError as exception:
    print(exception, file=sys.stderr)
    sys.exit(1)