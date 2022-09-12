import struct
import math
import simple_object
import section_header
import section
import table
import cmpr
import numpy as np
import castsimpleobject

class ho_archive:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        
        self.section_count = 0
        self.section_offset = 0
        self.section_headers = self.get_section_headers()
        self.get_sections() # <--- the headers contain the sections
        
        self.simple_objects = self.get_simple_objects()
        self.get_names()
        self.get_models()
        
    
    def overwrite(self, file, offset, data):
        file.seek(0)
        firstpart = file.read(offset)
        file.read(len(data))
        lastpart = file.read()
        
        file.seek(0)
        file.write(firstpart + data + lastpart)
    
    def save_archive(self):
        bytes_to_write = b""
        
        with open(self.path, "rb") as file:
            for i in self.simple_objects:
                offset = self.section_headers[i.root[0]].child.layers[i.root[1]].entries[i.root[2]][1]
                
                rotation_data   = float_to_byte(math.radians(180-i.rotation[1])) + float_to_byte(math.radians(i.rotation[0])) + float_to_byte(math.radians(i.rotation[2]))
                position_data   = float_to_byte(i.position[0]) + float_to_byte(i.position[1]) + float_to_byte(-i.position[2])
                scale_data      = float_to_byte(i.scale[0]) + float_to_byte(i.scale[1]) + float_to_byte(i.scale[2])
                
                mass_data = float_to_byte(i.mass)
                friction_data = float_to_byte(i.friction)
                
                bytes_to_write += castsimpleobject.save(file, offset, rotation_data, position_data, scale_data, mass_data, friction_data, i)
                
            bytes_to_write += file.read()
            
        with open(self.path, "wb") as file:
            file.seek(0)
            file.write(bytes_to_write)
            
        return
        
        for i in self.simple_objects:
            z = 0
            newdata = verts_to_bytes(i.model_class.model.vertices)
            newlength = len(newdata)
            newlengthpad = math.ceil(newlength/0x20)*0x20
            self.section_headers[i.model[z][0]].child.layers[i.model[z][1]].entries[i.model[z][2]][2] = newlength
            self.section_headers[i.model[z][0]].child.layers[i.model[z][1]].entries[i.model[z][2]][0] = newlengthpad
            self.update_section_headers()
            
            bytes_to_write = b""
            #with open(self.path, "rb") as file:
                
    def get_names(self):
        with open(self.path, "rb") as file:
            for section_header in self.section_headers:
                if section_header.name != "PD  ":
                    continue
                
                file.seek(section_header.child.offset)
                file.read(0x0C)
                file.seek(section_header.child_data_offset + int.from_bytes(file.read(0x04), "big"))
                
                while file.tell() < (section_header.child_data_offset + section_header.child_data_length):
                      
                    id_ = file.read(0x08)
                    file.read(0x18)   
                    name = ""
                    while True:
                        character = file.read(0x01)
                        if character == b"\x00":
                            file.seek(math.ceil(file.tell() / 0x40) * 0x40)
                            break
                        
                        name += character.decode("ANSI")
                    
                    for simp in self.simple_objects:
                        if simp.id == id_:
                            simp.name = name
                            
    def iter_assets(self):
        assets = []
        for xi, x in enumerate(self.section_headers):
            for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                for ii, i in enumerate(y.entries):
                    assets.append(i)
        return assets
    
    def get_models(self):
        with open(self.path, "rb") as file:
            known_ids = []
            for si, simp in enumerate(self.simple_objects):
                # Now simp.model_id will be, you guessed it, the model id.
                # This piece of code is gonna go through all tables and search for that ID.
                # Then it will do the same for the ids in those assets.
                # This goes on for a bit till we have everything.
                break_flag = False
                for known in known_ids:
                    if simp.model_id == known[0]:
                        simp.model = known[1]
                        simp.texture = known[3]
                        simp.bone_length = known[2]
                        simp.size_divisor = known[4]
                        simp.texture_ids = known[5]
                        simp.transformation = known[6]
                        simp.global_transforms = known[7]
                        simp.visibilities = known[8]
                        simp.pfst = known[9]
                        break_flag = True
                        break
                        
                if break_flag:
                    continue
                
                fin_modelroots = []
                fin_textures = []
                fin_texture_ids = []
                fin_bone_lengths = []
                fin_size_divisors = []
                transformation_matrices = []
                global_transforms = []
                fin_visible = []
                pfst = False
                model_header_ids = []
                more_model_ids = []
                break_flag = False
                bone_length = 0
                
                iteration = self.iter_assets()
                for ii, i in enumerate(iteration):
                    if i[4] == simp.model_id:
                        file.seek(i[1]+0x02) # Seek entry offset
                        mesh_amount = int.from_bytes(file.read(0x02), "big")
                        float_amount = int.from_bytes(file.read(0x02), "big")
                        more_model_id_amount = int.from_bytes(file.read(0x02), "big")
                        
                        file.read(0x58 + float_amount*0x30) #file.read(0x58 + float_amount*0x30)
                        for g in range(mesh_amount):
                            model_header_ids.append(file.read(0x08))
                        
                        for g in range(more_model_id_amount):
                            more_model_ids.append(file.read(0x08))
                        
                        break
                
                
                for mi, model_header_id in enumerate(model_header_ids):
                    model_ids = []
                    modelroots = []
                    effect_index = 0
                    texture_id = b"\x00\x00\x00\x00\x00\x00\x00\x00"
                    material_text_id = 0
                    texture = None # Root
                    break_flag = False
                    for ii, i in enumerate(iteration): # Now "i" will be a single entry
                        if i[4] == model_header_id:
                            file.seek(i[1])
                            file.read(0x28)
                            material_id = file.read(0x08)
                            
                            file.read(0x03)
                            bone_length = int.from_bytes(file.read(0x01), "big")
                            
                            file.read(0x05) # Contains amount of mesh data
                            reference_amount = int.from_bytes(file.read(0x01), "big")
                            
                            file.read(0x0a)
                            reference_offset = int.from_bytes(file.read(0x04), "big")
                            
                            file.seek(i[1])
                            file.read(reference_offset)
                            
                            for i in range(reference_amount):
                                model_ids.append(file.read(0x08))
                                
                                file.read(0x08)
                                
                            model_ids.append(file.read(0x08))
                            
                            # Delete this once you can
                            
                            file.read(0x28)
                            zeroth_texture = file.read(0x08)
                            
                            file.read(0x08)
                            first_texture = file.read(0x08)
                            
                            file.read(0x18)
                            secondary_texture = file.read(0x08)
                            
                            file.read(0x08)
                            third_texture = file.read(0x08) 
                            # -------
                            
                            break
                        
                    
                    for ii, i in enumerate(iteration): # Now "i" will be a single entry
                        if i[4] == material_id:
                            file.seek(i[1])
                            effect_id = file.read(0x08)
                            
                            file.read(0x14)
                            file.seek(i[1]+int.from_bytes(file.read(0x04), "big"))
                            
                            material_text_id = file.read(0x08) # Semi Texture id
                            
                            #if int.from_bytes(texture_id, "big") == 4575657222473777152:
                            #    print(file.tell())
                            
                            break
                        
                    
                    for ii, i in enumerate(iteration): # Now "i" will be a single entry
                        if i[4] == effect_id:
                            file.seek(i[1])
                            file.read(0x28)
                            generic_shader = file.read(0x08)
                            
                            break
                     
                    for ii, i in enumerate(iteration): # Now "i" will be a single entry
                        if i[4] == generic_shader:
                            file.seek(i[1])
                            file.read(0x97)
                            size_divisor = []
                            size_divisor.append(int.from_bytes(file.read(0x01), "big"))
                            size_divisor.append(int.from_bytes(file.read(0x01), "big"))
                            
                            break
                    
                    break_flag = False
                    for ii, i in enumerate(iteration): # Now "i" will be a single entry
                        if i[4] == material_text_id:
                            file.seek(i[1])
                            
                            texture_id = file.read(0x08) # Actual Texture ID
                            file.read(0x04)
                            visibility = byte_to_float(file.read(0x04))
                            
                            break_flag = True
                        
                            break
                    
                    if break_flag == False:
                        for ii, i in enumerate(iteration): # Now "i" will be a single entry
                            if i[4] == zeroth_texture or i[4] == first_texture or i[4] == secondary_texture or i[4] == third_texture:
                                file.seek(i[1])
                                
                                texture_id = file.read(0x08) # Actual Texture ID
                                file.read(0x04)
                                visibility = byte_to_float(file.read(0x04))
                            
                                break  
                    
                    break_flag = False
                    for xi, x in enumerate(self.section_headers):
                        for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                            for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                                if i[4] == texture_id:
                                    texture = [xi, yi, ii] # Actual texture ID
                                    
                                    break_flag = True
                                
                                    break
                            if break_flag: break
                        if break_flag: break
                    
                    for z in model_ids:
                        break_flag = False
                        for xi, x in enumerate(self.section_headers):
                            for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                                for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                                    if i[4] == z:
                                        if x.name == "PFST": pfst = True
                                        
                                        modelroots.append([xi, yi, ii])
                                        
                                        break_flag = True
                                    
                                        break
                                if break_flag: break
                            if break_flag: break
                    
                    if modelroots == []:
                        continue
                    
                    #print(simp.name, secondary_texture, texture_id)#, material_id, model_header_id)
                    fin_modelroots.append(modelroots)
                    fin_bone_lengths.append(bone_length)
                    fin_textures.append(texture)
                    fin_texture_ids.append(texture_id.hex())
                    fin_size_divisors.append(size_divisor)
                    fin_visible.append(visibility)
                    
                known_ids.append([simp.model_id, fin_modelroots, fin_bone_lengths, fin_textures, fin_size_divisors, fin_texture_ids, transformation_matrices, global_transforms, fin_visible, pfst])
                
                simp.model = fin_modelroots
                simp.texture = fin_textures
                simp.visibilities = fin_visible
                simp.texture_ids = fin_texture_ids
                simp.bone_length = fin_bone_lengths
                simp.size_divisor = fin_size_divisors
                simp.transformation = transformation_matrices
                simp.global_transforms = global_transforms
                simp.pfst = pfst
        
    def get_simple_objects(self):
        simple_objects = []
        
        with open(self.path, "rb") as file:
            for xy, x in enumerate(self.section_headers):
                for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                    for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                        file.seek(i[1])
                        temp = castsimpleobject.cast(file, i[5], xy, yi, ii, i)
                        if temp == None: continue
                        simple_objects.append(temp)
                        
        return simple_objects
        
    def get_section_headers(self):
        section_headers = []
        
        with open(self.path, "rb") as file:
            file.seek(0x83c) # <-- 0x83c contains the offset to the sects divided by 0x800
            file.seek(int.from_bytes(file.read(0x04), "big")*0x800+0x04)
            
            self.section_count = int.from_bytes(file.read(0x04), "big"); file.read(0x0c)
            self.section_offset = int.from_bytes(file.read(0x04), "big") + file.tell() - 0x18; file.read(0x08)
            
            
            for i in range(self.section_count):
                offset = file.tell()
                name = file.read(0x04).decode("ANSI"); file.read(0x18)
                child_data_offset = int.from_bytes(file.read(0x04), "big") * 0x800
                child_data_length = int.from_bytes(file.read(0x04), "big"); file.read(0x1c)
                
            
                section_headers.append(section_header.section_header(offset, name, child_data_offset, child_data_length))
                
        return section_headers
    
    def get_sections(self):
        sections = []
        
        with open(self.path, "rb") as file:
            file.seek(self.section_offset)
            
            for i in self.section_headers:
                offset = file.tell()
                name = file.read(0x04).decode("ANSI")
                length = int.from_bytes(file.read(0x04), "big")
                layer_count = int.from_bytes(file.read(0x04), "big")
                
                file.read(0x04)
                
                # This is the code for fetching the tables
                tables = [[[0,0], [0,0], [0,0], []] for i in range(int((layer_count-1)/3))] #last one is for entries
                
                if name != "PSLD":
                    complete_offset = 0
                    table_flag_first = file.read(0x04)
                    file.seek(file.tell()-0x04)
                    
                    if table_flag_first == b"\x00\x00\x00\x00":
                        for x in range(int((layer_count-1)/3)):
                            file.read(0x04)
                            table_offset = int.from_bytes(file.read(0x04), "big")
                            table_length = int.from_bytes(file.read(0x04), "big")
                            file.read(0x04)
                            
                            tables[x][0] = [complete_offset + i.child_data_offset, table_length]
                            complete_offset += table_length
                        
                        file.read(0x04)
                        table_offset = int.from_bytes(file.read(0x04), "big")
                        table_length = int.from_bytes(file.read(0x04), "big")
                        file.read(0x04)
                        complete_offset += table_length
                        
                        for x in range(int((layer_count-1)/3)):
                            for y in range(2):
                                file.read(0x04)
                                table_offset = int.from_bytes(file.read(0x04), "big")
                                table_length = int.from_bytes(file.read(0x04), "big")
                                file.read(0x04)
                                
                                tables[x][1-y+1] = [complete_offset + i.child_data_offset, table_length]
                                complete_offset += table_length
                            
                    else:
                        for x in range(int((layer_count-1)/3)):
                            for y in range(2):
                                file.read(0x04)
                                table_offset = int.from_bytes(file.read(0x04), "big")
                                table_length = int.from_bytes(file.read(0x04), "big")
                                file.read(0x04)
                                
                                tables[x][1-y+1] = [complete_offset + i.child_data_offset, table_length]
                                complete_offset += table_length
                        
                        file.read(0x04)
                        table_offset = int.from_bytes(file.read(0x04), "big")
                        table_length = int.from_bytes(file.read(0x04), "big")
                        file.read(0x04)
                        complete_offset += table_length
                        
                        for x in range(int((layer_count-1)/3)):
                            file.read(0x04)
                            table_offset = int.from_bytes(file.read(0x04), "big")
                            table_length = int.from_bytes(file.read(0x04), "big")
                            file.read(0x04)
                            
                            tables[x][0] = [complete_offset + i.child_data_offset, table_length]
                            complete_offset += table_length
                    
                    return_addr = file.tell()
                    # This code fetches the entries
                    # Entry = [Length+Padding, offset, Length, flag, id, type]
                    
                    for x in tables:
                        complete_offset = x[1][0]
                        file.seek(x[0][0])
                        asset_count = int.from_bytes(file.read(0x04), "big")
                        file.read(0x1c)
                        
                        for y in range(asset_count):
                            asset_length_padding = int.from_bytes(file.read(0x04), "big")
                            file.read(0x04)
                            asset_length = int.from_bytes(file.read(0x04), "big")
                            asset_flag = int.from_bytes(file.read(0x04), "big")
                            asset_id = file.read(0x08)
                            asset_type = file.read(0x04)
                            file.read(0x04)
                            
                            x[3].append([asset_length_padding, complete_offset, asset_length, asset_flag, asset_id, asset_type])
                
                            complete_offset += asset_length_padding
                        
                
                    file.seek(return_addr)
                    
                else:
                    file.read(0x10)
                
                layers = [table.table(tables[z][0], tables[z][1], tables[z][2], tables[z][3]) for z in range(int((layer_count-1)/3))]
                
                sections.append(section.section(offset, length, layer_count, layers))
                i.child = sections[-1]
                
            

            
            
            

    
    
