import math

import bpy

# Clean scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()


def make_material(name, color, metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 5.0
    return mat


neon_mat = make_material(
    "SciFiCyan",
    (0.0, 0.9, 1.0, 1.0),
    metallic=0.1,
    roughness=0.1,
    emission=(0.0, 0.8, 1.0, 1.0),
)
dark_mat = make_material(
    "PedestalMetal", (0.08, 0.08, 0.1, 1.0), metallic=0.85, roughness=0.3
)

# Crystal Cluster
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6, radius=0.3, depth=1.6, location=(0, 0, 0.9)
)
c1 = bpy.context.active_object
c1.scale = (0.7, 0.7, 1.2)
c1.data.materials.append(neon_mat)

for i, angle in enumerate([60, 180, 300]):
    rad = math.radians(angle)
    x = 0.35 * math.cos(rad)
    y = 0.35 * math.sin(rad)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=0.18, depth=0.9, location=(x, y, 0.5)
    )
    shard = bpy.context.active_object
    shard.rotation_euler = (0.2 * math.cos(rad), 0.2 * math.sin(rad), rad)
    shard.data.materials.append(neon_mat)

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8, radius=0.9, depth=0.2, location=(0, 0, 0.1)
)
base = bpy.context.active_object
base.data.materials.append(dark_mat)

# Setup Lighting
light_data = bpy.data.lights.new(name="MainSun", type="SUN")
light_data.energy = 4.0
light_obj = bpy.data.objects.new(name="MainSun", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (5.0, -5.0, 8.0)
light_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(45))

# Fill Light
fill_data = bpy.data.lights.new(name="FillLight", type="POINT")
fill_data.energy = 150.0
fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-4.0, -4.0, 4.0)

# Setup Camera
cam_data = bpy.data.cameras.new(name="Camera")
cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (4.5, -4.5, 3.2)
cam_obj.rotation_euler = (math.radians(60), 0, math.radians(45))

# Save Blend file
bpy.ops.wm.save_as_mainfile(
    filepath="C:/Users/User/.gemini/antigravity/scratch/local_ai_gui/blender_projects/live_cyber_crystal.blend"
)

# Render Preview (skip if live GUI or catch safely)
bpy.context.scene.render.filepath = "C:/Users/User/.gemini/antigravity/scratch/local_ai_gui/blender_projects/previews/live_cyber_crystal.png"
bpy.context.scene.render.image_settings.file_format = "PNG"
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
try:
    if bpy.app.background:
        bpy.ops.render.render(write_still=True)
except Exception as e:
    print("Render warning:", e)

# Switch 3D Viewport to Material Preview mode for live interactive viewing
try:
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.shading.type = "MATERIAL"
except Exception:
    pass
