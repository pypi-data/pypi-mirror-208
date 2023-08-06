import hashlib
import json


def hash_sha256_dict(x: dict = None) -> str:
    assert x is None or type(x) is dict, f"Invalid object to hash, it required dict but see type of {type(x)}"
    return hashlib.md5(json.dumps(x, indent=4, sort_keys=True, default=str).encode()).hexdigest()
