# Changelog

## 1.11.0 — 2026-10-19

- Share one implementation between the existing Polish and English entry points.
- Validate ASCII HEX digits and show an inline error instead of ignoring malformed input or crashing on Unicode digits.
- Accept three- or six-digit HEX colors with an optional # prefix; normalize copied values to #RRGGBB.
- Keep the preview, RGB sliders and manual value synchronized; initialize the preview to black.
- Replace the invalid Tkinter pip requirement with standard-library setup instructions.
- Add regression tests and verified PL/EN Windows executables with checksums and build provenance.

The 1.11.0 version follows the historical release label “Hex color v1.10”.
