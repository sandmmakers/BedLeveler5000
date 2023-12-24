def majorVersion(): return 0
def minorVersion(): return 3
def bugVersion(): return 3
def version(fourParts=False):
    parts3 = f'{majorVersion()}.{minorVersion()}.{bugVersion()}'
    if fourParts:
        return parts3 + '.0'
    else:
        return parts3