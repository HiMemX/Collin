import pyhotools
import ursina as urs
import threading
import random
import time
import math
import numpy
import frame
import cmpr
import wavefront
import tkinter as tk
import os
import shutil

class orbit_object(urs.Entity):
    def input(self, key):
        global grab_mode, scale_mode, locked_mode, lockedtext
        if key == 'scroll down':
            self.position += self.forward
            
        if key == 'scroll up':
            self.position += -self.forward
        
        if key == "l":
            if locked_mode:
                locked_mode = False
                lockedtext.text = ""
            else:
                locked_mode = True
                lockedtext.text = "Locked"
        
        if key == "f" and selected_object != None and models[selected_object] != None:
            self.position = models[selected_object].position
        
        if key == 'g':
            scale_mode = False
            grab_mode = 1-grab_mode
            
        if key == 's':
            grab_mode = False
            scale_mode = 1-scale_mode
            
        if key == "left mouse down":
            locked_mode = False
            grab_mode = False
            scale_mode = False
        
    def update(self):
        global fade_out_timer, fade_out_timer_set, axis, axistext, axis_pointers, grab_mode, scale_mode, models, models_to_load, load_flag
        global start_time, clipboard, locked_mode, helptext
        
        if urs.held_keys["tab"]:
            helptext.text = '''
Mouse3 to orbit
Shift+Mouse3 to move
G to Grab
S to Scale
X,Y,Z to select the axis
F to focus on object
L to toggle locked mode
CTRL+C to copy model
CTRL+V to paste model
'''
        else:
            helptext.text = "TAB for info"
        
        if urs.held_keys["c"] and urs.held_keys["control"] and selected_object != None and models[selected_object] != None:
            clipboard = models[selected_object].index
            
        if urs.held_keys["v"] and urs.held_keys["control"] and selected_object != None and models[selected_object] != None and clipboard != None:
            if models[selected_object].type_ == b"\x0B\x54\xBB\x17" and models[clipboard].anim_id != b"\x00\x00\x00\x00\x00\x00\x00\x00":
                debugstream.text = "You can't paste this on here!"
                fade_out_timer = fade_out_timer_set
                
            else:
                models[selected_object].model_id = models[clipboard].model_id
                models[selected_object].anim_id = models[clipboard].anim_id
                models[selected_object].model = urs.deepcopy(models[clipboard].model)
                
                for mesh in range(len(models[selected_object].meshes)):
                    print(len(models[selected_object].meshes))
                    urs.destroy(models[selected_object].meshes[mesh])
                
                models[selected_object].meshes = []
                    
                for mesh in range(len(models[clipboard].meshes)):
                    if models[clipboard].meshes[mesh].texture != None:
                        models[selected_object].meshes.append(urs.Entity(model=urs.Entity(vertices = models[clipboard].meshes[mesh].model.vertices, triangles = models[clipboard].meshes[mesh].model.triangles, uvs = models[clipboard].meshes[mesh].model.uvs), parent=models[selected_object], texture = models[clipboard].meshes[mesh].texture.path, double_sided = True))
                    else:
                        models[selected_object].meshes.append(urs.Entity(model=urs.Entity(vertices = models[clipboard].meshes[mesh].model.vertices, triangles = models[clipboard].meshes[mesh].model.triangles, uvs = models[clipboard].meshes[mesh].model.uvs), parent=models[selected_object], double_sided = True))
                    
                #models[selected_object].meshes = urs.deepcopy(models[clipboard].meshes)
                models[selected_object].collider = models[selected_object].model
                debugstream.text = "Pasted!"
                fade_out_timer = fade_out_timer_set
                
        for i in range(3):
            if load_flag:
                if len(models_to_load) == 0:
                    load_flag = False
                    fade_out_timer = fade_out_timer_set
                    debugstream.text = f"Loaded {len(models)} objects in {math.ceil((time.perf_counter()-start_time)*1000)/1000}s"
                    fade_out_timer = fade_out_timer_set
                    orbit.position = (0, 0, 0)
                    orbit.rotation = (-25, 45, 0)
                    break
                
                try:
                    fade_out_timer = fade_out_timer_set
                    view_model(*models_to_load[0])
                    debugstream.text = f"{models_to_load[0][-2]} loaded"
                    fade_out_timer = fade_out_timer_set
                    
                except:
                    models.append(None)
                
                models_to_load = models_to_load[1:]
            
        
        if selected_object != None and not grab_mode and not scale_mode and models[selected_object] != None:
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
        
        if selected_object != None and (grab_mode or scale_mode) and models[selected_object] != None:
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
        
        if grab_mode and selected_object != None and models[selected_object] != None:
            if   axis == "x": models[selected_object].position = (models[selected_object].position[0]-(sign(urs.camera.world_z-orbit.world_z) * urs.mouse.velocity[0] * urs.distance(urs.camera.world_position, models[selected_object].position)*2), models[selected_object].position[1], models[selected_object].position[2]) 
            elif axis == "y": models[selected_object].position = (models[selected_object].position[0], models[selected_object].position[1], models[selected_object].position[2]+(sign(urs.camera.world_x-orbit.world_x) * urs.mouse.velocity[0] * urs.distance(urs.camera.world_position, models[selected_object].position)*2))
            elif axis == "z": models[selected_object].position = (models[selected_object].position[0], models[selected_object].position[1]+(urs.mouse.velocity[1] * urs.distance(urs.camera.world_position, models[selected_object].position)*3), models[selected_object].position[2])
        
        if scale_mode and selected_object != None and models[selected_object] != None:
            models[selected_object].scale += (models[selected_object].scale[0] * urs.mouse.velocity[0]*10, models[selected_object].scale[1] * urs.mouse.velocity[0]*10, models[selected_object].scale[2] * urs.mouse.velocity[0]*10)
                
        if urs.mouse.middle and not urs.held_keys["shift"]:
            urs.camera.orthographic = False
            orbit.rotation_y += urs.mouse.velocity[0] * urs.time.dt * 20000
            orbit.rotation_x -= -urs.mouse.velocity[1] * urs.time.dt * 17000
            
            if orbit.rotation_x > 90:
                orbit.rotation_x = 90
            
            if orbit.rotation_x < -90:
                orbit.rotation_x = -90
            
            
        if urs.mouse.middle and urs.held_keys["shift"]:
            urs.camera.orthographic = False
            orbit.position += (orbit.left[0] * -urs.mouse.velocity[0] * urs.time.dt * 1500, -urs.mouse.velocity[1] * urs.time.dt * 3000, -urs.mouse.velocity[0] * urs.time.dt * 1500 * orbit.left[2])

        if selected_object != None and models[selected_object] != None:
            axis_origin.position = models[selected_object].position
        
        if locked_mode and selected_object != None and models[selected_object] != None:
            orbit.position = models[selected_object].position

