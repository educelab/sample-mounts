# Sample Mounts

3D-printable sample mounts (scroll cases, interface plates, spindles, and
trays) for scanner and beamline data acquisition.

User docs: https://educelab.github.io/sample-mounts/

## Models

Ready-to-print STLs. Variants are named after the parameters they were
rendered with (e.g. `SpindleBase-6.35mm.stl`, `SI Interface Plate - 200mm.stl`).

- **Mount discs and rings.** The standard base (`Generic Mount Disc`, and a
  65 mm version) and the ring it mates with.
- **Interface plates.** Adapt the mount disc to a specific scanner or
  beamline stage (SkyScan 1273, I12.EH1, SI).
- **Spindles.** Spindle bases and stoppers for several rod diameters.

## OpenSCAD

Parametric sources for the models. Parameters are top-level variables and can
be overridden on the command line:

```bash
openscad -o out.stl -D rod_type=2 "OpenSCAD/Spindle Base.scad"
```

Interface plates and spindle bases are built on `Generic Mount Disc*.scad`,
so changing the disc changes all of them.

`Fragment Trays.scad` and `Hanging Frame Case.scad` depend on
`Diamond Interface Plate.scad`, which isn't in this repo, so they won't render
as-is.

## scrollcase

Python generator for split scroll cases fit to a scroll mesh. Requires
[uv](https://docs.astral.sh/uv/):

```bash
cd scrollcase
uv run scrollcase defaults --style educelab.v1 > my-scroll.toml
uv run scrollcase build -c my-scroll.toml -o out/
```

See [Creating a scroll case](docs/creating-scroll-case.md) and the
[config reference](docs/scroll-case-config.md).

## utils

`SpiralLength.cpp` computes the length of an Archimedean spiral for use with
`Spiral Frame.scad`. It needs [GSL](https://www.gnu.org/software/gsl/):

```bash
cmake -S utils -B build && cmake --build build
```

## Docs

The user docs in `docs/` are built with MkDocs and published to GitHub Pages
on every push to `main`. To preview locally:

```bash
uvx --with mkdocs-material --with 'mkdocs<2' mkdocs serve
```

## License

AGPL-3.0. The scroll case's alignment and mesh pipeline are adapted from
[ScrollPrize/villa](https://github.com/ScrollPrize/villa/tree/main/foundation/scrollcase)
(MIT); see `scrollcase/src/scrollcase/LICENSE.villa`.
