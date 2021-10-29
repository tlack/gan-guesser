def read_bytes(fn):
    return open(fn, 'rb').read().strip()

def read_file(fn):
    return open(fn, 'r').read().strip()

def strip_trailing_s(string):
    if string[-1] == "s": return string[:-1]
    else: return string