class submesh(urs.Entity):
    def __init__(self, complete_mesh, model, parent, texture, texture_id, has_alpha):  #submesh(model=mesh, parent=curr_model, texture = "textures\\"+str(index).zfill(4)+str(mdl).zfill(4)+".png")
        super().__init__(
            texture_id = texture_id,
            complete_mesh = complete_mesh,
            model = model,
            parent = parent,
            texture = texture,
            double_sided = False,
            has_alpha = has_alpha
            )
        

class modelclass(urs.Entity):
    def __init__(self, model, texture_, position, rotation, scale, mass, friction, index, anim_id, type_, name, model_id, collider):
        super().__init__(
            parent = urs.scene,
            anim_id = anim_id,
            type_ = type_,
            model_id = model_id,
            model = model,
            texture_ = texture_,
            meshes = [],
            #texture = os.path.abspath(os.getcwd())+"\\textures\\"+str(index).zfill(4)+str(test).zfill(4)+".png",
            collider = collider,
            visible_self = False,
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
            highlight_color = urs.color.color(100, 0.5, 1)
            )
    
    def select(self):
        global selected_object, models
        if selected_object != None and models[selected_object] != None:    
            models[selected_object].deselect()
            
        selected_object = self.index
        self.selected = True
        
        for mesh in self.meshes:
            mesh.color = self.highlight_color
        
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
        for mesh in self.meshes:
            mesh.color = urs.color.white
         
          
    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                self.select()
        
models = []
clipboard = None
load_flag = False
models_to_load = []
selected_object = None

