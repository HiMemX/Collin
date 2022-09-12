import time
import numpy as np
import PIL
import random
import PIL.Image

#offset = 0x8B8A20

#path = r"S:\Extracted roms\ToS WII\DATAmod\files\SB09\Levels\SHUB.ho"
#path  = r"C:\Users\felix\Desktop\SHUB.ho"
#path2 = r"C:\Users\felix\Desktop"

def png_to_rgb(path):
    image = plt.imread(path)[:,:,:3]
    new_image = []
    for y in image:
        new_image.append([])
        for x in y:
            new_image[-1].append((int(x[0]*255), int(x[1]*255), int(x[2]*255)))
            
    return new_image

def rgba_to_pngs(rgb, path, name):
    rgbarray = []
    rgbarray = np.array([np.array([[x[0], x[1], x[2]] for x in i], np.uint8) for i in rgb[0]], np.uint8)
    rgbimage = PIL.Image.fromarray(rgbarray, "RGB")
    
    if len(rgb) == 2:
        rgbaarray = []
        rgbaarray = np.array([np.array([sum(x)/3 for x in i], np.uint8) for i in rgb[1]], np.uint8)
        rgbaimage = PIL.Image.fromarray(rgbaarray, "L")
    
        rgbaimage.save(path+f"/{name}_t.png")
        
    rgbimage.save(path+f"/{name}.png")


def rgb_to_png(rgb, path, name):
    rgbarray = []
    rgbarray = np.array([np.array([[x[0], x[1], x[2]] for x in i], np.uint8) for i in rgb[0]], np.uint8)
    rgbimage = PIL.Image.fromarray(rgbarray, "RGB")
    
    if len(rgb) == 2:
        rgbaarray = np.array([np.array([sum(x)/3 for x in i], np.uint8) for i in rgb[1]], np.uint8)
        rgbaimage = PIL.Image.fromarray(rgbaarray, "L")
        rgbimage.putalpha(rgbaimage)
        
    rgbimage.save(path+f"/{name}.png")

def overwrite(file, offset, data):
    file.seek(0)
    first_part = file.read(offset)
    middle_part = data; file.read(len(data))
    last_part = file.read()
    
    file.seek(0)
    file.write(first_part+middle_part+last_part)

def rgb565(color):
    return (color >> 11 << 3 & 0xff, color >> 5 << 2 & 0xff, color >> 0 << 3 & 0xff)

def rgb888_to_rgb565(color):
    return ((color[0] >> 3 << 11) + (color[1] >> 2 << 5) + (color[2] >> 3)).to_bytes(2, byteorder="big")

def vadd(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2])

def vdivide(vector1, divisor):
    return (int(vector1[0] / divisor), int(vector1[1] / divisor), int(vector1[2] / divisor))

def vmul(vector1, factor):
    return (int(vector1[0] * factor), int(vector1[1] * factor), int(vector1[2] * factor))

def vdiff(vector1, vector2):
    return (abs(vector1[0] - vector2[0]) + abs(vector1[1] - vector2[1]) + abs(vector1[2] - vector2[2]))/(765)
        