# --Modelhelpers-- #
def float_to_byte(float_input):
    return struct.pack("f", float_input)[::-1]

def byte_to_float(hex_input):
    return struct.unpack('!f', hex_input)[0]

def verts_to_bytes(verts):
    byte_verts = b""
    
    for vert in verts:
        for i in range(3):
            byte_verts += float_to_byte(vert[i])
            
    return byte_verts

def get_colors(file, offset, length):
    colors = []
    
    file.seek(offset)
    for i in range(int(length/4)):
        colors.append((int.from_bytes(file.read(0x01), "big"), int.from_bytes(file.read(0x01), "big"), int.from_bytes(file.read(0x01), "big")))
        file.read(0x01)
        
    return colors

def get_vertices(file, offset, length):
    verts = []

    file.seek(offset)
    for i in range(int(length/12)):
        verts.append((-byte_to_float(file.read(4)), byte_to_float(file.read(4)), byte_to_float(file.read(4))))

    return verts

def get_vertices_pfst(file, offset_in, length_in): # Translated from DynamicGeometries PfstVertexRawblob
    file.seek(offset_in)
    data = file.read(length_in)
    
    
    offset = 0x00
    verts = []

    offsetskip = 0x14

    while offset < len(data):
        buffer = data[offset:offset+0x14]

        X1 = int.from_bytes(buffer[0x00:0x02], "big", signed=True)/2**12
        X2 = int.from_bytes(buffer[0x02:0x04], "big", signed=True)/2**12
        
        Y1 = int.from_bytes(buffer[0x04:0x06], "big", signed=True)/2**12
        Y2 = int.from_bytes(buffer[0x06:0x08], "big", signed=True)/2**12
        
        Z1 = int.from_bytes(buffer[0x08:0x0A], "big", signed=True)/2**12
        Z2 = int.from_bytes(buffer[0x0A:0x0C], "big", signed=True)/2**12
        
        #print(int.from_bytes(buffer[0x00:0x02], "big"), X1, buffer.hex())
        verts.append((X1, Y1, Z1))
        verts.append((X2, Y2, Z2))


        # Type Check
        if len(data[offset+0x14:]) < 30:
            offset += offsetskip
            continue
        
        bufferlarge = data[offset:offset+0x44]
        first = int.from_bytes(bufferlarge[0x1C:0x20], "big")
        second = int.from_bytes(bufferlarge[0x20:0x24], "big")
        third = int.from_bytes(bufferlarge[0x40:0x44], "big")
        zerocheck = int.from_bytes(bufferlarge[0x12:0x14], "big")
        
        if (first == second or second == third or third == first) and zerocheck == 0:
            offsetskip = 0x24
        
        offset += offsetskip

    return verts