def update_visibility():
    global models, geo_visible
    for model in models:
        if model == None:
            continue
        
        if model.type_ == b"\x00\x11\x73\x1B":
            if geo_visible.value == "off":
                model.visible = False
            else:
                model.visible = True
            
def nlist_len(ls):
    length = 0
    for i in ls:
        length += len(i)
    return length  
    
def export_object():
    if selected_object == None or models[selected_object] == None:
        return
    
    try: directory = str(tk.filedialog.askdirectory())
    except: return
    
    directory += f"/{models[selected_object].name}"
    
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)
        
    os.mkdir(directory)
        
    
    
    wavefront.obj_export(directory, [models[selected_object]], False)
    
    for i, texture in enumerate(models[selected_object].texture_):
        if texture != [None]:
            #cmpr.rgb_to_png(texture, directory, .meshes[i].texture_id)
            cmpr.rgba_to_pngs(texture, directory, models[selected_object].meshes[i].texture_id)
        
    
    debugstream.text = f"Exported {models[selected_object].name} to {directory}"
    fade_out_timer = fade_out_timer_set
    
def import_object():
    if selected_object == None or models[selected_object] == None:
        return
    
    path = str(tk.filedialog.askopenfilename())
    
    verts, tris = wavefront.obj_import(path)
    colors = [urs.color.color(random.uniform(0, 255), random.uniform(0.05, 0.1), random.uniform(0.9, 1.0)) for i in verts]
    
    models[selected_object].model = urs.Mesh(vertices=verts, triangles=tris, mode='triangle', colors=colors)

def sign(num):
    if num == 0: return 1
    return num/abs(num)

