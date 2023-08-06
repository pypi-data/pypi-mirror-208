import zlib


def crc_from_file(fname, fix_3ds_header=False):
    prev = 0
    data = b""
    with open(fname, "rb") as filep:
        #  Replace 0x48 bytes with 0xFF at position 4608
        if fix_3ds_header:
            upper = 0x1200 + 0x48
            lower = 0x1200
            chunk = filep.read(upper)
            lchunk = bytearray(chunk)
            lchunk[lower:upper] = [0xFF] * 0x48
            data = data + bytes(lchunk)
            prev = zlib.crc32(bytes(lchunk), prev)

        for chunk in iter(lambda: filep.read(4096), b""):
            prev = zlib.crc32(chunk, prev)
            # data = data + chunk
    return f"{prev & 0xFFFFFFFF:08X}"  # , data
