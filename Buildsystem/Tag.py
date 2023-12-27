#!/usr/bin/env python

import re

class Tag:
    def __init__(self, tag):
        # Verify tag format
        if re.fullmatch(r'^v[0-9]+\.[0-9]+\.[0-9]+$', tag) is None:
            raise IOError(f'"{tag}" is not a valid tag.')
        parts = tag[1:].split('.')

        self.tag = tag
        self.major = int(parts[0])
        self.minor = int(parts[1])
        self.patch = int(parts[2])

    def asDict(self):
        return {'major': self.major,
                'minor': self.minor,
                'patch': self.patch}

    def asTuple(self, size=3):
        assert(size > 0 and size <= 4)

        parts = []

        if size >= 1:
            parts.append(self.major)
        if size >= 2:
            parts.append(self.minor)
        if size >= 3:
            parts.append(self.patch)
        if size == 4:
            parts.append(0)

        return tuple(parts)