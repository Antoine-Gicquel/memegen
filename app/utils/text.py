import hashlib
import re
from urllib.parse import unquote
from base64 import urlsafe_b64decode, urlsafe_b64encode


def encode(lines: list[str]) -> str:
    encoded_lines = []

    for line in lines:
        if line == "/":
            encoded_lines.append("_")
        elif line:
            encoded_lines.append(_encode(line))
        else:
            encoded_lines.append("_")

    slug = "/".join(encoded_lines)

    return slug or "_"


def _encode(line):
    return urlsafe_b64encode(line + '=' * (-len(line) % 4).encode()).decode('utf-8')


def decode(slug: str) -> list[str]:
    lines = slug.split("/")
    lines = [urlsafe_b64decode((line + '=' * (-len(line) % 4)).encode()).decode('utf-8') for line in lines]

    return lines


def normalize(slug: str) -> tuple[str, bool]:
    slug = unquote(slug)
    normalized_slug = encode(decode(slug))
    return normalized_slug, slug != normalized_slug


def fingerprint(value: str, *, prefix="_custom-", suffix="") -> str:
    return prefix + hashlib.sha1(value.encode()).hexdigest() + suffix


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value).strip("-")
