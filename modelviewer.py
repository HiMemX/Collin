import pyhotools
import ursina as urs
from ursina.prefabs.first_person_controller import FirstPersonController
import threading
import random
import time
import math
import numpy
import frame

class orbit_object(urs.Entity):
    def input(self, key):
        global grab_mode, scale_mode
        if key == 'scroll down':
            self.position += self.forward
            
        if key == 'scroll up':
            self.position += -self.forward
            
        if key == "f":
            self.position = models[selected_object].position
        
        if key == 'g':
            scale_mode = False
            grab_mode = True
            
        if key == 's':
            grab_mode = False
            scale_mode = True
        
        if key == 'left mouse down':
            grab_mode = False
            scale_mode = False
        
    def update(self):
        global fade_out_timer, fade_out_timer_set, axis, axistext, axis_pointers, grab_mode, scale_mode
        
        if selected_object != None and not grab_mode and not scale_mode:
            try:
                models[selected_object].position = (float(input_pos_x.text), models[selected_object].position[1], models[selected_object].position[2])
                models[selected_object].position = (models[selected_object].position[0], float(input_pos_y.text), models[selected_object].position[2])
                models[selected_object].position = (models[selected_object].position[0], models[selected_object].position[1], float(input_pos_z.text))
                
                models[selected_object].rotation = (float(input_rot_x.text), models[selected_object].rotation[1], models[selected_object].rotation[2])
                models[selected_object].rotation = (models[selected_object].rotation[0], float(input_rot_y.text), models[selected_object].rotation[2])
                models[selected_object].rotation = (models[selected_object].rotation[0], models[selected_object].rotation[1], float(input_rot_z.text))
                
                models[selected_object].scale = (float(input_scl_x.text), models[selected_object].scale[1], models[selected_object].scale[2])
                models[selected_object].scale = (models[selected_object].scale[0], float(input_scl_y.text), models[selected_object].scale[2])
                models[selected_object].scale = (models[selected_object].scale[0], models[selected_object].scale[1], float(input_scl_z.text))
                
                models[selected_object].mass = mass_slider.value
                models[selected_object].friction = friction_slider.value
        
            except:
                pass
        
        if selected_object != None and (grab_mode or scale_mode):
            input_pos_x.text = str(round(models[selected_object].position[0]*1000)/1000)
            input_pos_y.text = str(round(models[selected_object].position[1]*1000)/1000)
            input_pos_z.text = str(round(models[selected_object].position[2]*1000)/1000)
            
            input_rot_x.text = str(round(models[selected_object].rotation[0]*1000)/1000)
            input_rot_y.text = str(round(models[selected_object].rotation[1]*1000)/1000)
            input_rot_z.text = str(round(models[selected_object].rotation[2]*1000)/1000)
            
            input_scl_x.text = str(round(models[selected_object].scale[0]*1000)/1000)
            input_scl_y.text = str(round(models[selected_object].scale[1]*1000)/1000)
            input_scl_z.text = str(round(models[selected_object].scale[2]*1000)/1000)
        
        
        fade_out_timer -= 1
        if fade_out_timer == 0:
            fade_out_timer = fade_out_timer_set
            debugstream.text = ""
        
        axis_pointers[axis].alpha = 0.2
        axis_pointers[axis].scale = 1
        if urs.held_keys["x"]: axis = "x"
        if urs.held_keys["y"]: axis = "y"
        if urs.held_keys["z"]: axis = "z"
        axis_pointers[axis].alpha = 1
        axis_pointers[axis].scale = 1.2
        
        axistext.text = axis
        
        if grab_mode and selected_object != None:
            if   axis == "x": models[selected_object].position = (models[selected_object].position[0]-(sign(urs.camera.world_z-orbit.world_z) * urs.mouse.velocity[0] * urs.distance(urs.camera.world_position, orbit.world_position)*2), models[selected_object].position[1], models[selected_object].position[2]) 
            elif axis == "y": models[selected_object].position = (models[selected_object].position[0], models[selected_object].position[1], models[selected_object].position[2]+(sign(urs.camera.world_x-orbit.world_x) * urs.mouse.velocity[0] * urs.distance(urs.camera.world_position, orbit.world_position)*2))
            elif axis == "z": models[selected_object].position = (models[selected_object].position[0], models[selected_object].position[1]+(urs.mouse.velocity[1] * urs.distance(urs.camera.world_position, orbit.world_position)*3), models[selected_object].position[2])
        
        if scale_mode and selected_object != None:
            models[selected_object].scale += (models[selected_object].scale[0] * urs.mouse.velocity[0]*10, models[selected_object].scale[1] * urs.mouse.velocity[0]*10, models[selected_object].scale[2] * urs.mouse.velocity[0]*10)
                
        if urs.mouse.middle and not urs.held_keys["shift"]:
            urs.camera.orthographic = False
            orbit.rotation_y += urs.mouse.velocity[0] * urs.time.dt * 30000
            orbit.rotation_x -= -urs.mouse.velocity[1] * urs.time.dt * 25000
            
            if orbit.rotation_x > 90:
                orbit.rotation_x = 90
            
            if orbit.rotation_x < -90:
                orbit.rotation_x = -90
            
            
        if urs.mouse.middle and urs.held_keys["shift"]:
            urs.camera.orthographic = False
            orbit.position += (orbit.left[0] * -urs.mouse.velocity[0] * urs.time.dt * 1500, -urs.mouse.velocity[1] * urs.time.dt * 3000, -urs.mouse.velocity[0] * urs.time.dt * 1500 * orbit.left[2])

        if selected_object != None:
            axis_origin.position = models[selected_object].position
        

