import magic

old_tostr = magic.Magic._Magic__tostr
old_tobytes = magic.Magic._Magic__tobytes


def new_tostr(s):
    try:
        return old_tostr(s)
    except Exception:
        return str(s)

def new_tobytes(b):
    try:
        return old_tobytes(b)
    except Exception:
        return bytes(b)

magic.Magic._Magic__tostr = new_tostr
magic.Magic._Magic__tobytes = new_tobytes
