import simple_object
import pyhotools
import math


def save(file, offset, rotation_data, position_data, scale_data, mass_data, friction_data, i):
    bytes_to_write = b""
    bytes_to_write += file.read(offset-file.tell())
    bytes_to_write += i.id; file.read(0x08)
    
    if i.type == b"\xAF\x4D\x62\x21" or i.type == b"\x9D\x5F\x55\x0F" or i.type == b"\x42\xD9\x0B\xD1":
        bytes_to_write += file.read(0x18)
            
        bytes_to_write += rotation_data + position_data + scale_data; file.read(0x24)
        
        bytes_to_write += file.read(0x0C)
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x30)
        bytes_to_write += i.id; file.read(0x08)
        
        bytes_to_write += i.anim_id; file.read(0x08)
        
        bytes_to_write += mass_data + friction_data; file.read(0x08)                
    
    elif i.type == b"\xEB\x1F\xD6\x7E":
        bytes_to_write += file.read(0x08)
        bytes_to_write += i.id; file.read(0x08)
        
        bytes_to_write += file.read(0x18)
            
        bytes_to_write += rotation_data + position_data + scale_data; file.read(0x24)
        
        bytes_to_write += file.read(0x0C)
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x30)
        bytes_to_write += i.id; file.read(0x08)
        
        bytes_to_write += i.anim_id; file.read(0x08)
        
        bytes_to_write += mass_data + friction_data; file.read(0x08)                
    
    
    elif i.type == b"\x0B\x54\xBB\x17":
        bytes_to_write += file.read(0x08)
            
        bytes_to_write += rotation_data + position_data + scale_data; file.read(0x24)
        
        bytes_to_write += file.read(0x0C)
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x30)
        bytes_to_write += i.id; file.read(0x08)
        
        bytes_to_write += file.read(0x08)
        bytes_to_write += mass_data + friction_data; file.read(0x08)
        
    elif i.type == b"\x00\x11\x73\x1B":
        bytes_to_write += file.read(0x18)
            
        bytes_to_write += (b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        file.read(0x24)
        
        bytes_to_write += file.read(0x0C)
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x30)
        bytes_to_write += i.id; file.read(0x08)
        
        bytes_to_write += file.read(0x08)
        bytes_to_write += b"\x00\x00\x00\x00\x3F\x00\x00\x00"; file.read(0x08)
        
    elif i.type == b"\xC3\x33\x07\x2E":
        bytes_to_write += file.read(0x18)
        
        bytes_to_write += i.model_id; file.read(0x08)
        bytes_to_write += file.read(0x38)
        
        bytes_to_write += position_data; file.read(0x0C)
    
    elif i.type == b"\x60\xB1\xE6\x28":
        bytes_to_write += file.read(0x10)
        
        bytes_to_write += position_data
        bytes_to_write += rotation_data
        bytes_to_write += scale_data; file.read(0x24)
        
        bytes_to_write += file.read(0x04)
        
        bytes_to_write += i.model_id; file.read(0x08)
        
    elif i.type == b"\xF3\xDA\x1F\x7F" or i.type == b"\x3B\x31\x4D\xFD" or i.type == b"\x50\x5D\xD6\xA4":
        bytes_to_write += file.read(0x08)
        bytes_to_write += rotation_data 
        bytes_to_write += position_data; file.read(0x18)
        
        bytes_to_write += file.read(0x08)
        
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x38)
        
        bytes_to_write += scale_data; file.read(0x0C)
        
    elif i.type == b"\xFD\x5F\x1E\xC7" or i.type == b"\x63\x37\x8F\xE3":
        bytes_to_write += file.read(0x08)
        bytes_to_write += i.model_id; file.read(0x08)
        
        bytes_to_write += file.read(0x38)
        
        bytes_to_write += position_data
        bytes_to_write += rotation_data; file.read(0x18)
        
           
        
    return bytes_to_write
                
                
                
                
                
                
                
                
                
                
def cast(file, typeid, xy, yi, ii, i):
    if typeid == b"\xAF\x4D\x62\x21" or typeid == b"\x9D\x5F\x55\x0F" or typeid == b"\x42\xD9\x0B\xD1":
        file.read(0x20)
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        scale = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)))
        
        file.read(0x0c)
        model_id = file.read(0x08)
        
        file.read(0x38)
        anim_id = file.read(0x08)
            
        mass = pyhotools.byte_to_float(file.read(0x04))
        friction = pyhotools.byte_to_float(file.read(0x04))
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    elif typeid == b"\xEB\x1F\xD6\x7E":
        file.read(0x30)
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        scale = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)))
        
        file.read(0x0c)
        model_id = file.read(0x08)
        
        file.read(0x38)
        anim_id = file.read(0x08)
            
        mass = pyhotools.byte_to_float(file.read(0x04))
        friction = pyhotools.byte_to_float(file.read(0x04))
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    elif typeid == b"\x00\x11\x73\x1B":
        file.read(0x44)
        rotation = (0, 180, 0)
        position = (0, 0, 0)
        scale = (1, 1, 1)
        
        file.read(0x0c)
        model_id = file.read(0x08)
        
        file.read(0x38)
        anim_id = file.read(0x08)
            
        mass = pyhotools.byte_to_float(file.read(0x04))
        friction = pyhotools.byte_to_float(file.read(0x04))
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    elif typeid == b"\x0B\x54\xBB\x17":
        file.read(0x10)
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        scale = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)))
        
        file.read(0x0c)
        model_id = file.read(0x08)
        
        file.read(0x38)
        anim_id = file.read(0x08)
            
        mass = 0
        friction = 0
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    elif typeid == b"\xC3\x33\x07\x2E":
        file.read(0x20)
        
        model_id = file.read(0x08)
        
        file.read(0x38)
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        rotation = (0, 0, 0)
        scale = (1, 1, 1)
        
        anim_id = b"\x00\x00\x00\x00\x00\x00\x00\x00"
            
        mass = 0
        friction = 0
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    elif typeid == b"\x60\xB1\xE6\x28":
        file.read(0x18)
        
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        scale = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)))
        
        file.read(0x04)
        
        model_id = file.read(0x08)
        
        anim_id = b"\x00\x00\x00\x00\x00\x00\x00\x00"
            
        mass = 0
        friction = 0
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
        
    elif typeid == b"\xF3\xDA\x1F\x7F" or typeid == b"\x3B\x31\x4D\xFD" or typeid == b"\x50\x5D\xD6\xA4":
        file.read(0x10)
        
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        
        file.read(0x08)
        
        model_id = file.read(0x08)
        
        file.read(0x38)
        
        scale = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)))
        
        anim_id = b"\x00\x00\x00\x00\x00\x00\x00\x00"
            
        mass = 0
        friction = 0
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
        
    elif typeid == b"\xFD\x5F\x1E\xC7" or typeid == b"\x63\x37\x8F\xE3":
        file.read(0x10)
        
        model_id = file.read(0x08)
        
        file.read(0x38)
        
        position = (pyhotools.byte_to_float(file.read(0x04)), pyhotools.byte_to_float(file.read(0x04)), -pyhotools.byte_to_float(file.read(0x04)))
        rotation = (pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi, pyhotools.byte_to_float(file.read(0x04))*180/math.pi)
        rotation = (rotation[1], 180-rotation[0], rotation[2])
        scale = (1, 1, 1)
        
        anim_id = b"\x00\x00\x00\x00\x00\x00\x00\x00"
            
        mass = 0
        friction = 0
        
        return simple_object.simple_object([xy, yi, ii], i[4], typeid, position, rotation, scale, model_id, anim_id, mass, friction)
    
    return None
