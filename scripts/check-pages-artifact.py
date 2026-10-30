"""Verify the existing gh-pages byte tree before and after artifact upload."""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def payload_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ValueError("Unexpected path in the published payload")
    return str(path)


def record_snapshot(root, manifest_file, archive):
    root = root.resolve()
    git = ["git", "-C", str(root)]
    commit = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(git + ["rev-parse", "HEAD^{tree}"], text=True).strip()
    raw = subprocess.check_output(git + ["ls-tree", "-rtz", "--full-tree", "HEAD"])
    files = {}
    directories = {"."}
    packed = []
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, filename = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        name = payload_path(filename.decode("utf-8"))
        if kind == "tree":
            directories.add(name)
            continue
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("Pages payload must contain regular tracked files only")
        path = root.joinpath(*PurePosixPath(name).parts)
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Pages payload escaped the checked-out snapshot")
        content = path.read_bytes()
        actual_blob = hashlib.sha1(
            b"blob " + str(len(content)).encode("ascii") + b"\0" + content
        ).hexdigest()
        if actual_blob != blob:
            raise ValueError("A published file differs from its Git blob")
        files[name] = {"sha256": hashlib.sha256(content).hexdigest(),
                       "bytes": len(content), "executable": mode == "100755"}
        packed.append((name, content, mode, int(path.stat().st_mtime)))
    if "index.html" not in files or not files:
        raise ValueError("The existing published index is missing")
    # Match the official Pages artifact.tar protocol while preserving tracked
    # dotfiles such as the existing empty .nojekyll marker. Never pack .git.
    with tarfile.open(archive, "w") as payload:
        for name in sorted(directories, key=lambda item: (item.count("/"), item)):
            entry = tarfile.TarInfo(name)
            entry.type = tarfile.DIRTYPE
            entry.mode = 0o755
            payload.addfile(entry)
        for name, content, mode, mtime in packed:
            entry = tarfile.TarInfo(name)
            entry.size = len(content)
            entry.mode = 0o755 if mode == "100755" else 0o644
            entry.mtime = mtime
            payload.addfile(entry, io.BytesIO(content))
    result = {"commit": commit, "tree": tree, "files": files,
              "directories": sorted(directories)}
    manifest_file.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
    print(f"Recorded published snapshot {commit}, tree {tree}, {len(files)} files")


def verify_artifact(manifest_file, archive):
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    expected = manifest["files"]
    expected_dirs = set(manifest["directories"])
    seen = set()
    seen_dirs = set()
    with tarfile.open(archive, "r:*") as payload:
        for member in payload:
            name = payload_path(member.name)
            if member.isdir():
                if name not in expected_dirs or name in seen_dirs:
                    raise ValueError("Artifact has an extra or duplicate directory")
                seen_dirs.add(name)
                continue
            if member.type not in {tarfile.REGTYPE, tarfile.AREGTYPE} or name not in expected or name in seen:
                raise ValueError("Artifact has an extra, duplicate or non-regular file")
            file = expected[name]
            if member.size != file["bytes"]:
                raise ValueError("Uploaded artifact changed a published file size")
            content = payload.extractfile(member).read()
            if len(content) != file["bytes"] or (
                hashlib.sha256(content).hexdigest() != file["sha256"]
            ) or bool(member.mode & 0o111) != file["executable"]:
                raise ValueError("Uploaded artifact changed the published byte tree")
            seen.add(name)
    if seen != set(expected) or seen_dirs != expected_dirs:
        raise ValueError("Uploaded artifact omitted published files or directories")
    print(f"Verified uploaded Pages artifact: {len(seen)} unchanged files")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["record", "verify"])
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if args.action == "record":
        if args.archive is None:
            parser.error("record requires --archive")
        record_snapshot(args.first, args.second, args.archive)
    else:
        verify_artifact(args.first, args.second)


if __name__ == "__main__":
    main()