def tpl_decompress(file, offset):
    file.seek(offset)
    file.read(0x04)
    
    image_headers = [] # [offset, ...]
    images = [] # [[sizex, sizey, mode, offset], [...], ...]
        
    image_count = int.from_bytes(file.read(0x04), "big")
    image_table_offset = int.from_bytes(file.read(0x04), "big") + offset

    file.seek(image_table_offset)
    for i in range(image_count):
        image_headers.append(int.from_bytes(file.read(0x04), "big") + offset)
        file.read(0x04)
    
    for i in image_headers:
        file.seek(i)
        
        sizey = int.from_bytes(file.read(0x02), "big")
        sizex = int.from_bytes(file.read(0x02), "big"); file.read(0x03)
        mode = file.read(0x01)
        image_offset = int.from_bytes(file.read(0x04), "big") + offset
        
        images.append([sizex, sizey, mode, image_offset])
    
    decompressed_images = []
    
    for i in images:
        file.seek(i[3])
    
        image = [[0 for z in range(i[0])] for y in range(i[1])]
        
        if i[2] == b"\x00":
            for ycblock in range(int(i[1]/8)):
                for xcblock in range(int(i[0]/8)):
                    for y in range(8):
                        for ymod in range(4):
                            indices = int.from_bytes(file.read(0x01), "big")
                            for x in range(2):
                                value = (indices >> ((1-x) * 4) & 15) << 4 
                                image[-1-(ycblock*8 + y)][xcblock*8 + (x+ymod*2)] = (value, value, value)
          
        elif i[2] == b"\x0E":
            for ycblock in range(int(i[1]/8)):
                for xcblock in range(int(i[0]/8)):
                    for yblock in range(2):
                        for xblock in range(2):
                            color1int = int.from_bytes(file.read(0x02), "big")
                            color2int = int.from_bytes(file.read(0x02), "big")
                            
                            color1 = rgb565(color1int)
                            color2 = rgb565(color2int)
                            
                            if color1int > color2int:
                                palette = [color1, color2, vadd(vmul(color1, 2/3), vmul(color2, 1/3)), vadd(vmul(color1, 1/3), vmul(color2, 2/3))]
                                
                            else:
                                palette = [color1, color2, vadd(vmul(color2, 0.5), vmul(color1, 0.5)), (0, 0, 0)]
                                                                 
                            for y in range(4):
                                indices = int.from_bytes(file.read(0x01), "big")
                                for x in range(4):
                                    image[-1-(ycblock*8 + yblock*4 + y)][xcblock*8 + xblock*4 + (3-x)] = palette[indices >> (x * 2) & 3]
        
        else:
            image = "INVALID_TYPE"
        
        decompressed_images.append(image)
    
    return decompressed_images

def tpl_compress(file, offset, images, mipmap_level):
    
    for image in images:
        sizey = len(image)
        sizex = len(image[0])
        bytecode = b""
        for mipmap in range(mipmap_level):
            for ycblock in range(int(sizey/8)):
                for xcblock in range(int(sizex/8)):
                    for yblock in range(2):
                        for xblock in range(2):        
                            
                            high_diff = 1
                            high = (0, 0, 0)
                            
                            low_diff = 1
                            low = (255, 255, 255)
                            for y in range(4):
                                for x in range(4):
                                    curr_pixel = image[(ycblock*8 + yblock*4 + y)][xcblock*8 + xblock*4 + x]
                                    diff = vdiff(curr_pixel, (255, 255, 255))
                                    
                                    if diff < high_diff:
                                        high_diff = diff
                                        high = curr_pixel
                                    
                                    diff = vdiff(curr_pixel, (0, 0, 0))
                                    
                                    if diff < low_diff:
                                        low_diff = diff
                                        low = curr_pixel
                            
                            
                            if rgb888_to_rgb565(low) < rgb888_to_rgb565(high):
                                palette = [high, low, vadd(vmul(high, 2/3), vmul(low, 1/3)), vadd(vmul(high, 1/3), vmul(low, 2/3))]
                            
                            else:
                                palette = [low, high, vadd(vmul(high, 0.5), vmul(low, 0.5)), (0, 0, 0)]
                            
                            
                            for i in range(2):
                                bytecode += rgb888_to_rgb565(palette[i])
                            
                            indices = ""
                            
                            for y in range(4):
                                for x in range(4):
                                    curr_pixel = image[(ycblock*8 + yblock*4 + y)][xcblock*8 + xblock*4 + x]
                                    
                                    low = 0
                                    diff = 1
                                    for i in range(len(palette)):
                                        curr_diff = vdiff(curr_pixel, palette[i])
                                        if curr_diff < diff:
                                            diff = curr_diff
                                            low = i
                                            
                                    indices += str(bin(low))[2:].zfill(2)
                                    
                            bytecode += int(indices, 2).to_bytes(4, byteorder="big")    
    
#image = [png_to_rgb(r"C:\Users\felix\Desktop\test.png"), b"\x0E"]

#tpl_compress(open(path, "wb"), offset, image, mipmap_level)
#mipify(open(path, "rb+"), offset, sizex, sizey)
                            
if __name__ == "__main__":
    rgb_to_png(tpl_decompress(open(path, "rb"), offset)[0], path2)