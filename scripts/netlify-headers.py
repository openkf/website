"""Keep preview noindex headers separate from indexable production output."""

import argparse
from pathlib import Path
import re


def global_robots(text):
    route = None
    values = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            route = line.strip()
        elif route == "/*":
            name, separator, value = line.strip().partition(":")
            if separator and name.strip().lower() == "x-robots-tag":
                values.append(value.strip().lower())
    return values


def check_headers(text, production):
    values = global_robots(text)
    if production:
        if any(re.search(r"\b(?:noindex|none)\b", value) for value in values):
            raise ValueError("Production output has a global noindex header")
    elif not any(
        ":" not in value and {"noindex", "none"}.intersection(
            item.strip() for item in value.split(",")
        ) for value in values
    ):
        raise ValueError("Preview output lacks a global unqualified noindex header")


def preview_headers(text):
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    insert_at = None
    global_block = False
    for index, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            if global_block:
                insert_at = index
            global_block = line.strip() == "/*"
    if global_block:
        insert_at = len(lines)
    if insert_at is None:
        lines.extend(["\n" if lines else "", "/*\n", "  X-Robots-Tag: noindex\n"])
    else:
        lines.insert(insert_at, "  X-Robots-Tag: noindex\n")
    result = "".join(lines)
    check_headers(result, production=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["preview", "check"])
    parser.add_argument("--environment", default="preview",
                        choices=["production", "preview", "nonprod"])
    parser.add_argument("--file", type=Path, default=Path("public/_headers"))
    args = parser.parse_args()
    text = args.file.read_bytes().decode("utf-8") if args.file.exists() else ""
    if args.action == "preview":
        # Avoid changing unrelated headers or duplicating an existing guard.
        try:
            check_headers(text, production=False)
        except ValueError:
            text = preview_headers(text)
            args.file.parent.mkdir(parents=True, exist_ok=True)
            args.file.write_bytes(text.encode("utf-8"))
    else:
        check_headers(text, production=args.environment == "production")


if __name__ == "__main__":
    main()
