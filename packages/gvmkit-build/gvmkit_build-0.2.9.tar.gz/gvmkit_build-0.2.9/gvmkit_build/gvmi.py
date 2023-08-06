"""
.gvmi format operations
"""

import io
import json
import zlib
from typing import NamedTuple, Optional

from typing.io import BinaryIO
from typing_extensions import Final

_META_ENCODING: Final = "utf-8"
_META_SIZE_BYTES: Final = 8
_CRC32_BYTES = 4


class InvalidImageFormat(Exception):
    pass


class _Info(NamedTuple):
    crc_position: int
    meta_bytes: Optional[bytes] = None
    crc32: Optional[int] = None


def _find_meta_bytes(file_object: BinaryIO) -> _Info:
    file_size = file_object.seek(-_META_SIZE_BYTES, io.SEEK_END) + _META_SIZE_BYTES
    meta_size_bytes = file_object.read(_META_SIZE_BYTES)
    assert meta_size_bytes is not None
    try:
        meta_size = int(meta_size_bytes.decode("ascii"))
    except ValueError:
        return _Info(file_size)

    pos = file_object.seek(-(_META_SIZE_BYTES + meta_size + _CRC32_BYTES), io.SEEK_END)
    if pos < 0:
        return _Info(file_size)
    crc32_bytes = file_object.read(_CRC32_BYTES)
    assert crc32_bytes is not None
    crc32saved = int.from_bytes(crc32_bytes, "little", signed=False)

    meta_bytes = file_object.read(meta_size)
    assert meta_bytes is not None
    crc32sum = zlib.crc32(meta_bytes)
    if crc32sum != crc32saved:
        return _Info(file_size)

    return _Info(crc_position=pos, meta_bytes=meta_bytes, crc32=crc32sum)


def decode_meta(file_object: BinaryIO) -> dict:
    _, meta_bytes, _ = _find_meta_bytes(file_object)
    if meta_bytes is None:
        raise InvalidImageFormat("Missing meta data")

    meta = json.loads(meta_bytes.decode(_META_ENCODING))
    if isinstance(meta, dict):
        return meta
    raise InvalidImageFormat("Invalid meta json", meta)


def encode_meta(file_object: BinaryIO, meta: dict):
    r = _find_meta_bytes(file_object)
    meta_bytes = json.dumps(meta).encode(_META_ENCODING)
    crc32_bytes = zlib.crc32(meta_bytes).to_bytes(_CRC32_BYTES, byteorder="little", signed=False)
    meta_size_bytes = ("%08d" % (len(meta_bytes),)).encode("ascii")
    file_object.seek(r.crc_position, io.SEEK_SET)
    file_object.write(crc32_bytes)
    file_object.write(meta_bytes)
    file_object.write(meta_size_bytes)
    file_object.truncate()
