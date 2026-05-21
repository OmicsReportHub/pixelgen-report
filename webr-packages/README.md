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

- `patches/prepare_bpcells_source.py` downloads the `BPCells` `v0.3.1` R
  package source, patches a few HDF5 dimension casts, and disables Clang's
  C++11 narrowing diagnostic for additional HDF5 dimension initializer lists
  that Emscripten rejects during the wasm build. It also removes BPCells'
  duplicate explicit `-lz` link flag because the webR HDF5 flags already supply
  zlib, and adds `hwy/timer.cc` to BPCells' vendored Highway static-library
  build so `BPCells.so` does not leave Highway timer symbols unresolved at
  browser load time.
- `patches/prepare_pixelatorr_source.py` downloads the `pixelatorR` `v0.17.1`
  source release for local webR compilation.
- `patches/rwasm-c17.mk` keeps local builds aligned with webR's compiler
  settings.
- `patches/prepare_png_source.py` patches `png` for webR by replacing its
  CRAN-check-only dummy routine calls. Without this, `png.so` imports
  `R_registerRoutines` and `R_useDynamicSymbols` with an ABI that the browser
  runtime rejects.
