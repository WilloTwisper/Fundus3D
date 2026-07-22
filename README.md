# Fundus3D

2D fundus photograph → 3D textured eye model + surgical microscope rendering.

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
