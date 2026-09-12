#!/usr/bin/env python3
"""Generate lightweight GLB visual assets for the browser/Gazebo preview.

These meshes are visual-only. Collision geometry stays in SDF primitives.
Run with: blender --background --python scripts/asset_tools/generate_blender_visuals.py
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets' / 'visual'
OUT.mkdir(parents=True, exist_ok=True)


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

soil = mat('schwerer_brauner_marschboden', (0.34, 0.24, 0.14, 1))
soil_light = mat('trockene_dammkante', (0.50, 0.35, 0.20, 1))
stem_mat = mat('kartoffel_staengel', (0.16, 0.36, 0.11, 1))
leaf_mat = mat('kartoffel_blatt', (0.10, 0.42, 0.12, 1))
weed_mat = mat('unkraut_blatt', (0.22, 0.55, 0.14, 1))


def assign(obj, material):
    obj.data.materials.append(material)
    return obj


def export(name):
    path = OUT / name
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', export_yup=False, export_apply=True)
    return path


def make_leaf(name, loc, rot, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc, rotation=rot)
    leaf = bpy.context.object
    leaf.name = name
    leaf.scale = scale
    assign(leaf, material)
    return leaf


def potato_haulm():
    clear()
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.018, depth=0.32, location=(0, 0, 0.16))
    stem = bpy.context.object
    stem.name = 'potato_haulm_main_stem'
    assign(stem, stem_mat)
    for i, (x, y, z, rz, sx, sy) in enumerate([
        (0.065, 0.020, 0.25, 0.25, 0.105, 0.035),
        (-0.055, 0.030, 0.29, -0.65, 0.095, 0.032),
        (0.020, -0.070, 0.32, 1.15, 0.110, 0.036),
        (0.085, -0.035, 0.38, -0.15, 0.090, 0.030),
        (-0.075, -0.045, 0.36, 0.75, 0.085, 0.028),
        (0.010, 0.060, 0.42, -1.1, 0.075, 0.025),
    ]):
        make_leaf(f'potato_leaf_{i}', (x, y, z), (0.35, 0.15, rz), (sx, sy, 0.010), leaf_mat)
    export('potato_haulm.glb')


def weed():
    clear()
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.006, depth=0.18, location=(0, 0, 0.09))
    assign(bpy.context.object, stem_mat)
    for i, rz in enumerate([0, 2.1, 4.2, 1.2]):
        radius = 0.055 if i < 3 else 0.040
        make_leaf(f'weed_leaf_{i}', (0.025 * math.cos(rz), 0.025 * math.sin(rz), 0.12 + i * 0.018), (0.55, 0.1, rz), (radius, 0.018, 0.007), weed_mat)
    export('weed_broadleaf.glb')


def ridge():
    clear()
    # Low-poly triangular/prismatic ridge, length along X, width Y, height Z.
    mesh = bpy.data.meshes.new('potato_ridge_mesh')
    L, W, H = 3.4, 0.42, 0.15
    verts = [(-L/2, -W/2, 0), (L/2, -W/2, 0), (L/2, W/2, 0), (-L/2, W/2, 0),
             (-L/2, 0, H), (L/2, 0, H)]
    faces = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('rounded_visual_potato_ridge', mesh)
    bpy.context.collection.objects.link(obj)
    assign(obj, soil)
    bevel = obj.modifiers.new('soft_dam_edges', 'BEVEL')
    bevel.width = 0.025
    bevel.segments = 2
    obj.modifiers.new('soft_normals', 'WEIGHTED_NORMAL')
    # small clods as visual surface noise
    for i in range(18):
        x = -L/2 + (i + 0.35) * L / 18
        y = (0.04 if i % 2 else -0.055) * (1 + (i % 3) * 0.15)
        z = H * 0.88
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.022 + 0.004 * (i % 3), location=(x, y, z))
        clod = bpy.context.object
        clod.name = f'ridge_clod_{i}'
        clod.scale.y = 0.65
        assign(clod, soil_light if i % 3 else soil)
    export('potato_ridge_340cm.glb')


potato_haulm()
weed()
ridge()
print('Generated visual assets in', OUT)
