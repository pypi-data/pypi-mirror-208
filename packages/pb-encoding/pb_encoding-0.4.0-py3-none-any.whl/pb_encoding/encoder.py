import struct
from typing import Callable, Any

from .typing import SupportedType

__all__ = (
    "EncodeField",
    "getEncoder",
    "PackField",
)


def EncodeVarint(write, value):
    local_int2byte = struct.Struct(">B").pack
    bits = value & 0x7F
    value >>= 7
    while value:
        write(local_int2byte(0x80 | bits))
        bits = value & 0x7F
        value >>= 7
    write(local_int2byte(bits))


def EncodeSignedVarint(write, value):
    local_int2byte = struct.Struct(">B").pack
    if value < 0:
        value += 1 << 64
    bits = value & 0x7F
    value >>= 7
    while value:
        write(local_int2byte(0x80 | bits))
        bits = value & 0x7F
        value >>= 7
    write(local_int2byte(bits))


def _ZigZagEncode(value):
    if value >= 0:
        return value << 1
    return (value << 1) ^ (~0)


def EncodeSignedVarintZigZag(write, value):
    return EncodeSignedVarint(write, _ZigZagEncode(value))


def _StructPackEncoder(format):
    def _EncodeField(write, value):
        write(struct.pack(format, value))

    return _EncodeField


def EncodeBytes(write, value: bytes):
    EncodeVarint(write, len(value))
    write(value)


EncodeFixed32 = _StructPackEncoder("<I")
EncodeFixed64 = _StructPackEncoder("<Q")
EncodeSFixed32 = _StructPackEncoder("<i")
EncodeSFixed64 = _StructPackEncoder("<q")
EncodeFloat = _StructPackEncoder("<f")
EncodeDouble = _StructPackEncoder("<d")


def EncodeString(write, value):
    encoded = value.encode("utf-8")
    EncodeVarint(write, len(encoded))
    write(encoded)


_field_encoder_mapping = {
    "int32": EncodeSignedVarint,
    "int64": EncodeSignedVarint,
    "uint32": EncodeVarint,
    "uint64": EncodeVarint,
    "sint32": EncodeSignedVarintZigZag,
    "sint64": EncodeSignedVarintZigZag,
    "fixed32": EncodeFixed32,
    "fixed64": EncodeFixed64,
    "sfixed32": EncodeSFixed32,
    "sfixed64": EncodeSFixed64,
    "string": EncodeString,
    "bytes": EncodeBytes,
    "float": EncodeFloat,
    "double": EncodeDouble,
}


def getEncoder(type: SupportedType) -> Callable:
    return _field_encoder_mapping[type]


def EncodeField(type: SupportedType, write: Callable[[bytes], Any], value: Any) -> None:
    return _field_encoder_mapping[type](write, value)


def PackField(type: SupportedType, value) -> bytes:
    b = bytearray()
    EncodeField(type, b.__iadd__, value)
    return bytes(b)
