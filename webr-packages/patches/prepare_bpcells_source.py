#!/usr/bin/env python3
"""Prepare the BPCells R package source for the webR release workflow."""

from __future__ import annotations

import io
import os
import shutil
import stat
import tarfile
import tempfile
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESTINATION = REPO_ROOT / "webr-packages" / "patched-src" / "BPCells"
SOURCE_URL = "https://github.com/bnprks/BPCells/archive/refs/tags/v0.3.1.tar.gz"


def safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members: list[tarfile.TarInfo] = []
    for member in archive.getmembers():
        path = Path(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"Unsafe archive member: {member.name}")
        if len(path.parts) >= 2 and path.parts[1] == "r":
            members.append(member)
    return members


def main() -> None:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "pixelgen-report-webr-release"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        archive_bytes = response.read()

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            archive.extractall(tmpdir, members=safe_members(archive))

        source_dirs = sorted(tmpdir.glob("*/r"))
        if len(source_dirs) != 1:
            raise RuntimeError(f"Expected one BPCells R source directory, found {source_dirs}")

        if DESTINATION.exists():
            shutil.rmtree(DESTINATION)
        shutil.copytree(source_dirs[0], DESTINATION)

    configure = DESTINATION / "configure"
    if configure.exists():
        configure.chmod(configure.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    patch_hdf5_header()
    print(f"Wrote {DESTINATION}")


def patch_hdf5_header() -> None:
    header = DESTINATION / "src" / "bpcells-cpp" / "arrayIO" / "hdf5.h"
    text = header.read_text(encoding="utf-8")
    replacements = {
        "dataset.resize({cur_size + count});": (
            "dataset.resize({static_cast<size_t>(cur_size + count)});"
        ),
        "dataset.select({cur_size}, {count}).write_raw(in, datatype);": (
            "dataset.select({static_cast<size_t>(cur_size)}, "
            "{static_cast<size_t>(count)}).write_raw(in, datatype);"
        ),
        "dataset.select({pos}, {count}).read_raw(out, datatype);": (
            "dataset.select({pos}, {static_cast<size_t>(count)}).read_raw(out, datatype);"
        ),
    }
    for old, new in replacements.items():
        if old not in text:
            raise RuntimeError(f"Expected BPCells HDF5 source line was not found: {old}")
        text = text.replace(old, new)
    header.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