def init():
    global app, orbit, debugstream, fade_out_timer_set, fade_out_timer, axis, axistext, axis_pointers, axis_origin, nametext, grab_mode, scale_mode, input_pos_x, input_pos_y, input_pos_z, input_rot_x, input_rot_y, input_rot_z, input_scl_x, input_scl_y, input_scl_z
    global mass_slider, friction_slider, collision_group, lockedtext, locked_mode, mode_buffer, geo_visible
    global helptext
    app = urs.Ursina(vsync = True)
    urs.window.title = 'Editor'
    urs.window.icon = "couch.ico"
    urs.window.forced_aspect_ratio = 1.5
    urs.window.windowed_size = urs.window.fullscreen_size / 1.7
    urs.window.borderless = False
    urs.window.fullscreen = False
    urs.window.exit_button.visible = False
    urs.window.fps_counter.enabled = False
    urs.window.color = urs.color.color(0, 0, 0.15)
    
    urs.scene.fog_density = 1         # sets exponential density
    urs.scene.fog_density = (120, 150)
    urs.scene.fog_color = urs.color.color(0, 0, 0.15)
    
    x = 4
    fade_out_timer_set = 350
    fade_out_timer = 1
    grab_mode = False
    scale_mode = False
    locked_mode = False
    
    urs.Texture.default_filtering = "bilinear"
    #sky = urs.Sky(color=urs.color.color(0, 0, 0.2))
    
    urs.camera.rotation_y = 180
    urs.camera.rotation_x = 0
    urs.camera.position = (0, 0, x)
    urs.camera.fov = 120
    urs.camera.clip_plane_far = 150
    
    orbit = orbit_object(model="sphere", visible=False)
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
    
    position_text = urs.Text(text="Position", position=(0.08, 0.425, 0), origin=(0.5, 0), font=r"Krabby Patty.ttf")
    rotation_text = urs.Text(text="Rotation", position=(0.08, 0.37, 0), origin=(0.5, 0), font=r"Krabby Patty.ttf")
    scale_text = urs.Text(text="Scale", position=(0.08, 0.315, 0), origin=(0.5, 0), font=r"Krabby Patty.ttf")
    
    x_text = urs.Text(text="X", position=(0.19, 0.46, 0), origin=(0, 0), font=r"Krabby Patty.ttf")
    y_text = urs.Text(text="Y", position=(0.4, 0.46, 0), origin=(0, 0), font=r"Krabby Patty.ttf")
    z_text = urs.Text(text="Z", position=(0.61, 0.46, 0), origin=(0, 0), font=r"Krabby Patty.ttf")
    
    mass_slider = urs.ThinSlider(0, 256, text="Mass", position=(0.1, 0.24, 0))
    mass_slider.label.font = r"Krabby Patty.ttf"
    
    friction_slider = urs.ThinSlider(0, 256, text="Friction", position=(0.1, 0.18, 0))
    friction_slider.label.font = r"Krabby Patty.ttf"
    
    export_button = urs.Button(text="Export", model="quad", position=(0.61, 0.1, 0), scale=(0.2, 0.05))
    export_button.on_click = export_object
    export_button.text_entity.font = r"Krabby Patty.ttf"
    
    geo_visible_text = urs.Text(text="Level Geometry: ", position=(0.61, 0, 0), origin=(0.5, 1), font=r"Krabby Patty.ttf")
    geo_visible = urs.ButtonGroup(('off', 'on'), min_selection=1, position=(0.61, 0, 0), default='on', selected_color=urs.color.red)
    geo_visible.on_value_changed = update_visibility
    
    #import_button = urs.Button(text="Import", model="quad", position=(0.61, 0.02, 0), scale=(0.2, 0.05))
    #import_button.on_click = import_object
    #import_button.text_entity.font = r"Krabby Patty.ttf"
    
    axis = "x"
    axis_origin = urs.Entity(model="cube", alpha=0)
    axis_pointers = {"x": urs.Entity(model="arrow", color=urs.color.red, origin=(-0.8, 0, 0), rotation = (0, 0, 0), alpha=0.2, parent=axis_origin),
                     "y": urs.Entity(model="arrow", color=urs.color.green, origin=(-0.8, 0, 0), rotation = (0, 90, 0), alpha=0.2, parent=axis_origin),
                     "z": urs.Entity(model="arrow", color=urs.color.blue, origin=(-0.8, 0, 0), rotation = (0, 0, -90), alpha=0.2, parent=axis_origin)}
    
    nametext = urs.Text(text="", x=0, y=-0.4, origin=(0, 0), color=urs.color.color(200, 0.5, 1), font=r"Krabby Patty.ttf")
    debugstream = urs.Text(text="", x=0, y=-0.47, origin=(0, 0), color=urs.color.color(0, 0.5, 1), font=r"Krabby Patty.ttf")
    lockedtext = urs.Text(text="", position=(-0.7, 0.46, 0), font=r"Krabby Patty.ttf")
    helptext = urs.Text(text="TAB for info", position=(-0.7, -0.46, 0), origin=(-0.5, -0.5), font=r"Krabby Patty.ttf")
    #grid = urs.Entity(model=urs.Grid(100, 100, mode='line', thickness=1), scale = (500, 500, 500), rotation = (90, 0, 0), color = urs.color.gray)
       
