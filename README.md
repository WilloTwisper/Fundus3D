# Fundus3D

Convert a 2D fundus photograph into a 3D textured eye model using schematic eye
optics (Navarro 1985) and camera projection.

## Quick Start

```bash
# Basic: generate a retinal patch (.glb)
python -m fundus3d photo.jpg -o eye.glb

# Full anatomical eye with adjustable parameters
python -m fundus3d photo.jpg -o eye.glb \
    --mesh-mode full --resolution 4 \
    --axial-length 24.0 --equatorial-diameter 24.0 \
    --camera pinhole --fov 45
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--mesh-mode` | `patch` | `patch` (FOV cap only) or `full` (complete eye with layers) |
| `--camera` | `pinhole` | `pinhole` (45°) or `widefield` (200° equisolid) |
| `--eye-model` | `navarro` | `navarro` \| `simplified` \| `custom` |
| `--axial-length` | 24.0 | Eye axial length in mm |
| `--equatorial-diameter` | 24.0 | Equatorial diameter in mm |
| `--fov` | 45 / 200 | Field of view in degrees |
| `--resolution` | 4 | Mesh subdivision level (0-7) |
| `--fov-mask` | — | Path to FOV mask image |
| `--refraction` | off | Enable Snell refraction correction at cornea |
| `--left-eye` | off | Mark as left eye (flips landmark offsets) |
| `--clip` | off | Cut-away view (exposes interior layers) |
| `--vitreous` | off | Show semi-transparent vitreous body |
| `--disc-offset` | — | Optic disc 3D offset "x,y" in mm |
| `--output` / `-o` | auto | Output path (.glb or .obj) |
| `--format` | `glb` | `glb` or `obj` |

## How It Works

```
fundus photo → preprocess (circle detection, alpha mask)
    → schematic eye model (Navarro)
    → camera projection (pinhole / widefield)
    → UV mapping onto retinal surface
    → texture atlas
    → .glb export with named anatomical layers
```

The schematic eye model controls retinal surface geometry:
- **Navarro** (default): Aspheric/ellipsoidal surface, clinically validated
- **Simplified**: Spherical approximation for fast prototyping
- **Custom**: User-specified segment lengths

## Companion: Microscope Renderer

A surgical-microscope view renderer is included in `microscope/`. It loads
`.glb` files produced by `fundus3d` and renders them through virtual optics
with coaxial/oblique/red-reflex illumination, stereo pairs, and magnification.

```bash
python -m microscope eye.glb --light oblique -o view.png
```