class model_(urs.Entity):
    def __init__(self, model, position, rotation, scale, mass, friction, index, name):
        super().__init__(
            parent = urs.scene,
            model = model,
            collider = "mesh",
            color = urs.color.white,
            position = [position[0], position[1], position[2]],
            rotation = rotation,
            name = name,
            mass = mass,
            friction = friction,
            scale = scale,
            double_sided = True,
            selected = False,
            index = index,
            highlight_color = urs.color.lime
            )
    
    def select(self):
        global selected_object, models
        if selected_object != None:    
            models[selected_object].deselect()
        selected_object = self.index
        self.selected = True
        self.color = self.highlight_color
        nametext.text = self.name
        
        input_pos_x.text = str(round(models[selected_object].position[0]*1000)/1000)
        input_pos_y.text = str(round(models[selected_object].position[1]*1000)/1000)
        input_pos_z.text = str(round(models[selected_object].position[2]*1000)/1000)
        
        input_rot_x.text = str(round(models[selected_object].rotation[0]*1000)/1000)
        input_rot_y.text = str(round(models[selected_object].rotation[1]*1000)/1000)
        input_rot_z.text = str(round(models[selected_object].rotation[2]*1000)/1000)
        
        input_scl_x.text = str(round(models[selected_object].scale[0]*1000)/1000)
        input_scl_y.text = str(round(models[selected_object].scale[1]*1000)/1000)
        input_scl_z.text = str(round(models[selected_object].scale[2]*1000)/1000)
        
        mass_slider.value = models[selected_object].mass
        friction_slider.value = models[selected_object].friction
        
    def deselect(self):
        self.selected = False
        self.color = urs.color.white 
          
    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                self.select()
    
models = []
selected_object = None

def sign(num):
    if num == 0: return 1
    return num/abs(num)

