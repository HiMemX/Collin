import transformations

def obj_export(path, entities, apply_transformation):
    with open(path+"/output.obj", "a") as file:
        file.write(f"mtllib output.mtl\n")
    
    verts_to_add = 0
    uvs_to_add = 0
    
    for ei, entity in enumerate(entities):
        verts_to_add_incr = 0
        uvs_to_add_incr = 0
        
        name = entity.name
        with open(path+"/output.mtl", "a") as file:
            file.write("Wavefront OBJ material file\n")
            for mi, model in enumerate(entity.meshes):
                file.write(f"\nnewmtl {name}{mi}\n")
                
                file.write(f"Ns 0\n")
                file.write(f"Ka 1.0 1.0 1.0\n")
                file.write(f"Kd 1 1 1\n")
                file.write(f"Ks 0 0 0\n")
            
                file.write(f"map_Kd " +  model.texture_id + ".png\n")
                if model.has_alpha: file.write(f"map_d " +  model.texture_id + "_t.png\n")
                
                file.write(f"illum 0\n")
      
        with open(path+"/output.obj", "a") as file:
            file.write("o " + str(name) + f"{ei}\n")
            
            for model in entity.meshes:
                for vert in model.complete_mesh[0]:
                    
                    if apply_transformation: # BSP
                        i = transformations.transform(transformations.scale(vert, entity.scale), entity.position, entity.rotation)
                    else:
                        i = vert
                        
                    file.write("v " + str(-i[0]) +" "+ str(i[1]) +" "+ str(i[2]) + "\n")
                    verts_to_add_incr += 1
                    
            for model in entity.meshes:
                for i in model.complete_mesh[1]:
                    file.write("vt " + str(i[0]) +" "+ str(i[1]) + "\n")
                    uvs_to_add_incr += 1
            
            for mi, model in enumerate(entity.meshes):
                file.write(f"\nusemtl {name}{mi}\n")
                file.write("s off\n")
                for i in model.complete_mesh[2]:
                    file.write(f"f {i[0][0]+1+verts_to_add}/{i[0][1]+1+uvs_to_add} {i[1][0]+1+verts_to_add}/{i[1][1]+1+uvs_to_add} {i[2][0]+1+verts_to_add}/{i[2][1]+1+uvs_to_add}\n")
            file.write("\n")
            
            verts_to_add += verts_to_add_incr
            uvs_to_add += uvs_to_add_incr
   
def obj_import(path):
    verts = []
    faces = []
    with open(path, "r") as file:
        for line in file:
            if line[0:2] == "v ":
                verts.append(line[2:].replace(",", ".").replace("\n", "").split(" "))
            
            elif line[0:2] == "f ":
                tri = []
                for i in range(3):
                    tri.append(int(line[2:].split(" ")[i].split("/", 1)[0])-1)
                    
                faces.append(tri)
                
    for i in range(len(verts)):
        verts[i] = (float(verts[i][0]), float(verts[i][1]), float(verts[i][2]))
    
    return verts, faces
    
if __name__ == "__main__":
    #obj_export(r"C:\Users\felix\Desktop", "test", [(0, 1, 2), (2, 3, 4), (6, 2, 1), (3, 5, 1)], [(0, 1, 2), (1, 2, 3)])
    print(obj_import(r"C:\Users\felix\Desktop\untitled.obj"))