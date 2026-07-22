# Fundus3D — Project Context

## Overview

Fundus3D converts a single 2D fundus (retinal) photograph into a textured 3D
eye model suitable for visualization, simulation, and export.

The core idea: a schematic model of the human eye provides the 3D retinal
surface geometry, and a camera model back-projects the 2D image pixels
onto that surface through the eye's optics.

## Schematic Eye Models

Three models are implemented, all based on published anatomical data:

### Navarro (1985) — Default
*Navarro R, Santamaría J, Bescós J. "Accommodation-dependent model of the
human eye with aspherics." JOSA A, 2(8):1273-1281, 1985.*

- Aspheric corneal surfaces (conic constant ≈ -0.26)
- Gradient-index lens
- Clinically validated for visual optics research
- Axial length ~24 mm (emmetropic), adjustable for myopia/hyperopia
- Anterior segment length: ~12 mm

### Simplified
- Spherical approximation
- Constant refractive index lens
- Fast prototyping, less anatomically accurate

### Custom
- User-specified segment lengths
- Useful for pathological eye shapes (high myopia, staphyloma)

## Camera Models

### Pinhole Camera
- Standard perspective projection
- Focal length derived from image size and FOV
- Default FOV: 45° (typical fundus camera)

### Widefield Camera
- Equisolid-angle projection (f = R / 2sin(θ/2))
- Suitable for widefield/ultra-widefield fundus imaging
- Default FOV: 200°

## Pipeline

```
1. Preprocessing
   - Detect fundus circle via Hough transform / thresholding
   - Create alpha mask (circular or from FOV mask image)
   - Generate texture atlas (fundus photo + generic retina fill + sclera)

2. Eye Model Generation
   - Build schematic eye geometry from parameters
   - Two mesh modes:
     a) Patch: retinal spherical cap matching camera FOV
     b) Full: complete eye with layers (sclera, cornea, iris, lens,
        retina, choroid, ciliary body, optic nerve, vitreous)

3. Camera Projection
   - Map image pixels → 3D rays through the eye
   - Compute UV coordinates for retinal vertices
   - Optional Snell refraction correction at corneal surface

4. Export
   - GLB (glTF 2.0 binary) with PBR materials
   - OBJ with MTL
   - Named anatomical layers for selective rendering
```

## Datasets Used

- **ODIR-5K**: 5000 paired left/right fundus images, preprocessed to 512×512
- **HRF**: High-resolution fundus images (3504×2336) with FOV masks

## Parameters

| Parameter | Range | Meaning |
|-----------|-------|---------|
| `axial_length` | 20–32 mm | Eye length (24=emmetropic, >26=myopic) |
| `equatorial_diameter` | 22–28 mm | Width at equator |
| `fov_deg` | 20–200° | Camera field of view |
| `mesh_resolution` | 0–7 | Subdivision level (higher = finer) |

## Key References

- Navarro R et al. (1985) — Schematic eye model with aspherics
- Atchison DA et al. (2004) — Eye shape changes with myopia (axial elongation
  with preserved equatorial diameter)
- Equisolid-angle projection for widefield fundus cameras
