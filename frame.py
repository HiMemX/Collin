import modelviewer
import pyhotools
from threading import Thread
from multiprocessing import Process
import tkinter as tk
from tkinter import filedialog
import random
import cmpr
import os
import wavefront
import shutil
import typekey

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry("500x500")
        self.parent.iconbitmap("couch.ico")
        self.parent.title("Collin")
        
        self.listboxframe = tk.LabelFrame(self.parent, padx=10, pady=10, text="Objects")
        self.listboxframe.place(x=0, y=0)
        
        #self.settingsframe = tk.LabelFrame(self.parent, padx=10, pady=10, text="Settings")
        #self.settingsframe.place(x=500, y=0)
        
        self.objectlist = tk.Listbox(self.listboxframe, height=27, width=65)
        self.objectlist.pack()
        self.objectlist.bind("<<ListboxSelect>>", self.update_selection)
        
        #self.fovslider_text = tk.Label(self.settingsframe, text="FOV")
        #self.fovslider_text.pack()
        
        #self.fovslider = tk.ttk.Scale(self.settingsframe, from_=50, to=150, command=self.fovslider_changed, length=170)
        #self.fovslider.set(120)
        #self.fovslider.pack()
        
        self.current_directory = r""
        
        self.menu = tk.Menu(self.parent)
        self.parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff="off")
        self.menu.add_cascade(label="File", menu=self.file_menu)
        
        self.extra_menu = tk.Menu(self.menu, tearoff="off")
        self.menu.add_cascade(label="Extra", menu=self.extra_menu)
        
        self.file_menu.add_command(label="Open...", command=self.ask_directory)
        self.file_menu.add_command(label="Save...", command=self.save_models)
        self.file_menu.add_command(label="Quit", command=self.quit)
        
        self.extra_menu.add_command(label="Physicate", command=self.physicate)
        self.extra_menu.add_command(label="Swap transforms", command=self.swap_transforms)
        self.extra_menu.add_command(label="Export all", command=self.export_all)   
    
    def fovslider_changed(self, event):
        modelviewer.urs.camera.fov = self.fovslider.get()
    
    def export_all(self):
        if self.current_directory == r"":
            return
        
        try: directory = str(tk.filedialog.askdirectory())
        except: return
        
        directory += f"/Level Export"
        
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)
            
        os.mkdir(directory)
        
        wavefront.obj_export(directory, [i for i in modelviewer.models if i != None], True)
        
        exported_ids = []
        
        for model in modelviewer.models:
            if model == None: continue
            for i, texture in enumerate(model.texture_):
                if (model.meshes[i].texture_id in exported_ids):
                    continue
                exported_ids.append(model.meshes[i].texture_id)
                
                if texture != [None]:
                    cmpr.rgba_to_pngs(texture, directory, model.meshes[i].texture_id)
                    #if len(texture) == 2:
                    #    cmpr.rgb_to_png(texture, directory, model.meshes[i].texture_id + "_t")
        
        modelviewer.debugstream.text = f"Exported scene to {directory}"
        modelviewer.fade_out_timer = modelviewer.fade_out_timer_set
    
    def swap_transforms(self):
        if self.current_directory == r"":
            return
        
        indices = []
        for ii, i in enumerate(self.ho_archive.simple_objects):
            if i.type == b"\xAF\x4D\x62\x21" and modelviewer.models[ii] != None:
                indices.append(ii)
                
        for i in indices:
            if modelviewer.models[i] == None:
                continue
            
            random_object = indices[random.randint(0, len(indices)-1)]
            
            self.ho_archive.simple_objects[i].position, self.ho_archive.simple_objects[random_object].position = self.ho_archive.simple_objects[random_object].position, self.ho_archive.simple_objects[i].position
            self.ho_archive.simple_objects[i].rotation, self.ho_archive.simple_objects[random_object].rotation = self.ho_archive.simple_objects[random_object].rotation, self.ho_archive.simple_objects[i].rotation
            
            modelviewer.models[i].position = self.ho_archive.simple_objects[i].position
            modelviewer.models[i].rotation = self.ho_archive.simple_objects[i].rotation
            
            modelviewer.models[random_object].position = self.ho_archive.simple_objects[random_object].position
            modelviewer.models[random_object].rotation = self.ho_archive.simple_objects[random_object].rotation
        
        modelviewer.debugstream.text = f"Swapped {len(self.ho_archive.simple_objects)} objects transforms"
        modelviewer.fade_out_timer = modelviewer.fade_out_timer_set
        
    def physicate(self):
        if self.current_directory == r"":
            return
        
        for ii, i in enumerate(self.ho_archive.simple_objects):
            if modelviewer.models[ii] == None or i.type != b"\xAF\x4D\x62\x21":
                continue
            
            i.mass = 20
            i.friction = 10
            
            modelviewer.models[ii].mass = 20
            modelviewer.models[ii].friction = 10
        
        modelviewer.debugstream.text = f"Physicated {len(self.ho_archive.simple_objects)} objects"
        modelviewer.fade_out_timer = modelviewer.fade_out_timer_set
        
    def save_models(self):
        if self.current_directory == r"":
            return
        
        for ii, i in enumerate(self.ho_archive.simple_objects):
            if modelviewer.models[ii] == None:
                continue
            
            i.model_id = modelviewer.models[ii].model_id
            i.position = modelviewer.models[ii].position
            i.rotation = modelviewer.models[ii].rotation
            i.scale    = modelviewer.models[ii].scale
            i.mass     = modelviewer.models[ii].mass
            i.friction = modelviewer.models[ii].friction
            i.anim_id  = modelviewer.models[ii].anim_id
            i.model_class = modelviewer.models[ii]
            
        try:
            self.ho_archive.save_archive()
            modelviewer.debugstream.text = "Saved"
            modelviewer.fade_out_timer = modelviewer.fade_out_timer_set
            
        except PermissionError:
            modelviewer.debugstream.text = "Aint got no permission to write there lad"
            modelviewer.fade_out_timer = modelviewer.fade_out_timer_set
            
        
    
    def quit(self):
        self.parent.destroy()
    
    def update_selection(self, event):
        if self.current_directory == r"":
            return
        
        if modelviewer.selected_object != None:
            if modelviewer.models[modelviewer.selected_object] != None:
                
                modelviewer.models[modelviewer.selected_object].deselect()
            
        selection = event.widget.curselection()
        modelviewer.selected_object = selection[0]
        if modelviewer.models[selection[0]] == None:
            return
        
        modelviewer.models[modelviewer.selected_object].select()
    
    def ask_directory(self):
        global current_directory, archive
        temp_directory = (str(tk.filedialog.askopenfilename(filetypes=[("hkO Archives", "*.ho")])))
        if temp_directory == "":
            return
        self.current_directory = temp_directory
        
        self.ho_archive = pyhotools.ho_archive(self.current_directory, 0)    # 0 = TOS; UP, 1 = WALLE
        archive = self.ho_archive
        
        if len(self.ho_archive.simple_objects) == 0:
            return
        
        modelviewer.selected_object = None
        modelviewer.view_scene(self.ho_archive)
        modelviewer.update_visibility()
        self.update_listbox()

        self.parent.title(f"Collin - {self.current_directory}")
        
    def update_listbox(self):
        self.objectlist.delete(0, tk.END)
        for si, simp in enumerate(self.ho_archive.simple_objects):
            self.objectlist.insert(tk.END, f"[{typekey.types[simp.type]}] {simp.name}")

# To do list
# -----------
# -Create an editor || Bruh dun

# Gizmos:
# Make evrt 2D
# texture rainbow effect

archive = 0

def run():
    global root
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
    modelviewer.urs.application.quit()
    

if __name__ == "__main__":
    Thread(target=run).start()
    
    
    modelviewer.init()
    modelviewer.app.run()
    root.destroy()
    
    