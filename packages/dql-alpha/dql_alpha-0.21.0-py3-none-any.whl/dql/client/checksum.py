import hashlib
import sys
from functools import partial

if sys.version_info < (3, 9):
    md5 = hashlib.md5
else:
    md5 = partial(hashlib.md5, usedforsecurity=False)

BUFSIZE = 2**18


def file_digest(fileobj):
    """Calculate the digest of a file-like object."""
    buf = bytearray(BUFSIZE)  # Reusable buffer to reduce allocations.
    view = memoryview(buf)
    digestobj = md5()
    # From 3.11's hashlib.filedigest()
    while True:
        size = fileobj.readinto(buf)
        if size == 0:
            break  # EOF
        digestobj.update(view[:size])
    return digestobj.hexdigest()