def init():
    global app, orbit, debugstream, fade_out_timer_set, fade_out_timer, axis, axistext, axis_pointers, axis_origin, nametext, grab_mode, scale_mode, input_pos_x, input_pos_y, input_pos_z, input_rot_x, input_rot_y, input_rot_z, input_scl_x, input_scl_y, input_scl_z
    global mass_slider, friction_slider
    app = urs.Ursina()
    urs.window.title = 'Model Preview'
    urs.window.forced_aspect_ratio = 1.5
    urs.window.windowed_size = urs.window.fullscreen_size / 1.7
    urs.window.borderless = False
    urs.window.fullscreen = False
    urs.window.exit_button.visible = False
    urs.window.fps_counter.enabled = False
    
    x = 10
    fade_out_timer_set = 500
    fade_out_timer = 1
    grab_mode = False
    scale_mode = False
    
    
    urs.camera.rotation_y = 180
    urs.camera.rotation_x = 0
    urs.camera.position = (0, 0, x)
    urs.camera.fov = 120
    urs.camera.clip_plane_far = 200
    
    orbit = orbit_object(model="cube", visible=False)
    urs.camera.parent = orbit
    orbit.rotation_x -= 30
    orbit.rotation_y -= 45
    
    input_pos_x = urs.InputField(position=(0.19, 0.425, 0), model='quad', scale_x=0.2); #input_pos_x.scale=0.04
    input_pos_y = urs.InputField(position=(0.4, 0.425, 0), model='quad', scale_x=0.2); #input_pos_y.scale=0.04
    input_pos_z = urs.InputField(position=(0.61, 0.425, 0), model='quad', scale_x=0.2); #input_pos_z.scale=0.04
    
    input_rot_x = urs.InputField(position=(0.19, 0.37, 0), model='quad', scale_x=0.2); #input_rot_x.scale=0.04
    input_rot_y = urs.InputField(position=(0.4, 0.37, 0), model='quad', scale_x=0.2); #input_rot_y.scale=0.04
    input_rot_z = urs.InputField(position=(0.61, 0.37, 0), model='quad', scale_x=0.2); #input_rot_z.scale=0.04
    
    input_scl_x = urs.InputField(position=(0.19, 0.315, 0), model='quad', scale_x=0.2); #input_scl_x.scale=0.04
    input_scl_y = urs.InputField(position=(0.4, 0.315, 0), model='quad', scale_x=0.2); #input_scl_y.scale=0.04
    input_scl_z = urs.InputField(position=(0.61, 0.315, 0), model='quad', scale_x=0.2); #input_scl_z.scale=0.04
    
    position_text = urs.Text(text="Position", position=(0.08, 0.425, 0), origin=(0.5, 0))
    rotation_text = urs.Text(text="Rotation", position=(0.08, 0.37, 0), origin=(0.5, 0))
    scale_text = urs.Text(text="Scale", position=(0.08, 0.315, 0), origin=(0.5, 0))
    
    x_text = urs.Text(text="X", position=(0.19, 0.46, 0), origin=(0, 0))
    y_text = urs.Text(text="Y", position=(0.4, 0.46, 0), origin=(0, 0))
    z_text = urs.Text(text="Z", position=(0.61, 0.46, 0), origin=(0, 0))
    
    mass_slider = urs.ThinSlider(0, 256, text="Mass", position=(0.1, 0.24, 0))
    friction_slider = urs.ThinSlider(0, 256, text="Friction", position=(0.1, 0.18, 0))
    
    
    
    axis = "x"
    axistext = urs.Text(text=axis, x=-0.7, y=0)
    axis_origin = urs.Entity(model="cube", alpha=0)
    axis_pointers = {"x": urs.Entity(model="arrow", color=urs.color.red, origin=(-0.8, 0, 0), rotation = (0, 0, 0), alpha=0.2, parent=axis_origin),
                     "y": urs.Entity(model="arrow", color=urs.color.green, origin=(-0.8, 0, 0), rotation = (0, 90, 0), alpha=0.2, parent=axis_origin),
                     "z": urs.Entity(model="arrow", color=urs.color.blue, origin=(-0.8, 0, 0), rotation = (0, 0, -90), alpha=0.2, parent=axis_origin)}
    
    nametext = urs.Text(text="", x=0, y=-0.47, origin=(0, 0))
    debugstream = urs.Text(text="", x=0, y=-0.4, origin=(0, 0))
    #grid = urs.Entity(model=urs.Grid(100, 100, mode='line', thickness=1), scale = (500, 500, 500), rotation = (90, 0, 0), color = urs.color.gray)
       
def view_model(verts, tris, position, rotation, scale, mass, friction, index, name):
    global models
    
    colors = [urs.color.color(0, 0, random.uniform(0.8, 1.0)) for i in verts]
    models.append(model_(model=urs.Mesh(vertices=verts, triangles=tris, mode='triangle', colors=colors), position = position, scale = scale, rotation = rotation, mass = mass, friction = friction, index = index, name = name))
    
def view_scene(archive):
    global models
    
    debugstream.text = "Loading Models..."
    start_time = time.perf_counter()
    
    for model in models:
        urs.destroy(model)
        del model
        
    models = []
    fail_counter = 0
    for index in range(0, len(archive.simple_objects)):
        time.sleep(0.03)
        orbit.rotation_y += 5
        try:
            verts = pyhotools.get_vertices(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[0][0]].child.layers[archive.simple_objects[index].model[0][1]].entries[archive.simple_objects[index].model[0][2]][1], archive.section_headers[archive.simple_objects[index].model[0][0]].child.layers[archive.simple_objects[index].model[0][1]].entries[archive.simple_objects[index].model[0][2]][2])
            faces = pyhotools.get_faces(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[-1][0]].child.layers[archive.simple_objects[index].model[-1][1]].entries[archive.simple_objects[index].model[-1][2]][1], archive.section_headers[archive.simple_objects[index].model[-1][0]].child.layers[archive.simple_objects[index].model[-1][1]].entries[archive.simple_objects[index].model[-1][2]][2], len(archive.simple_objects[index].model)-1, archive.simple_objects[index].bone_length)
            
            view_model(verts, faces, archive.simple_objects[index].position, archive.simple_objects[index].rotation, archive.simple_objects[index].scale, archive.simple_objects[index].mass, archive.simple_objects[index].friction, index, archive.simple_objects[index].name)
            debugstream.text = f"{archive.simple_objects[index].name} loaded"
            
        except:
            
            debugstream.text = f"{archive.simple_objects[index].name} failed to load"
            models.append(None)
            fail_counter += 1
            time.sleep(0.05)
    
    debugstream.text = f"Done!   ({round((time.perf_counter()-start_time)*1000)/1000}s)"
    print(f"{fail_counter} model(s) failed to load!")
    print(len(models), len(archive.simple_objects))
    