"""Final demo: GAMMA 0101 OCT → microscope render all features."""
import os, sys, cv2, numpy as np
sys.path.insert(0, "MedSim-main")

import plugins
from medsim.core.context import Context
from medsim.pipeline.runner import Pipeline
from medsim.core.mesh import Mesh
from medsim.core.scene import Scene, SceneNode
from medsim.runtime.registry import make_component

OUT = "outputs/final_demo"
os.makedirs(OUT, exist_ok=True)

# Run official OCT pipeline on GAMMA 0101
print("OCT pipeline...")
ctx = Context(cfg={"params": {"oct_path": "datasets/gamma/bscan_png/0101",
                               "oct_fov_mm": [6.0, 6.0], "z_scale": 0.15}}, out_dir=OUT)
ctx = Pipeline(["oct.load", "oct.preprocess", "oct.surface_detect", "oct.enface_fuse", "oct.resize"]).run(ctx)

hm = ctx.data["heightmap"]; H, W = hm.shape
# Invert heightmap so fovea is depression
z_vals = (hm.max() - hm.astype(np.float32)) * 0.15

ji, ii = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
verts = np.stack([ji.ravel() - W / 2, ii.ravel() - H / 2, z_vals.ravel()], axis=-1).astype(np.float32)
_i = np.arange(H - 1, dtype=np.int32).reshape(-1, 1) * np.ones(W - 1, dtype=np.int32)
_j = np.ones(H - 1, dtype=np.int32).reshape(-1, 1) * np.arange(W - 1, dtype=np.int32)
v00 = (_i * W + _j).ravel(); v01 = v00 + 1; v10 = v00 + W; v11 = v10 + 1
faces = np.concatenate([np.stack([v00, v01, v10], axis=-1), np.stack([v01, v11, v10], axis=-1)], axis=0).astype(np.int32)
u = ji.ravel() / max(W - 1, 1.); v = 1. - ii.ravel() / max(H - 1, 1.)
tcoords = np.stack([u, v], axis=-1).astype(np.float32)

