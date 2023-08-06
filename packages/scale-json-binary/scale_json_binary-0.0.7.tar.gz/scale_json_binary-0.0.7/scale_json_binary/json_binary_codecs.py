import dataclasses
import numpy as np
import ujson
from io import BytesIO
from typing import IO, Any, List, Optional

"""
TODO(dmchoi): there was a bug in an older version of json_binary_encoder where TypedDicts aren't being encoded properly for some reason. Need to investigate
https://app.shortcut.com/scaleai/story/417111/binaryjsonencoder-does-not-handle-typeddicts-correctly

Validate that this version works
"""


def fill_block(data: bytes, block_size: int = 4, fill: bytes = b"\00") -> bytes:
    return data + fill * (block_size - len(data) % block_size)


def dump(obj: Any, fp: IO[bytes]) -> None:
    block_size = 4
    items = []
    binaries = [bytes(block_size)]

    def get_offset(binaries: List[bytes]) -> int:
        return sum([len(b) for b in binaries])

    def encode(obj: Any, keys: List[str]) -> Any:
        if dataclasses.is_dataclass(obj):
            # if the object is a dataclass, convert to json
            return encode(dataclasses.asdict(obj), keys)

        if isinstance(obj, dict):
            obj = dict(obj)
            for k, v in obj.items():
                obj[k] = encode(v, keys + [k])
            return obj

        if isinstance(obj, list):
            obj = list(obj)
            for k, v in enumerate(obj):
                obj[k] = encode(v, keys + [k])
            return obj

        if isinstance(obj, np.ndarray):
            data = obj.tobytes()
            fill_size = block_size - len(data) % block_size
            offset = get_offset(binaries)
            binaries.append(data)
            binaries.append(b"\00" * fill_size)
            items.append(
                {
                    "keys": keys,
                    "length": len(data),
                    "offset": offset,
                    "dtype": obj.dtype.name,
                    "shape": obj.shape,
                }
            )
            return ""

        return obj

    header = dict(encode(obj, []))
    header["$items"] = items

    encoded_header = fill_block(ujson.dumps(header).encode("utf-8"), block_size, b" ")

    fp.write(encoded_header)
    for binary in binaries:
        fp.write(binary)


def dumps(obj: Any) -> bytes:
    fp = BytesIO()
    dump(obj, fp)
    fp.seek(0)
    return fp.read()


def write_file(file_path: str, obj: dict) -> None:
    with open(file_path, "wb") as fp:
        dump(obj, fp)


def loads(data: bytes) -> dict:
    header_length = data.find(bytes(1))
    obj = ujson.loads(data[:header_length].decode("utf-8"))
    if not isinstance(obj, dict):
        raise Exception("Loaded data was not a valid dict")

    items = obj.pop("$items")
    data = data[header_length:]

    def set_nested(obj: dict, keys: list, value: Any) -> None:
        while len(keys) > 1:
            if isinstance(obj, list):
                obj = obj[int(keys.pop(0))]
            else:
                obj = obj[keys.pop(0)]
        obj[keys[0]] = value

    for item in items:
        raw_value: bytes = data[item["offset"] : item["offset"] + item["length"]]
        if "dtype" in item:
            np_value = np.frombuffer(raw_value, dtype=item["dtype"])
            if "shape" in item:
                np_value = np_value.reshape(item["shape"])
            set_nested(obj, item["keys"], np_value)
        else:
            set_nested(obj, item["keys"], raw_value)

    return obj


def load(fp: IO[bytes]) -> dict:
    return loads(fp.read())


def read_file(file_path: str) -> dict:
    with open(file_path, "rb") as fp:
        return load(fp)


# Class for retro-compatibility
class JSONBinaryEncoder:
    def dumps(self, obj: Any) -> bytes:
        return dumps(obj)

    def loads(self, data: bytes) -> dict:
        return loads(data)

    def write_file(self, file_path: str, obj: dict) -> None:
        return write_file(file_path, obj)

    def read_file(self, file_path: str) -> dict:
        with open(file_path, "rb") as fp:
            return self.loads(fp.read())
