# Pixelgen webR R Environment

This directory defines the downloadable R package release used by
`index.html`.

It follows the same contract as `rnaseq-report`, but without publishing a
GitHub Pages package snapshot:

1. Read a version from `VERSION`.
2. Read package refs from `packages`.
3. Build a webR package repository with `r-wasm/actions`.
4. Archive the repository as a release ZIP.
5. Convert the repository into a browser-loadable webR library bundle.
6. Upload the HTML page, package ZIP, and library bundle files to a GitHub
   Release.

The library bundle is the most convenient file for interactive browser use. In
`index.html`, use **Mount bundle** and choose:

```text
pixelgen-report-webr-library-v0.1.0.zip
```

or choose both:

```text
pixelgen-report-webr-library-v0.1.0.data.gz
pixelgen-report-webr-library-v0.1.0.js.metadata
```

The mounted library is session-scoped browser state. Mount it again after a
browser refresh.

## webR Build Patches

- `patches/rwasm-c17.mk` keeps local builds aligned with webR's compiler
  settings.
- `patches/prepare_png_source.py` patches `png` for webR by replacing its
  CRAN-check-only dummy routine calls. Without this, `png.so` imports
  `R_registerRoutines` and `R_useDynamicSymbols` with an ABI that the browser
  runtime rejects.
