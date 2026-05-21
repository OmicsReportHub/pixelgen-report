#!/usr/bin/env python3
"""Build a small downloadable Pixelgen browser R release bundle."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = (REPO_ROOT / "webr-packages" / "VERSION").read_text(encoding="utf-8").strip()
DIST_DIR = REPO_ROOT / "dist"
BUNDLE_DIR = DIST_DIR / f"pixelgen-r-browser-{VERSION}"
ARCHIVE_PATH = DIST_DIR / f"pixelgen-r-browser-{VERSION}.zip"


def main() -> None:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    copy_file(REPO_ROOT / "index.html", BUNDLE_DIR / f"pixelgen-r-console-{VERSION}.html")
    copy_file(REPO_ROOT / "README.md", BUNDLE_DIR / "README.md")

    package_dir = BUNDLE_DIR / "webr-packages"
    package_dir.mkdir()
    for name in ["VERSION", "packages", "packages.graph-experimental", "packages.pixi-full", "README.md"]:
        copy_file(REPO_ROOT / "webr-packages" / name, package_dir / name)

    patches_dir = package_dir / "patches"
    patches_dir.mkdir()
    for name in ["rwasm-c17.mk", "prepare_png_source.py"]:
        copy_file(REPO_ROOT / "webr-packages" / "patches" / name, patches_dir / name)

    scripts_dir = BUNDLE_DIR / "scripts"
    scripts_dir.mkdir()
    copy_file(
        REPO_ROOT / "scripts" / "check_webr_package_abi.cjs",
        scripts_dir / "check_webr_package_abi.cjs",
    )

    workflow_dir = BUNDLE_DIR / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    copy_file(
        REPO_ROOT / ".github" / "workflows" / "release-webr-r-env.yml",
        workflow_dir / "release-webr-r-env.yml",
    )

    write_release_notes(BUNDLE_DIR / "RELEASE_NOTES.txt")

    if ARCHIVE_PATH.exists():
        ARCHIVE_PATH.unlink()
    with zipfile.ZipFile(ARCHIVE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(BUNDLE_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(BUNDLE_DIR.parent))

    print(f"Wrote {ARCHIVE_PATH}")


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_release_notes(path: Path) -> None:
    path.write_text(
        f"""Pixelgen R Browser Lab {VERSION}

This local archive contains the browser R console and the webR package release
metadata. The GitHub Actions workflow included here is what compiles the actual
WebAssembly R package repository and webR library bundle for GitHub Releases.

Open:
  pixelgen-r-console-{VERSION}.html

After the workflow has created a release, download and mount:
  pixelgen-report-webr-library-{VERSION}.zip

or mount both:
  pixelgen-report-webr-library-{VERSION}.data.gz
  pixelgen-report-webr-library-{VERSION}.js.metadata
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
