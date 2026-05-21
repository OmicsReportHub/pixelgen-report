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
choose the files. They are copied into the webR session under
`/pixelgen-data`, for example:

```r
counts <- read.csv("/pixelgen-data/counts.csv", check.names = FALSE)
metadata <- read.delim("/pixelgen-data/metadata.tsv", check.names = FALSE)
```

## Package Manifests

- `webr-packages/packages` is the default browser package set plus its explicit
  runtime dependency closure used by the release workflow.
- `webr-packages/packages.pixi-full` records the R dependencies from the source
  Pixi feature for traceability. Some of those packages have native system
  dependencies and may not compile cleanly for webR without extra patching.
- `webr-packages/packages.graph-experimental` keeps `igraph`, `tidygraph`, and
  `ggraph` separate because `igraph` did not appear in the generated webR
  package index during the first release attempt.

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
