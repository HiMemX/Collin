import math
import math as m
import numpy
import numpy as np
from scipy.spatial.transform import Rotation as R
import struct


def scale(vert, scale):
    return [vert[0]*scale[0], vert[1]*scale[1], vert[2]*scale[2]]


def getVectorLength(vector):
    return math.sqrt(sum([element**2 for element in vector[:3]]))

def matrixToTransformation(matrix):
    position = [matrix[0][3], matrix[1][3], matrix[2][3]]
    scale = [getVectorLength(matrix[0]), getVectorLength(matrix[1]), getVectorLength(matrix[2])]
    
    rotationmatrix = [[matrix[m][n]/scale[n] for n in range(3)] for m in range(3)]
    
    
    rotation = R.from_matrix(rotationmatrix).as_euler("xyz").tolist()
    
    #print(rotationmatrix)
    #print(rotation)
    
    return position, rotation, scale


def transformationToMatrix(position, rotation, scale):
    
    rotationmatrix = R.from_rotvec(numpy.array(rotation)).as_matrix().tolist()
    #print(rotation)
    #print(rotationmatrix)
    rotationmatrix[0].append(0)
    rotationmatrix[1].append(0)
    rotationmatrix[2].append(0)
    
    positionmatrix = [
        [1, 0, 0, position[0]],
        [0, 1, 0, position[1]],
        [0, 0, 1, position[2]]
    ]
    scalematrix = [
        [scale[0], 0, 0, 0],
        [0, scale[1], 0, 0],
        [0, 0, scale[2], 0]  
    ]
    temp = dot(rotationmatrix, scalematrix).tolist()[:3]
    temp2 = dot(positionmatrix, temp).tolist()[:3]
    #print(temp, temp2)
    return temp2

def Rx(theta):
    return np.matrix([[ 1, 0           , 0           ],
                   [ 0, m.cos(theta),-m.sin(theta)],
                   [ 0, m.sin(theta), m.cos(theta)]])
  
def Ry(theta):
    return np.matrix([[ m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])
  
def Rz(theta):
    return np.matrix([[ m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

def transform(point, position, angle):
    rotation = Rz(m.radians(angle[2])) * Ry(m.radians(angle[1])) * Rx(m.radians(angle[0]))
    point = (rotation.dot(np.array(point))).tolist()[0]
    point = (-point[0]-position[0], point[1]+position[1], -point[2]-position[2])
    
    return point

def scale(point, factors):
    return (point[0]*factors[0], point[1]*factors[1], point[2]*factors[2])

def dot(m1, m2):
    m1 += [[0, 0, 0, 1]]
    m2 += [[0, 0, 0, 1]]
    return numpy.dot(m1, m2)

def toFloatMatrix(data):
    return [[byte_to_float(data[x+y:x+y+4]) for x in range(0, 0x10, 0x04)] for y in range(0, 0x30, 0x10)]


def byte_to_float(hex_input):
    return struct.unpack('!f', hex_input)[0]

    
    
    
    
