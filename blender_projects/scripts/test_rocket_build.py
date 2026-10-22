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


hull_mat = make_material(
    "RocketHull", (0.9, 0.9, 0.95, 1.0), metallic=0.3, roughness=0.2
)
accent_mat = make_material(
    "RedAccent", (0.85, 0.1, 0.1, 1.0), metallic=0.4, roughness=0.3
)
thruster_mat = make_material(
    "ThrusterGlow", (1.0, 0.5, 0.1, 1.0), emission=(1.0, 0.4, 0.05, 1.0)
)

# Body
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.8, location=(0, 0, 1.1))
body_obj = bpy.context.active_object
body_obj.data.materials.append(hull_mat)

# Nose Cone
bpy.ops.mesh.primitive_cone_add(
    radius1=0.4, radius2=0.0, depth=0.8, location=(0, 0, 2.4)
)
nose = bpy.context.active_object
nose.data.materials.append(accent_mat)

# Fins (3 fins)
for angle in [0, 120, 240]:
    rad = math.radians(angle)
    x = 0.45 * math.cos(rad)
    y = 0.45 * math.sin(rad)
    bpy.ops.mesh.primitive_cube_add(size=0.4, location=(x, y, 0.4))
    fin = bpy.context.active_object
    fin.scale = (0.05, 0.35, 0.4)
    fin.rotation_euler = (0, 0, rad)
    fin.data.materials.append(accent_mat)

# Exhaust nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.2, location=(0, 0, 0.1))
nozzle = bpy.context.active_object
nozzle.data.materials.append(thruster_mat)

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
    filepath="C:/Users/User/.gemini/antigravity/scratch/local_ai_gui/blender_projects/test_rocket.blend"
)

# Render Preview
bpy.context.scene.render.filepath = "C:/Users/User/.gemini/antigravity/scratch/local_ai_gui/blender_projects/previews/test_rocket.png"
bpy.context.scene.render.image_settings.file_format = "PNG"
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
try:
    bpy.ops.render.render(write_still=True)
except Exception as e:
    print("Render warning:", e)
