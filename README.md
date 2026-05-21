# Pixelgen R Browser Lab

This repository packages a small browser-side R console for the Pixelgen CAR-T
analysis environment. It follows the webR release strategy used by
`rnaseq-report`: build a versioned WebAssembly R package repository, turn that
repository into a browser-loadable webR library bundle, and upload the compiled
files as GitHub Release assets.

The default scope is the R portion of the Pixelgen Pixi environment only. It
does not build or host the Python analysis environment.

## Local HTML

Open `index.html` in a browser to start webR, write R code, and capture plots.
The page can:

- initialize webR from the pinned runtime
- install packages from a configured webR package repository
- mount a downloaded webR library bundle ZIP or `.data.gz` plus `.js.metadata`
- run R code with console output and captured canvas plots

If a browser blocks webR workers from `file://`, open the file through a local
static server instead:

```bash
python3 -m http.server 8000
```

Then visit:

```text
http://127.0.0.1:8000/
```

## Release Assets

The manual workflow `.github/workflows/release-webr-r-env.yml` creates a GitHub
Release named like:

```text
pixelgen-report-webr-r-env-v0.1.0
```

Release downloads include:

- `pixelgen-r-console-v0.1.0.html`
- `pixelgen-report-webr-packages-v0.1.0.zip`
- `pixelgen-report-webr-library-v0.1.0.zip`
- `pixelgen-report-webr-library-v0.1.0.data.gz`
- `pixelgen-report-webr-library-v0.1.0.js.metadata`
- `pixelgen-report-webr-packages-v0.1.0.txt`

Use the library ZIP in the HTML page's "Mount bundle" control to load the
compiled packages without reinstalling during that browser session.

To read local analysis files in the browser, click "Mount local files" and
choose the files. They are mounted read-only into the webR session and the path
is stored as `pixelgen_data_dir`. Mounting does not copy the whole file into
webR first, but R still needs browser memory for the data it reads. For larger
raw matrices, split or pre-filter the file first, or run that part in local R.

Example:

```r
list.files(pixelgen_data_dir)
counts <- read.csv(file.path(pixelgen_data_dir, "counts.csv"), check.names = FALSE)
metadata <- read.delim(file.path(pixelgen_data_dir, "metadata.tsv"), check.names = FALSE)
```

The browser bundle includes the webR-compatible part of the Pixelgen R list:
`dplyr`, `stringr`, `BPCells`, `pixelatorR`, `SeuratObject`, `ggplot2`,
`tidyr`, `tibble`, `patchwork`, `limma`, `ggridges`, `readr`, `harmony`,
`pheatmap`, and the existing browser plotting/table helpers. `BPCells` is built
from the `bnprks/BPCells` `v0.3.1` R package source because it is not in the
official webR binary package index. `pixelatorR` is built from the
`PixelgenTechnologies/pixelatorR` `v0.17.1` source release.

`Seurat` is not included in the browser bundle. Its current CRAN webR package
depends on `reticulate` and `uwot`, and those dependencies are not available in
the webR package index used by the browser runtime. `SeuratDisk` is also not
included because it imports `Seurat`. Run Seurat/SeuratDisk workflows in local R,
then load exported CSV/TSV/RDS summaries in this page for plotting or lighter
downstream checks.

## Package Manifests

- `webr-packages/packages` is the default browser package set plus its explicit
  runtime dependency closure used by the release workflow.
- `webr-packages/packages.pixi-full` records the R dependencies from the source
  Pixi feature for traceability. Some of those packages have native system
  dependencies and may not compile cleanly for webR without extra patching.
- `webr-packages/packages.graph-experimental` records the older isolated graph
  stack build attempt. The default manifest now includes the graph stack because
  it is required by `pixelatorR`.

To attempt a fuller build, run the workflow manually with:

```text
package_file = webr-packages/packages.pixi-full
```

## Local Release Bundle

To make a small downloadable bundle containing the HTML and release metadata:

```bash
python3 scripts/build_release_bundle.py
```

The archive is written to `dist/`.
