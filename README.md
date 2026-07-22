# Fundus3D

2D fundus photograph → 3D textured eye model → surgical microscope rendering.

## Demo

```bash
# Generate eye model
python -m fundus3d datasets/preprocessed_images/10_left.jpg -o eye.glb --mesh-mode full

# Render microscope views
python -m microscope eye.glb --light coaxial -o coaxial.png
python -m microscope eye.glb --light oblique  -o oblique.png
python -m microscope eye.glb --light red-reflex -o redreflex.png
```

### Example Output (10_left.jpg → 3D model → microscope)

| Coaxial | Oblique | Red Reflex |
|---------|---------|------------|
| coaxial shadowless view | oblique reveals 3D surface | warm illumination |

> Screenshots generated at 1024×1024, magnification 5×, mask radius 0.95.

## Modules

### fundus3d
Convert a fundus photo to a 3D eye model (`.glb`).

```bash
python -m fundus3d <image.jpg> -o output.glb
#    --mesh-mode full          complete eye with anatomical layers
#    --camera pinhole          pinhole (45°) or widefield (200°)
#    --axial-length 24.0       eye axial length in mm
#    --resolution 4            mesh subdivision 0–7
#    --fov-mask mask.tif       FOV mask image
```

### microscope
Render surgical-microscope views of Fundus3D eye models.

```bash
python -m microscope model.glb -o output.png
#    --magnification 5        5–25×
#    --light coaxial          coaxial | oblique | red-reflex
#    --stereo                 stereo pair
#    --gaze 10,-5             pitch,yaw in degrees
#    --video --sway 20        gaze-sweep video
#    --size 2048              output resolution
```

## Pipeline
```
fundus photo → preprocess → eye model → camera projection → UV mapping → .glb export
                                                                    ↓
                                                          microscope renderer
                                                          (coaxial/oblique/red-reflex,
                                                           stereo, magnification,
                                                           gaze, circular mask)
```
