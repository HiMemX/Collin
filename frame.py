import modelviewer
import pyhotools
from threading import Thread
import tkinter as tk
from tkinter import filedialog
import random


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry("500x500")
        
        self.listboxframe = tk.LabelFrame(self.parent, padx=10, pady=10, text="Objects")
        self.listboxframe.place(x=0, y=0)
        
        self.objectlist = tk.Listbox(self.listboxframe, height=27, width=65)
        self.objectlist.pack()
        self.objectlist.bind("<<ListboxSelect>>", self.update_selection)
        
        self.current_directory = r""
        
        self.menu = tk.Menu(self.parent)
        self.parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff="off")
        self.menu.add_cascade(label="File", menu=self.file_menu)
        
        self.extra_menu = tk.Menu(self.menu, tearoff="off")
        self.menu.add_cascade(label="Extra", menu=self.extra_menu)
        
        self.file_menu.add_command(label="Open .ho file", command=self.ask_directory)
        self.file_menu.add_command(label="Save .ho file", command=self.save_models)
        self.file_menu.add_command(label="Quit", command=self.quit)
        
        self.extra_menu.add_command(label="Physicate", command=self.physicate)
    
    def physicate(self):
        for ii, i in enumerate(self.ho_archive.simple_objects):
            if modelviewer.models[ii] == None:
                continue
            
            i.mass = 20
            i.friction = 10
            
            modelviewer.models[ii].mass = 20
            modelviewer.models[ii].friction = 10
        
        modelviewer.nametext.text = "Physicated!"
        
    def save_models(self):
        for ii, i in enumerate(self.ho_archive.simple_objects):
            if modelviewer.models[ii] == None:
                continue
            
            i.position = modelviewer.models[ii].position
            i.rotation = modelviewer.models[ii].rotation
            i.scale    = modelviewer.models[ii].scale
            i.mass     = modelviewer.models[ii].mass
            i.friction = modelviewer.models[ii].friction
            
        self.ho_archive.save_archive()
        modelviewer.nametext.text = "Saved!"
    
    def quit(self):
        self.parent.destroy()
    
    def update_selection(self, event):
        if modelviewer.selected_object == None:
            return
        
        modelviewer.models[modelviewer.selected_object].deselect()
        selection = event.widget.curselection()
        modelviewer.selected_object = selection[0]
        modelviewer.models[modelviewer.selected_object].select()
    
    def ask_directory(self):
        global current_directory
        self.current_directory = (str(tk.filedialog.askopenfilename()))
        self.ho_archive = pyhotools.ho_archive(self.current_directory)
        
        if len(self.ho_archive.simple_objects) == 0:
            return
        
        modelviewer.selected_object = None
        modelviewer.view_scene(self.ho_archive)
        self.update_listbox()
        
    def update_listbox(self):
        self.objectlist.delete(0, tk.END)
        for simp in self.ho_archive.simple_objects:
            self.objectlist.insert(tk.END, simp.name)

# To do list
# -----------
# -Create an editor

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
    
    