fundus = cv2.imread("datasets/gamma/fundus_0101.jpg")
hf, wf = fundus.shape[:2]; sz = min(hf, wf); cx, cy = wf // 2, hf // 2
fc = fundus[cy - sz // 2:cy + sz // 2, cx - sz // 2:cx + sz // 2]
tex = cv2.cvtColor(cv2.resize(fc, (W, H), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)

mesh = Mesh(vertices=verts, faces=faces, tcoords=tcoords, texture=tex)
ctx.scene = Scene(root=SceneNode(id="retina", visual=mesh))

print("Rendering...")
tests = [
    ("1_coaxial_5x", {"magnification": 5.0, "light_mode": "coaxial"}),
    ("2_oblique_5x", {"magnification": 5.0, "light_mode": "oblique"}),
    ("3_redreflex_5x", {"magnification": 5.0, "light_mode": "red-reflex"}),
    ("4_coaxial_10x", {"magnification": 10.0, "light_mode": "coaxial"}),
    ("5_coaxial_20x", {"magnification": 20.0, "light_mode": "coaxial"}),
    ("6_stereo", {"magnification": 5.0, "stereo": True}),
    ("7_gaze_15deg", {"magnification": 5.0, "gaze_yaw": 15.0}),
]
for stem, kw in tests:
    rdr = make_component("microscope.renderer", offscreen=True, out_dir=OUT, ctx=ctx,
                         magnification=kw.get("magnification", 5.0),
                         light_mode=kw.get("light_mode", "coaxial"),
                         stereo=kw.get("stereo", False),
                         gaze_yaw=kw.get("gaze_yaw", 0.0),
                         size=2048, mask_radius=0.95, vignette=0.04, output_stem=stem)
    rdr.add(ctx.scene.root); rdr.render()
    print(f"  {stem}")

# Wireframe — build circular mesh from polar coordinates
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from PIL import Image
from scipy.interpolate import RegularGridInterpolator

# Sample heightmap on a circular polar grid
RADII = 64        # radial rings
ANGLES = 128      # angular segments

r_vals = np.linspace(0, 1, RADII)
t_vals = np.linspace(0, 2 * np.pi, ANGLES, endpoint=False)
rr, tt = np.meshgrid(r_vals, t_vals)

# Map polar → Cartesian for sampling heightmap
hm_h, hm_w = hm.shape
xx_grid = (rr * np.cos(tt) * hm_w/2 + hm_w/2).ravel()
yy_grid = (rr * np.sin(tt) * hm_h/2 + hm_h/2).ravel()

# Interpolate heightmap at these positions
XX, YY = np.meshgrid(np.arange(hm_w, dtype=np.float32), np.arange(hm_h, dtype=np.float32))
interp = RegularGridInterpolator(
    (np.arange(hm_h, dtype=np.float32), np.arange(hm_w, dtype=np.float32)),
    z_vals.astype(np.float64), bounds_error=False, fill_value=0.0)
z_polar = interp(np.column_stack([yy_grid, xx_grid])).reshape(ANGLES, RADII)

# Build mesh from polar grid
cart_x = (rr * np.cos(tt) * hm_w/2).astype(np.float32)
cart_y = (rr * np.sin(tt) * hm_h/2).astype(np.float32)
verts2 = np.stack([cart_x.ravel(), cart_y.ravel(), z_polar.ravel() * 5], axis=-1).astype(np.float32)  # *5 for visibility
W2, H2 = RADII, ANGLES  # (cols=radii, rows=angles)

_i2 = np.arange(H2 - 1, dtype=np.int32).reshape(-1, 1) * np.ones(W2 - 1, dtype=np.int32)
_j2 = np.ones(H2 - 1, dtype=np.int32).reshape(-1, 1) * np.arange(W2 - 1, dtype=np.int32)
v00a = (_i2 * W2 + _j2).ravel(); v01a = v00a + 1; v10a = v00a + W2; v11a = v10a + 1
f2 = np.concatenate([np.stack([v00a, v01a, v10a], axis=-1), np.stack([v01a, v11a, v10a], axis=-1)], axis=0).astype(np.int32)

# Close the polar wrap: connect last angle column to first
for r_idx in range(W2 - 1):
    v0 = (H2 - 1) * W2 + r_idx
    v1 = r_idx
    v2 = (H2 - 1) * W2 + r_idx + 1
    v3 = r_idx + 1
    extra = np.array([[v0, v3, v2], [v0, v1, v3]], dtype=np.int32)
    f2 = np.concatenate([f2, extra], axis=0)

pts2 = vtk.vtkPoints(); pts2.SetData(numpy_to_vtk(verts2.astype(np.float32), deep=True))
c2 = vtk.vtkCellArray(); c2.SetData(
    numpy_to_vtkIdTypeArray(np.arange(0, 3 * (len(f2) + 1), 3, dtype=np.int64), deep=True),
    numpy_to_vtkIdTypeArray(f2.astype(np.int64).ravel(), deep=True))
p2 = vtk.vtkPolyData(); p2.SetPoints(pts2); p2.SetPolys(c2)
m2 = vtk.vtkPolyDataMapper(); m2.SetInputData(p2); m2.ScalarVisibilityOff()
a2 = vtk.vtkActor(); a2.SetMapper(m2); a2.GetProperty().SetRepresentationToWireframe(); a2.GetProperty().SetColor(1, 1, 1); a2.GetProperty().SetLighting(False)
r2 = vtk.vtkRenderer(); r2.SetBackground(0.05, 0.05, 0.1); r2.AddActor(a2)
cam2 = r2.GetActiveCamera(); cam2.SetFocalPoint(0, 0, z_polar.mean() * 5)
cam2.SetPosition(hm_w * 0.15, -hm_w * 0.25, hm_w * 0.15); cam2.SetViewUp(0, 0, 1); cam2.SetClippingRange(1, hm_w * 5)
rw2 = vtk.vtkRenderWindow(); rw2.SetOffScreenRendering(1); rw2.SetSize(2048, 2048); rw2.AddRenderer(r2)
rw2.Render(); r2.ResetCamera(); rw2.Render()
w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(rw2); w2i.SetInputBufferTypeToRGB(); w2i.Update()
io = w2i.GetOutput()
if io:
    d = io.GetDimensions(); fr = vtk_to_numpy(io.GetPointData().GetScalars()).reshape(d[1], d[0], 3)[::-1].copy()
    Image.fromarray(fr).save(os.path.join(OUT, "8_wireframe_3d.png"))

print(f"\nDone: {OUT}/")
for f in sorted(os.listdir(OUT)):
    sz = os.path.getsize(os.path.join(OUT, f)) / 1024
    print(f"  {f}: {sz:.0f} KB")