def view_model(verts_in, tris, texture, texture_ids, uvs_in, position, rotation, scale, mass, friction, index, size_divisor, anim_id, type_, name, model_id):
    global models
    orbit.position = position
    orbit.rotation = (rotation[0]-25, rotation[1]+45, rotation[2])
    
    #curr_model = modelclass(model=None, texture_ = texture, position = position, scale = scale, rotation = rotation, mass = mass, friction = friction, index = index, anim_id = anim_id, type_ = type_, name = name, model_id = model_id)
    # ----
    fin_faces = []
    
    for mdl in range(len(verts_in)):
        for face in tris[mdl]:
            fin_faces.append(((face[0][0]+nlist_len(verts_in[:mdl]), face[0][1]+nlist_len(uvs_in[:mdl])), (face[1][0]+nlist_len(verts_in[:mdl]), face[1][1]+nlist_len(uvs_in[:mdl])), (face[2][0]+nlist_len(verts_in[:mdl]), face[2][1]+nlist_len(uvs_in[:mdl]))))
    
    
    temp_verts = [item for sublist in verts_in for item in sublist]
    temp_uvs = [item for sublist in uvs_in for item in sublist]
    tris_ = fin_faces
    tris__ = [tuple(index[0] for index in face) for face in tris_]
    verts = []
    uvs = []
    #print(name)
    #print([len(vert) for vert in verts_in])
    #print(tris)
    #for face in tris_:
    #    verts.append(temp_verts[face[0][0]])
    #    verts.append(temp_verts[face[1][0]])
    #    verts.append(temp_verts[face[2][0]])
    #print(tris__, [(i, i+1, i+2) for i in range(0, int(len(verts)), 3)])   
    #collider = ["mesh", "sphere"][len(verts) > 1500]
    #mesh = urs.Mesh(vertices=verts, triangles=[(i, i+1, i+2) for i in range(0, int(len(verts)), 3)], mode='triangle')
    mesh = urs.Mesh(vertices=temp_verts, triangles=tris__, mode='triangle')
    #collider = [mesh, "sphere"][len(temp_verts) > 2000]
    collider = "mesh"
    curr_model = modelclass(model = mesh, texture_ = texture, position = position, scale = scale, rotation = rotation, mass = mass, friction = friction, index = index, anim_id = anim_id, type_ = type_, name = name, model_id = model_id, collider=collider)
    # -----
    
    
    for mdl in range(len(verts_in)):
        sizex = 2**size_divisor[mdl][0]
        sizey = 2**size_divisor[mdl][0]
        
        temp_verts = verts_in[mdl]
        temp_uvs = [[i[0]/sizex, i[1]/sizey] for i in uvs_in[mdl]]
        uvs = []
        verts = []
        fin_faces = []
    
        for face in tris[mdl]:
            fin_faces.append(((face[0][0]+nlist_len(verts_in[:mdl]), face[0][1]+nlist_len(uvs_in[:mdl])), (face[1][0]+nlist_len(verts_in[:mdl]), face[1][1]+nlist_len(uvs_in[:mdl])), (face[2][0]+nlist_len(verts_in[:mdl]), face[2][1]+nlist_len(uvs_in[:mdl]))))
        
        for face in tris[mdl]:
            #try:
            verts.append(temp_verts[face[0][0]])
            verts.append(temp_verts[face[1][0]])
            verts.append(temp_verts[face[2][0]])
                    
            uvs.append((temp_uvs[face[0][1]]))
            uvs.append((temp_uvs[face[1][1]]))
            uvs.append((temp_uvs[face[2][1]]))
            #except:
            #    print(face)
            #   exit()
            
        mesh = urs.Mesh(vertices=verts, triangles=[(i, i+1, i+2) for i in range(0, int(len(verts)), 3)], uvs=uvs, mode='triangle')
        #curr_model = modelclass(model=mesh, texture_ = texture[mdl], position = position, scale = scale, rotation = rotation, mass = mass, friction = friction, index = index, anim_id = anim_id, type_ = type_, name = name, model_id = model_id, test = mdl)
        
        if os.path.exists("textures\\"+texture_ids[mdl]+".png"):
            curr_model.meshes.append(submesh(complete_mesh = (temp_verts, temp_uvs, fin_faces), model=mesh, parent=curr_model, texture = "textures\\"+texture_ids[mdl]+".png", texture_id = texture_ids[mdl], has_alpha = len(texture[mdl])==2))
        else:
            curr_model.meshes.append(submesh(complete_mesh = (temp_verts, temp_uvs, fin_faces), model=mesh, parent=curr_model, texture = None, texture_id = texture_ids[mdl], has_alpha=False))
        #models.append(curr_model)
    
    models.append(curr_model)
    
    #verts = [item for sublist in verts for item in sublist]
    #tris = [item for sublist in tris for item in sublist]
    
    '''
    fin_faces = []
    
    for mdl in range(len(verts)):
        for face in tris[mdl]:
            fin_faces.append(((face[0][0]+nlist_len(verts[:mdl]), face[0][1]+nlist_len(uvs[:mdl])), (face[1][0]+nlist_len(verts[:mdl]), face[1][1]+nlist_len(uvs[:mdl])), (face[2][0]+nlist_len(verts[:mdl]), face[2][1]+nlist_len(uvs[:mdl]))))
    
    temp_verts = [item for sublist in verts for item in sublist]
    temp_uvs = [item for sublist in uvs for item in sublist]
    tris = fin_faces
    verts = []
    uvs = []
    
    sizex = 2**size_divisor[0]
    sizey = 2**size_divisor[0]
    
    for face in tris:
        #print(face, temp_uvs)
        verts.append(temp_verts[face[0][0]])
        verts.append(temp_verts[face[1][0]])
        verts.append(temp_verts[face[2][0]])
        
        uvs.append((temp_uvs[face[0][1]][0]/sizex, temp_uvs[face[0][1]][1]/sizey))
        uvs.append((temp_uvs[face[1][1]][0]/sizex, temp_uvs[face[1][1]][1]/sizey))
        uvs.append((temp_uvs[face[2][1]][0]/sizex, temp_uvs[face[2][1]][1]/sizey))

    mesh = urs.Mesh(vertices=verts, triangles=[(i, i+1, i+2) for i in range(0, int(len(verts)), 3)], uvs=uvs, mode='triangle')
    curr_model = modelclass(model=mesh, texture_ = texture[0], position = position, scale = scale, rotation = rotation, mass = mass, friction = friction, index = index, anim_id = anim_id, type_ = type_, name = name, model_id = model_id)
    
    models.append(curr_model)
    '''
