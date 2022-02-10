import struct
import math
import simple_object
import section_header
import section
import table

class ho_archive:
    def __init__(self, path):
        self.path = path
        
        self.section_count = 0
        self.section_offset = 0
        self.section_headers = self.get_section_headers()
        self.get_sections() # <--- the headers contain the sections
        
        self.simple_objects = self.get_simple_objects()
        self.get_models()
        self.get_names()
    
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
                
                
                bytes_to_write += file.read(offset-file.tell()+0x20) + rotation_data + position_data + scale_data
                file.read(0x24)
                bytes_to_write += file.read(0x54)
                file.read(0x08)
                bytes_to_write += mass_data + friction_data
                
            bytes_to_write += file.read()
            
        with open(self.path, "wb") as file:
            file.seek(0)
            file.write(bytes_to_write)
            
        
    def get_names(self):
        with open(self.path, "rb") as file:
            file.seek(self.section_headers[1].child_data_offset)
            
            while file.tell() < (self.section_headers[1].child_data_offset + self.section_headers[1].child_data_length):
                  
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
                    
                
    #print(simp[-1].name)
        
    def get_models(self):
        
        with open(self.path, "rb") as file:
            for si, simp in enumerate(self.simple_objects):
                # Now simp.model_id will be, you guessed it, the model id.
                # This piece of code is gonna go through all tables and search for that ID.
                # Then it will do the same for the ids in those assets.
                # This goes on for a bit till we have everything.
                model_ids = []
                modelroots = [] 
                texture_id = 0
                texture = [] # Root
                break_flag = False
                bone_length = 0
                
                for xi, x in enumerate(self.section_headers):
                    for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                        for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                            if i[4] == simp.model_id:
                                file.seek(i[1]) # Seek entry offset
                                file.read(0x60)
                                model_header_id = file.read(0x08)
                                
                                break_flag = True
                            if break_flag: break
                        if break_flag: break
                    if break_flag: break
                
                
                break_flag = False
                for xi, x in enumerate(self.section_headers):
                    for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                        for ii, i in enumerate(y.entries): # Now "i" will be a single entry
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
                                
                                break_flag = True
                            
                            if break_flag: break
                        if break_flag: break
                    if break_flag: break
                    
                break_flag = False
                for xi, x in enumerate(self.section_headers):
                    for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                        for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                            if i[4] == material_id:
                                file.seek(i[1])
                                file.read(0x30)
                                
                                texture_id = file.read(0x08) # Semi Texture id
                                
                                break_flag = True
                            
                            if break_flag: break
                        if break_flag: break
                    if break_flag: break
                
                break_flag = False
                for xi, x in enumerate(self.section_headers):
                    for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                        for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                            if i[4] == texture_id:
                                file.seek(i[1])
                                
                                texture_id = file.read(0x08) # Actual Texture ID
                                
                                break_flag = True
                            
                            if break_flag: break
                        if break_flag: break
                    if break_flag: break
                
                
                break_flag = False
                for xi, x in enumerate(self.section_headers):
                    for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                        for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                            if i[4] == texture_id:
                                texture = [xi, yi, ii] # Actual texture ID
                                
                                break_flag = True
                            
                            if break_flag: break
                        if break_flag: break
                    if break_flag: break
                
                for z in model_ids:
                    break_flag = False
                    for xi, x in enumerate(self.section_headers):
                        for yi, y in enumerate(x.child.layers): # Now "y" will be a table
                            for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                                if i[4] == z:
                                    
                                    modelroots.append([xi, yi, ii])
                                    
                                    break_flag = True
                                
                                if break_flag: break
                            if break_flag: break
                        if break_flag: break
                    
                if modelroots == [] or texture == []:
                    self.simple_objects[si] = "delete"
                    continue
                
                simp.bone_length = bone_length
                simp.model = modelroots
                simp.texture = texture
        
        self.simple_objects = list(filter(("delete").__ne__, self.simple_objects)) # Removes Objects with no data from List
                            
    def get_simple_objects(self):
        simple_objects = []
        
        with open(self.path, "rb") as file:
            for yi, y in enumerate(self.section_headers[0].child.layers): # Now "y" will be a table
                for ii, i in enumerate(y.entries): # Now "i" will be a single entry
                    if i[5] == b"\xAF\x4D\x62\x21" or i[5] == b"\x9D\x5F\x55\x0F":
                        file.seek(i[1]+0x20)
                        rotation = (byte_to_float(file.read(0x04))*180/math.pi, byte_to_float(file.read(0x04))*180/math.pi, byte_to_float(file.read(0x04))*180/math.pi)
                        rotation = (rotation[1], 180-rotation[0], rotation[2])
                        position = (byte_to_float(file.read(0x04)), byte_to_float(file.read(0x04)), -byte_to_float(file.read(0x04)))
                        scale = (byte_to_float(file.read(0x04)), byte_to_float(file.read(0x04)), byte_to_float(file.read(0x04)))
                        
                        file.read(0x0c)
                        model_id = file.read(0x08)
                        
                        file.read(0x38)
                        anim_id = file.read(0x08)
                            
                        mass = byte_to_float(file.read(0x04))
                        friction = byte_to_float(file.read(0x04))
                        
                        simple_objects.append(simple_object.simple_object([0, yi, ii], i[4], position, rotation, scale, model_id, anim_id, mass, friction))
    
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
                
                file.read(0x14)
                
                # This is the code for fetching the tables
                tables = [[[0, 0], [0, 0], [0, 0], []] for i in range(int((layer_count-1)/3))] #last one is for entries
                
                if name != "PSLD":
                    counters = [0, 0, 0] # offset, data, padding
                    complete_offset = 0
                    for x in range(layer_count-1):
                        table_flag = int.from_bytes(file.read(0x04), "big")
                        table_offset = int.from_bytes(file.read(0x04), "big")
                        table_length = int.from_bytes(file.read(0x04), "big")
                        file.read(0x04)
                        
                        tables[counters[table_flag]][table_flag] = [complete_offset + i.child_data_offset, table_length]
                        complete_offset += table_length
                        
                        counters[table_flag] += 1
                    
                    return_addr = file.tell()
                    # This code fetches the entries
                    # Entry = [Length+Padding, offset, Length, flag, id, type]
                    complete_offset = i.child_data_offset
                    for x in tables:
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
            
                layers = [table.table(tables[z][0], tables[z][1], tables[z][2], tables[z][3]) for z in range(int((layer_count-1)/3))]
                
                sections.append(section.section(offset, length, layer_count, layers))
                i.child = sections[-1]
                
            

            
            
            

    
    
# --Modelhelpers-- #
def float_to_byte(float_input):
    return struct.pack("f", float_input)[::-1]

def byte_to_float(hex_input):
    return struct.unpack('!f', hex_input)[0]


def get_vertices(file, offset, length):
    verts = []

    file.seek(offset)
    for i in range(int(length/12)):
        verts.append((-byte_to_float(file.read(4)), byte_to_float(file.read(4)), byte_to_float(file.read(4))))

    return verts


def get_faces(file, offset, length, reference_amount, anim_amount):
    indices = []
    
    file.seek(offset)
    while file.tell() < offset+length:
        test = file.read(1)
        if test == b"\x98" or test == b"\x90":
            indices.append([])
            for i in range(int.from_bytes(file.read(2), "big")):
                temp = []
                file.read(anim_amount)
                for x in range(reference_amount):
                    temp.append(int.from_bytes(file.read(2), "big"))
                indices[-1].append(temp)
                  
    faces = []
    for i in indices:
        for x in range(len(i)-2):
            faces.append((i[x][0], i[x+1][0], i[x+2][0]))
        
    return faces