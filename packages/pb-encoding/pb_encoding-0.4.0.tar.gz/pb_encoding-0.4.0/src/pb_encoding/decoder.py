import struct
from typing import Any, Tuple, Callable, Union

from .typing import SupportedType

__all__ = (
    "DecodeField",
    "getDecoder",
    "UnpackField",
)


def _VarintDecoder(mask, result_type):
    def DecodeVarint(buffer, pos):
        result = 0
        shift = 0
        while 1:
            b = buffer[pos]
            result |= (b & 0x7F) << shift
            pos += 1
            if not (b & 0x80):
                result &= mask
                result = result_type(result)
                break
            shift += 7
            if shift >= 64:
                raise Exception("Too many bytes when decoding varint.")

        return (result, pos)

    return DecodeVarint


def _SignedVarintDecoder(bits, result_type):
    signbit = 1 << (bits - 1)
    mask = (1 << bits) - 1

    def DecodeVarint(buffer, pos):
        result = 0
        shift = 0
        while 1:
            b = buffer[pos]
            result |= (b & 0x7F) << shift
            pos += 1
            if not (b & 0x80):
                result &= mask
                result = (result ^ signbit) - signbit
                result = result_type(result)
                break
            shift += 7
            if shift >= 64:
                raise Exception("Too many bytes when decoding varint.")

        return (result, pos)

    return DecodeVarint


DecodeVarint32 = _VarintDecoder((1 << 32) - 1, int)
DecodeVarint = _VarintDecoder((1 << 64) - 1, int)
DecodeSignedVarint32 = _SignedVarintDecoder(32, int)
DecodeSignedVarint = _SignedVarintDecoder(64, int)


def _ZigZagDecode(value):
    if not value & 0x1:
        return value >> 1
    return (value >> 1) ^ (~0)


def DecodeSignedVarint32ZigZag(buffer, pos):
    value, pos = DecodeSignedVarint32(buffer, pos)
    return _ZigZagDecode(value), pos


def DecodeSignedVarintZigZag(buffer, pos):
    value, pos = DecodeSignedVarint(buffer, pos)
    return _ZigZagDecode(value), pos


def _StructPackDecoder(format):
    value_size = struct.calcsize(format)

    def _DecodeField(buffer, pos):
        new_pos = pos + value_size
        return struct.unpack(format, buffer[pos:new_pos])[0], new_pos

    return _DecodeField


DecodeFixed32 = _StructPackDecoder("<I")
DecodeFixed64 = _StructPackDecoder("<Q")
# the following two lines are needed?
DecodeSFixed32 = _StructPackDecoder("<i")
DecodeSFixed64 = _StructPackDecoder("<q")
DecodeFloat = _StructPackDecoder("<f")
DecodeDouble = _StructPackDecoder("<d")


def DecodeString(buffer, pos):
    size, pos = DecodeVarint(buffer, pos)
    new_pos = pos + size
    return buffer[pos:new_pos].decode("utf-8"), new_pos


def DecodeBytes(buffer, pos) -> Tuple[bytes, int]:
    size, pos = DecodeVarint(buffer, pos)
    new_pos = pos + size
    return bytes(buffer[pos:new_pos]), new_pos


_field_decoder_mapping = {
    "int32": DecodeSignedVarint32,
    "int64": DecodeSignedVarint,
    "uint32": DecodeVarint32,
    "uint64": DecodeVarint,
    "sint32": DecodeSignedVarint32ZigZag,
    "sint64": DecodeSignedVarintZigZag,
    "fixed32": DecodeFixed32,
    "fixed64": DecodeFixed64,
    "sfixed32": DecodeSFixed32,
    "sfixed64": DecodeSFixed64,
    "string": DecodeString,
    "bytes": DecodeBytes,
    "float": DecodeFloat,
    "double":DecodeDouble,
}


def getDecoder(type: SupportedType) -> Callable:
    return _field_decoder_mapping[type]


def DecodeField(type: SupportedType, buffer, pos: int) -> Tuple[Any, int]:
    return _field_decoder_mapping[type](buffer, pos)


def UnpackField(type: SupportedType, buffer) -> Union[str, int, float, bytes]:
    pos = 0
    value, _ = DecodeField(type, buffer, pos)
    return value
