import numpy as np
import math as m
  
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