def get_uvs(file, offset, length):
    uvs = []
    
    file.seek(offset)
    for i in range(int(length/2)):
        uv = []
        uv.append(int.from_bytes(file.read(0x02), "big", signed=True))
        uv.append(int.from_bytes(file.read(0x02), "big", signed=True))
        uvs.append(uv)

    return uvs

def get_faces(file, offset_in, length, referenceamount, animamount, pfst):
    referenceamount += pfst
    file.seek(offset_in)
    data = file.read(length)
    offset = 0
    faces = []

    while offset < length:
        mode = data[offset:offset+1]
        offset += 0x01

        if mode == b"\x90": # Normal Definition Mode (Check out the modern ToS Wiki for more info)
            indexamount = int.from_bytes(data[offset:offset+2], "big")
            offset += 0x02
            for tri in range(int(indexamount/3)):
                face = []
                for indx in range(3):
                    index = []
                    offset += animamount

                    for reference in range(referenceamount):
                        index.append(int.from_bytes(data[offset:offset+0x02], "big"))
                        offset += 0x02

                    face.append(index) # UVS TEMPORARILY DISABLED
                        
                faces.append(face)

        elif mode == b"\x98":
            indexamount = int.from_bytes(data[offset:offset+2], "big")
            offset += 0x02
            face = []
            for tri in range(0, indexamount):
                index = []
                offset += animamount

                for reference in range(referenceamount):
                    index.append(int.from_bytes(data[offset:offset+0x02], "big"))
                    offset += 0x02

                face.append(index) # UVS TEMPORARILY DISABLED
            
            faces.append(face)
            #for i in range(len(face)-2):
            #    faces.append([face[i], face[i+1], face[i+2]])
    
    
    indices = []
    for i in faces:
        for x in range(len(i)-2):
            if (x+1) % 2 == pfst:
                indices.append(((i[x][0], i[x][-1], i[x][-2]), (i[x+2][0], i[x+2][-1], i[x+2][-2]), (i[x+1][0], i[x+1][-1], i[x+1][-2])))
                continue
            
            indices.append(((i[x][0], i[x][-1], i[x][-2]), (i[x+1][0], i[x+1][-1], i[x+1][-2]), (i[x+2][0], i[x+2][-1], i[x+2][-2])))

    return indices