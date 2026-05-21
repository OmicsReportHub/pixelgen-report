#!/usr/bin/env python3
"""Prepare the pixelatorR source package for the webR release workflow."""

from __future__ import annotations

import io
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESTINATION = REPO_ROOT / "webr-packages" / "patched-src" / "pixelatorR"
SOURCE_URL = "https://github.com/PixelgenTechnologies/pixelatorR/archive/refs/tags/v0.17.1.tar.gz"


def safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members: list[tarfile.TarInfo] = []
    for member in archive.getmembers():
        path = Path(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"Unsafe archive member: {member.name}")
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

        source_dirs = sorted(path for path in tmpdir.iterdir() if path.is_dir())
        if len(source_dirs) != 1:
            raise RuntimeError(f"Expected one pixelatorR source directory, found {source_dirs}")

        if DESTINATION.exists():
            shutil.rmtree(DESTINATION)
        shutil.copytree(source_dirs[0], DESTINATION)

    print(f"Wrote {DESTINATION}")


if __name__ == "__main__":
    main()
