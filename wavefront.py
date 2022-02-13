def obj_export(path, name, verts, faces):
    with open(path+"/"+name+".obj", "w") as file:
        file.write("o " + str(name) + "\n")
        for i in verts:
            file.write("v " + str(i[0]) +" "+ str(i[1]) +" "+ str(i[2]) + "\n")
        
        file.write("s off\n")
        for i in faces:
            file.write("f " + str(i[0]+1) +" "+ str(i[1]+1) +" "+ str(i[2]+1) + "\n")

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