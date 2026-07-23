# Fundus3D

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Convert a 2D fundus (retinal) photograph into a textured 3D eye model using schematic eye optics (Navarro 1985) and camera projection.**

Fundus3D bridges the gap between clinical 2D fundus imaging and 3D anatomical visualization. Given a single fundus photo (e.g., from ODIR-5K or HRF datasets), it reconstructs a anatomically-grounded 3D eye model by back-projecting the 2D image onto a schematic retinal surface using clinically validated optical models.

## Features

- **Schematic Eye Models**: Navarro (aspheric, clinically validated), Simplified (spherical), Custom (pathological)
- **Camera Models**: Pinhole (standard fundus camera, 45° FOV) and Widefield (equisolid-angle, up to 200° FOV)
- **Two Mesh Modes**: Retinal patch (FOV cap only) or full anatomical eye with 9 layers
- **Snell Refraction Correction**: Optional ray refraction at corneal surface
- **Export Formats**: GLB (glTF 2.0 with PBR materials) and OBJ with MTL
- **Named Anatomical Layers**: Sclera, cornea, iris, lens, retina, choroid, ciliary body, optic nerve, vitreous
- **Microscope Renderer**: Surgical-microscope view simulator with coaxial/oblique/red-reflex illumination and stereo pairs

## Pipeline

```
fundus photo → preprocess (circle detection, alpha mask)
    → schematic eye model (Navarro 1985)
    → camera projection (pinhole / widefield)
    → UV mapping onto retinal surface
    → texture atlas (fundus + generic retina + sclera)
    → .glb export with named anatomical layers
```

## Quick Start

```bash
# Basic: generate a retinal patch (.glb)
python -m fundus3d photo.jpg -o eye.glb

# Full anatomical eye with adjustable parameters
python -m fundus3d photo.jpg -o eye.glb \
    --mesh-mode full --resolution 4 \
    --axial-length 24.0 --equatorial-diameter 24.0 \
    --camera pinhole --fov 45

# Surgical microscope rendering
python -m microscope eye.glb --light oblique -o view.png
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--mesh-mode` | `patch` | `patch` (FOV cap only) or `full` (complete eye with layers) |
| `--camera` | `pinhole` | `pinhole` (45°) or `widefield` (200° equisolid) |
| `--eye-model` | `navarro` | `navarro` \| `simplified` \| `custom` |
| `--axial-length` | 24.0 | Eye axial length in mm (20–32 mm) |
| `--equatorial-diameter` | 24.0 | Equatorial diameter in mm (22–28 mm) |
| `--fov` | 45 / 200 | Field of view in degrees |
| `--resolution` | 4 | Mesh subdivision level (0–7) |
| `--refraction` | off | Enable Snell refraction correction at cornea |
| `--left-eye` | off | Mark as left eye (flips landmark offsets) |
| `--clip` | off | Cut-away view (exposes interior layers) |
| `--vitreous` | off | Show semi-transparent vitreous body |
| `--output` / `-o` | auto | Output path (.glb or .obj) |
| `--format` | `glb` | `glb` or `obj` |

## Eye Models

### Navarro (1985) — Default
Clinically validated schematic eye with aspheric corneal surfaces (conic constant ≈ -0.26), gradient-index lens, and ~24 mm axial length (emmetropic). Adjustable for myopia/hyperopia.

> Navarro R, Santamaría J, Bescós J. "Accommodation-dependent model of the human eye with aspherics." *JOSA A*, 2(8):1273-1281, 1985.

### Simplified
Spherical approximation with constant refractive index lens. Fast prototyping, less anatomically accurate.

### Custom
User-specified segment lengths for pathological eye shapes (high myopia, staphyloma).

## Camera Models

### Pinhole
Standard perspective projection. Focal length derived from image size and FOV. Default FOV: 45° (typical fundus camera).

### Widefield
Equisolid-angle projection (f = R / 2sin(θ/2)). Suitable for widefield/ultra-widefield fundus imaging. Default FOV: 200°.

## Datasets

- **ODIR-5K**: 5000 paired left/right fundus images, preprocessed to 512×512
- **HRF**: High-resolution fundus images (3504×2336) with FOV masks

## Project Structure

```
fundus3d/
├── fundus3d/                # Main package
│   ├── __init__.py          # Public API (Pipeline, preprocess_fundus)
│   ├── pipeline.py          # End-to-end pipeline orchestration
│   ├── preprocessing.py     # Circle detection, alpha mask, texture atlas
│   ├── eye/                 # Schematic eye models
│   │   ├── models.py        # NavarroEye, SimplifiedEye, CustomEye
│   │   └── mesh.py          # Eye mesh generation (patch & full)
│   ├── camera/              # Camera projection models
│   │   ├── base.py          # CameraModel base class
│   │   ├── pinhole.py       # PinholeCamera (45°)
│   │   ├── widefield.py     # WidefieldCamera (200°)
│   │   └── refraction.py    # Snell refraction correction
│   ├── projection/          # UV mapping
│   │   └── mapper.py        # project_image_to_mesh
│   └── export/              # 3D export
│       └── exporter.py      # GLB & OBJ export
├── microscope/              # Surgical microscope renderer
├── run_final_demo.py        # OCT → microscope demo pipeline
├── README.md
└── AGENTS.md                # Development notes
```

## Installation

```bash
pip install numpy opencv-python trimesh
```

## License

MIT

## Author

Jialiang Liu — SUSTech
