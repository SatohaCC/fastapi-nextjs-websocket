"""RFC 9562 に準拠した UUIDv7 生成ユーティリティ。"""

import os
import time
import uuid


def generate_uuid7() -> uuid.UUID:
    """時系列ソート可能な UUIDv7 を生成して返します。"""
    timestamp_ms = int(time.time() * 1000)
    timestamp_bytes = timestamp_ms.to_bytes(6, byteorder="big")

    rand_bytes = os.urandom(10)

    b = bytearray(16)
    b[0:6] = timestamp_bytes
    b[6:16] = rand_bytes

    # Version 7 (0111) 設定
    b[6] = (b[6] & 0x0F) | 0x70
    # Variant 2 (10) 設定
    b[8] = (b[8] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(b))
