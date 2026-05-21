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

TEXT_REPLACEMENTS = {
    "          outdata <- read_parquet(file.path(exdir_temp, item_name))":
        "          outdata <- arrow::read_parquet(file.path(exdir_temp, item_name))",
    "  nm_dt <- (coords %>% schema())$GetFieldByName(\"name\")$ToString() %>% stringr::str_remove(\"name: \")":
        "  nm_dt <- (coords %>% arrow::schema())$GetFieldByName(\"name\")$ToString() %>% stringr::str_remove(\"name: \")",
    "  object <- object %>% to_duckdb()":
        "  object <- object %>% arrow::to_duckdb()",
}


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

    patch_browser_optional_arrow(DESTINATION)
    print(f"Wrote {DESTINATION}")


def patch_browser_optional_arrow(source_dir: Path) -> None:
    """Let pixelatorR load in webR without the unsupported arrow package.

    The upstream package imports arrow, but arrow does not currently produce a
    webR binary package. Browser builds still keep arrow-qualified code paths,
    so functions that actually need parquet/Arrow support fail at call time
    instead of preventing library(pixelatorR) from loading.
    """
    description = source_dir / "DESCRIPTION"
    text = description.read_text(encoding="utf-8")
    text = text.replace("    arrow,\n", "")
    if "Suggests:\n    arrow,\n" not in text:
        text = text.replace("Suggests:\n", "Suggests:\n    arrow,\n", 1)
    description.write_text(text, encoding="utf-8")

    namespace = source_dir / "NAMESPACE"
    lines = namespace.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith("importFrom(arrow,")]
    namespace.write_text("\n".join(lines) + "\n", encoding="utf-8")

    roxygen = source_dir / "R" / "pixelatorR-package.R"
    lines = roxygen.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith("#' @importFrom arrow ")]
    roxygen.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for relative_path in [
        "R/load_data_mpx.R",
        "R/graph_conversion.R",
    ]:
        path = source_dir / relative_path
        text = path.read_text(encoding="utf-8")
        for old, new in TEXT_REPLACEMENTS.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
