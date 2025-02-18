import hashlib
import re
from urllib.parse import unquote
from base64 import urlsafe_b64decode, urlsafe_b64encode
import os


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
    if os.getenv('MEMEGEN_BASE64', '') == '1':
        return urlsafe_b64encode(line.encode()).decode('utf-8').replace("=", "")
    else:
        has_trailing_under = "_ " in line

        encoded = unquote(line)

        for before, after in [
            ("_", "__"),
            ("-", "--"),
            (" ", "_"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ('"', "''"),
            ("/", "~s"),
            ("\\", "~b"),
            ("\n", "~n"),
            ("&", "~a"),
            ("<", "~l"),
            (">", "~g"),
            ("‘", "'"),
            ("’", "'"),
            ("“", '"'),
            ("”", '"'),
            ("–", "-"),
        ]:
            encoded = encoded.replace(before, after)

        if has_trailing_under:
            encoded = encoded.replace("___", "__-")

        return encoded


def decode(slug: str) -> list[str]:
    if os.getenv('MEMEGEN_BASE64', '') == '1':
        lines = slug.split("/")
        lines = [urlsafe_b64decode((line + '=' * (-len(line) % 4)).encode()).decode('utf-8') for line in lines]

        return lines
    else:
        has_dash = "_----" in slug
        has_flag = "_--" in slug
        has_arrow = "_--~g" in slug
        has_under = "___" in slug

        slug = slug.replace("_", " ").replace("  ", "_")
        slug = slug.replace("-", " ").replace("  ", "-")
        slug = slug.replace("''", '"')

        if has_dash:
            slug = slug.replace("-- ", " --")
        elif has_flag:
            slug = slug.replace("- ", " -")

        if has_arrow:
            slug = slug.replace("- ~g", " -~g")

        if has_under:
            slug = slug.replace("_ ", " _")

        for before, after in [
            ("~q", "?"),
            ("~p", "%"),
            ("~h", "#"),
            ("~n", "\n"),
            ("~a", "&"),
            ("~l", "<"),
            ("~g", ">"),
            ("~b", "\\"),
        ]:
            slug = slug.replace(before, after)

        lines = slug.split("/")
        lines = [line.replace("~s", "/") for line in lines]

        return lines


def normalize(slug: str) -> tuple[str, bool]:
    slug = unquote(slug)
    normalized_slug = encode(decode(slug))
    return normalized_slug, slug != normalized_slug


def fingerprint(value: str, *, prefix="_custom-", suffix="") -> str:
    return prefix + hashlib.sha1(value.encode()).hexdigest() + suffix


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value).strip("-")