def view_scene(archive):
    global models, models_to_load, load_flag, start_time
    
    debugstream.text = "Loading Models..."
    fade_out_timer = fade_out_timer_set
    start_time = time.perf_counter()
    
    for model in models:
        urs.destroy(model)
        del model
        
    models = []
    known_textures = []
    known_models = []
    
    dir = os.getcwd()+"\\textures"
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
        
    exported_ids = []
    for index in range(0, len(archive.simple_objects)):
        verts = []
        faces = []
        texture = []
        raw_uvs = []
        for x in range(len(archive.simple_objects[index].model)):
            break_flag = False
            for text in known_models:
                if text[0] == archive.simple_objects[index].model[x][0]:
                    verts.append(text[1])
                    faces.append(text[2])
                    raw_uvs.append(text[3])
                    break_flag = True
            
            if not break_flag:
                #verts.append(pyhotools.get_vertices(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][1], archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][2]))
                if archive.simple_objects[index].pfst:
                    new_verts = pyhotools.get_vertices_pfst(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][1], archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][2])
                
                else:
                    new_verts = pyhotools.get_vertices(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][1], archive.section_headers[archive.simple_objects[index].model[x][0][0]].child.layers[archive.simple_objects[index].model[x][0][1]].entries[archive.simple_objects[index].model[x][0][2]][2])
                
                if (len(archive.simple_objects[index].model) - len(archive.simple_objects[index].transformation)) <= x:
                    #print(x, len(archive.simple_objects[index].transformation), len(archive.simple_objects[index].model))
                    # Transform verts
                    #print(archive.simple_objects[index].transformation[x - (len(archive.simple_objects[index].model) - len(archive.simple_objects[index].transformation))])
                    matrix = archive.simple_objects[index].transformation[x - (len(archive.simple_objects[index].model) - len(archive.simple_objects[index].transformation))][0]
                    position = archive.simple_objects[index].transformation[x - (len(archive.simple_objects[index].model) - len(archive.simple_objects[index].transformation))][1]
                    transformed_verts = []
                    
                    #print(archive.simple_objects[index].transformation[x - (len(archive.simple_objects[index].model) - len(archive.simple_objects[index].transformation))])
                    
                    for vert in new_verts:
                        #print(matrix.dot(numpy.array(vert)).tolist())
                        new_vert = matrix.dot(numpy.array(vert)).tolist()[0]
                        new_vert = numpy.array((-new_vert[0]-position[0], new_vert[1]+position[1], new_vert[2]+position[2]))
                        
                        for transform in archive.simple_objects[index].global_transforms:
                            new_vert = transform[0].dot(new_vert).tolist()[0]
                           
                        #for transform in archive.simple_objects[index].global_transforms:
                            new_vert = (new_vert[0]-transform[1][0], new_vert[1]+transform[1][1], new_vert[2]+transform[1][2])
                            #print(new_vert.tolist())
                            
                        #new_vert = new_vert.tolist()[0]
                        
                        #new_vert = (-vert[0]-position[0], vert[1]+position[1], vert[2]+position[2])
                        
                        transformed_verts.append(new_vert)
                    
                    new_verts = transformed_verts
                
                    verts.append(new_verts)
                    
                    faces.append(pyhotools.get_faces(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][-1][0]].child.layers[archive.simple_objects[index].model[x][-1][1]].entries[archive.simple_objects[index].model[x][-1][2]][1], archive.section_headers[archive.simple_objects[index].model[x][-1][0]].child.layers[archive.simple_objects[index].model[x][-1][1]].entries[archive.simple_objects[index].model[x][-1][2]][2], len(archive.simple_objects[index].model[x])-1, archive.simple_objects[index].bone_length[x], archive.simple_objects[index].pfst))
                    raw_uvs.append(pyhotools.get_uvs(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][-2][0]].child.layers[archive.simple_objects[index].model[x][-2][1]].entries[archive.simple_objects[index].model[x][-2][2]][1], archive.section_headers[archive.simple_objects[index].model[x][-2][0]].child.layers[archive.simple_objects[index].model[x][-2][1]].entries[archive.simple_objects[index].model[x][-2][2]][2]))
                    #known_models.append([archive.simple_objects[index].model[x][0], verts[-1], faces[-1], raw_uvs[-1]])
            
                else:
                    verts.append(new_verts)
                    
                    faces.append(pyhotools.get_faces(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][-1][0]].child.layers[archive.simple_objects[index].model[x][-1][1]].entries[archive.simple_objects[index].model[x][-1][2]][1], archive.section_headers[archive.simple_objects[index].model[x][-1][0]].child.layers[archive.simple_objects[index].model[x][-1][1]].entries[archive.simple_objects[index].model[x][-1][2]][2], len(archive.simple_objects[index].model[x])-1, archive.simple_objects[index].bone_length[x], archive.simple_objects[index].pfst))
                    
                    raw_uvs.append(pyhotools.get_uvs(open(archive.path, "rb"), archive.section_headers[archive.simple_objects[index].model[x][-2][0]].child.layers[archive.simple_objects[index].model[x][-2][1]].entries[archive.simple_objects[index].model[x][-2][2]][1], archive.section_headers[archive.simple_objects[index].model[x][-2][0]].child.layers[archive.simple_objects[index].model[x][-2][1]].entries[archive.simple_objects[index].model[x][-2][2]][2]))
                    known_models.append([archive.simple_objects[index].model[x][0], verts[-1], faces[-1], raw_uvs[-1]])
                
            break_flag = False
            for text in known_textures:
                if text[0] == archive.simple_objects[index].texture[x]:
                    texture.append(text[1])
                    break_flag = True
            
            if not break_flag:
                if archive.simple_objects[index].texture[x] != None:
                    if (archive.simple_objects[index].texture_ids[x] in exported_ids):
                        continue
               
                    exported_ids.append(archive.simple_objects[index].texture_ids[x])
                    offset = archive.section_headers[archive.simple_objects[index].texture[x][0]].child.layers[archive.simple_objects[index].texture[x][1]].entries[archive.simple_objects[index].texture[x][2]][1]
                    texture.append(cmpr.tpl_decompress(open(archive.path, "rb"), offset+0x20))
                else:
                    texture.append([None])
                
                known_textures.append([archive.simple_objects[index].texture[x], texture[-1]])
            
        for x in range(len(texture)):
            if texture[x] != [None]:
                if archive.simple_objects[index].visibilities[x] == 1:
                    cmpr.rgb_to_png(texture[x], os.path.abspath(os.getcwd())+"\\textures", archive.simple_objects[index].texture_ids[x])#str(index).zfill(4)+str(x).zfill(4))
                else:
                    cmpr.rgb_to_png([texture[x][0]], os.path.abspath(os.getcwd())+"\\textures", archive.simple_objects[index].texture_ids[x])#str(index).zfill(4)+str(x).zfill(4))
        
        #fin_texture = 
        #for text in texture: 
        models_to_load.append([verts, faces, texture, archive.simple_objects[index].texture_ids, raw_uvs, archive.simple_objects[index].position, archive.simple_objects[index].rotation, archive.simple_objects[index].scale, archive.simple_objects[index].mass, archive.simple_objects[index].friction, index, archive.simple_objects[index].size_divisor, archive.simple_objects[index].anim_id, archive.simple_objects[index].type, archive.simple_objects[index].name, archive.simple_objects[index].model_id])
    
    load_flag = True