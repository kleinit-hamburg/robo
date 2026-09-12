#!/usr/bin/env python3
"""Generate GLB visual assets for the browser/Gazebo preview.

Visual-only: collision geometry stays in SDF primitives so Gazebo remains the
physics truth. Run with: blender --background --python scripts/asset_tools/generate_blender_visuals.py
"""
from pathlib import Path
import math
import random
import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets' / 'visual'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(62)


def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def mat(name, color, roughness=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0
    return m

soil = mat('feuchter_marschboden', (0.27, 0.18, 0.10, 1), .96)
soil_mid = mat('damm_erdig', (0.44, 0.30, 0.17, 1), .95)
soil_light = mat('trockene_krume', (0.58, 0.43, 0.26, 1), .93)
stem_mat = mat('kartoffel_staengel', (0.13, 0.31, 0.10, 1), .82)
leaf_mat = mat('kartoffel_blatt', (0.08, 0.34, 0.11, 1), .86)
leaf_light = mat('kartoffel_blatt_hell', (0.18, 0.55, 0.19, 1), .84)
weed_mat = mat('unkraut_blatt', (0.20, 0.50, 0.12, 1), .85)
robot_green = mat('lack_gruen_matt', (0.22, 0.42, 0.25, 1), .72)
rubber = mat('gummi_dunkel', (0.035, 0.045, 0.04, 1), .88)
orange = mat('warnorange', (0.95, 0.42, 0.08, 1), .62)
metal = mat('metall_dunkel', (0.18, 0.20, 0.18, 1), .55)


def assign(obj, material):
    obj.data.materials.append(material)
    return obj


def export(name):
    path = OUT / name
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', export_yup=False, export_apply=True)
    return path


def cube_obj(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel:
        mod = obj.modifiers.new('soft_edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 5
        obj.modifiers.new('weighted_normals', 'WEIGHTED_NORMAL')
    return obj


def cyl_obj(name, loc, radius, depth, material, vertices=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material)
    return obj


def leaf(name, loc, rot, length, width, material, bend=0.015):
    verts = [(0, 0, 0)]
    outline = []
    steps = 6
    for i in range(steps + 1):
        t = i / steps
        x = length * t
        w = width * math.sin(math.pi * t) * (0.85 + 0.15 * math.cos(2 * math.pi * t))
        z = bend * math.sin(math.pi * t)
        outline.append((x, w, z))
    for i in range(steps - 1, -1, -1):
        t = i / steps
        x = length * t
        w = -width * math.sin(math.pi * t) * (0.85 + 0.15 * math.cos(2 * math.pi * t))
        z = bend * math.sin(math.pi * t)
        outline.append((x, w, z))
    verts.extend(outline)
    faces = []
    for i in range(1, len(verts)):
        faces.append((0, i, 1 if i == len(verts) - 1 else i + 1))
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    assign(obj, material)
    return obj


def potato_haulm_variant(filename, phase, height_scale=1.0, spread=1.0):
    clear()
    cyl_obj('main_stem', (0, 0, 0.18 * height_scale), .012, .34 * height_scale, stem_mat, 14)
    branch_angles = [-1.25, -.72, -.25, .35, .92, 1.55]
    for i, a in enumerate(branch_angles):
        x, y, z = .050 * spread * math.cos(a + phase), .050 * spread * math.sin(a + phase), (.19 + .030 * i) * height_scale
        cyl_obj(f'branch_{i}', (x / 2, y / 2, z), .0048, .14 * spread, stem_mat, 10, rot=(1.08, .22, a + phase + math.pi / 2))
    angles = [-1.55, -1.10, -.70, -.32, .05, .42, .80, 1.18, 1.62, 2.10, 2.72]
    for i, a in enumerate(angles):
        aa = a + phase + .10 * math.sin(i)
        r = (.045 + .012 * (i % 4)) * spread
        z = (.20 + .021 * i + .006 * math.sin(i * 1.7)) * height_scale
        length = (.105 + .018 * ((i + 1) % 3)) * spread
        width = (.030 + .006 * (i % 3)) * spread
        loc = (r * math.cos(aa), r * math.sin(aa), z)
        rot = (.38 + .08 * (i % 2), .10 * math.sin(i), aa)
        leaf(f'leaf_{i}', loc, rot, length, width, leaf_light if i % 5 == 0 else leaf_mat, bend=.010 + .004 * (i % 3))
    export(filename)


def potato_haulm():
    potato_haulm_variant('potato_haulm.glb', 0.0, 1.00, 1.00)
    potato_haulm_variant('potato_haulm_b.glb', 0.55, .88, 1.12)
    potato_haulm_variant('potato_haulm_c.glb', -0.42, 1.10, .92)


def weed():
    clear()
    cyl_obj('weed_stem', (0, 0, .08), .005, .16, stem_mat, 10)
    for i, a in enumerate([0, 1.4, 2.8, 4.2, 5.3]):
        leaf(f'weed_leaf_{i}', (.020 * math.cos(a), .020 * math.sin(a), .10 + .018 * i), (.60, .08, a), .060 if i < 3 else .045, .018, weed_mat, bend=.006)
    export('weed_broadleaf.glb')


def ridge():
    clear()
    L, W, H = 3.4, 0.44, 0.15
    xs = [(-L / 2) + i * L / 34 for i in range(35)]
    ys = [-W / 2, -W * .32, 0, W * .32, W / 2]
    verts = []
    for x in xs:
        for y in ys:
            crown = H * (1 - min(1, abs(y) / (W / 2)) ** 1.7)
            z = max(0, crown + 0.010 * math.sin(9 * x + 21 * y) + 0.006 * math.sin(17 * x))
            verts.append((x, y, z))
    faces = []
    cols = len(ys)
    for i in range(len(xs) - 1):
        for j in range(cols - 1):
            a = i * cols + j
            faces.append((a, a + 1, a + cols + 1, a + cols))
    mesh = bpy.data.meshes.new('irregular_potato_ridge_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('irregular_visual_potato_ridge', mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, soil_mid)
    obj.modifiers.new('weighted_normals', 'WEIGHTED_NORMAL')
    for i in range(42):
        x = random.uniform(-L / 2, L / 2)
        y = random.uniform(-W * .30, W * .30)
        z = H * (1 - min(1, abs(y) / (W / 2)) ** 1.7) + .018
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=5, radius=random.uniform(.010, .028), location=(x, y, z))
        clod = bpy.context.object
        clod.name = f'crumb_{i}'
        clod.scale.y = random.uniform(.55, 1.3)
        assign(clod, soil_light if i % 4 else soil)
    export('potato_ridge_340cm.glb')


def soil_patch():
    clear()
    L, W = 6.0, 4.0
    nx, ny = 70, 46
    verts = []
    for i in range(nx):
        x = -L / 2 + i * L / (nx - 1)
        for j in range(ny):
            y = -W / 2 + j * W / (ny - 1)
            z = 0.004 * math.sin(8 * x) * math.cos(7 * y) + 0.002 * math.sin(23 * x + 11 * y)
            verts.append((x, y, z))
    faces = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a = i * ny + j
            faces.append((a, a + 1, a + ny + 1, a + ny))
    mesh = bpy.data.meshes.new('soil_surface_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('visual_soil_surface', mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, soil)

    for k, y in enumerate([-0.62, 0.0, 0.62]):
        strip = cube_obj(f'darker_furrow_{k}', (0, y, .004), (5.8, .045, .006), soil, .004)
        strip.rotation_euler.z = .015 * (k - 1)
    for i in range(95):
        x = random.uniform(-2.8, 2.8)
        y = random.uniform(-1.85, 1.85)
        if abs(y - .31) < .24 or abs(y + .31) < .24:
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=random.uniform(.006, .020), location=(x, y, random.uniform(.004, .016)))
        crumb = bpy.context.object
        crumb.name = f'field_crumb_{i}'
        crumb.scale.y = random.uniform(.55, 1.6)
        assign(crumb, soil_light if i % 5 == 0 else soil)
    export('soil_patch_6x4.glb')


def tracked_shell():
    clear()
    cube_obj('rounded_body_shell', (0, 0, .30), (.64, .38, .22), robot_green, .045)
    cube_obj('front_tool_panel', (.33, 0, .28), (.035, .26, .08), orange, .010)
    cube_obj('sensor_mast', (.08, 0, .52), (.045, .045, .22), metal, .012)
    cyl_obj('lidar_head', (.08, 0, .65), .055, .045, metal, 32)
    for side, y in [('left', .31), ('right', -.31)]:
        cube_obj(f'{side}_rubber_track_visual', (0, y, .13), (.82, .12, .20), rubber, .035)
        for k in range(12):
            x = -.36 + k * .065
            cube_obj(f'{side}_tread_{k}', (x, y, .245), (.035, .135, .018), rubber, .004)
    export('tracked_robot_shell.glb')


potato_haulm()
weed()
ridge()
soil_patch()
tracked_shell()
print('Generated visual assets in', OUT)
