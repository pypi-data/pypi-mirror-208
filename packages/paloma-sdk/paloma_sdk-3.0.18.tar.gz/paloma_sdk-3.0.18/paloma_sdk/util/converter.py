from datetime import datetime

import bech32


def to_isoformat(dt: datetime) -> str:
    return (
        dt.isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
        .replace(".000Z", "Z")
    )


def address_convert(addr: str, prefix: str) -> str:
    decode_result = bech32.bech32_decode(addr)
    return bech32.bech32_encode(prefix, decode_result[1])
