from numba import jit
import numpy as np
import math

def PixelXY2BodyPolar(inX, inY, inCamHor_FOV, inCamVer_FOV, inCamWidth, inCamHeight):
    ok = False
    el = 0
    az = 0
    inY = -inY

    if ( inX <= inCamWidth / 2  and (inX >= (-inCamWidth / 2))  and inY <= inCamHeight/2 and inY >= (-inCamHeight/2)):
        ok = True
        el = np.arctan(2*inY*np.tan(inCamVer_FOV/2)/inCamHeight)
        az = np.arctan(2*inX*np.tan(inCamHor_FOV/2)/inCamWidth)
        
    return (ok, az, el)

def BodyPolar2PixelXY(inAz, inEl, inCamHor_FOV, inCamVer_FOV, inCamWidth, inCamHeight):
    ok = False
    pixelX = 0
    pixelY = 0
    inEl = -inEl

    if ( inAz <= (inCamHor_FOV / 2)  and (inAz >= (-inCamHor_FOV / 2))  and inEl <= (inCamVer_FOV/2) and inEl >= (-inCamVer_FOV/2)):
        ok = True
        pixelY = np.tan(inEl)/(2*np.tan(inCamVer_FOV/2)/inCamHeight)
        pixelX = np.tan(inAz)/(2*np.tan(inCamHor_FOV/2)/inCamWidth)


    return (ok, pixelX, pixelY)


# Calculates Rotation Matrix given euler angles.
def eulerAnglesToRotationMatrix(theta) :  
    R_iv1 = np.array([[math.cos(theta[2]),    math.sin(theta[2]),    0],
                    [-math.sin(theta[2]),    math.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])

    R_v1v2 = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                    ])

    R_v2b = np.array([[1,         0,                  0                   ],
                    [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                    [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                    ])
    Rib = np.dot(R_v2b, np.dot( R_v1v2, R_iv1 ))

    return Rib

def RotationMatrixToEulerAngles(theta) :   
    Rbi = eulerAnglesToRotationMatrix(theta).transpose()
    return Rbi

def BodyPolar2GlobalPolar(inPixelAz, inPixelEl, inRoll, inPitch, inYaw):
    ### convert position in body polar coordinates to polar coordinates in global frame
    r_bi = RotationMatrixToEulerAngles([inRoll, inPitch, inYaw])
    x = np.cos(inPixelEl)*np.cos(inPixelAz)
    y = np.cos(inPixelEl)*np.sin(inPixelAz)
    z = np.sin(inPixelEl)

    xyz = np.array([x, y, z])

    calc_xyz = np.dot(r_bi, xyz)

    el = np.arcsin(calc_xyz[2])
    az = np.arctan(calc_xyz[1]/calc_xyz[0])

    return az,el

def GlobalPolar2BodyPolar(inTargetAz, inTargetEl, inRoll, inPitch, inYaw):
    ### convert position in global polar coordinates to polar coordinates in body frame
    r_ib = eulerAnglesToRotationMatrix([inRoll, inPitch, inYaw])
    x = np.cos(inTargetEl)*np.cos(inTargetAz)
    y = np.cos(inTargetEl)*np.sin(inTargetAz)
    z = np.sin(inTargetEl)
    
    xyz = np.array([x, y, z])
    
    calc_xyz = np.dot(r_ib, xyz)
    
    el = np.arcsin(calc_xyz[2])
    az = np.arctan(calc_xyz[1]/calc_xyz[0])

    return az,el

    




