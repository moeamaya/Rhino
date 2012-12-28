import rhinoscriptsyntax as rs
import math
import random

def initialCrv():
    return rs.GetCurveObject("Get curve", True)[0]

class Point(object):
    def __init__(self, pt, index):
        self.x = pt[0]
        self.y = pt[1]
        self.z = pt[2]
        self.i = index
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
        
    def getZ(self):
        return self.z
        
    def getCoord(self):
        return [self.x, self.y, self.z]
        
    def setIndex(self, index):
        self.i = index
        
    def getNewPoint(self):
        oldx, oldy, oldz = self.getX(), self.getY(), self.getZ()
        delta_xy = random.choice([0, 1.0, 1.05, 1.1, 1.15]) ** self.i
        delta_z = random.choice([0,1,1,2]) #* self.i
        
        delta_xy = delta_xy * random.choice([-1,1])
        #check the angle
        if oldx != 0:
            newx = oldx + delta_xy
            newy = oldy + delta_xy
            newz = oldz + delta_z
        else:
            newx = oldx
            newy = oldy
            newz = oldz
        
        return Point([newx, newy, newz], self.i)
        
    def getCurvePlane(self):
        return rs.CurvePlane(self.crv)

def movePoints(crv):
    '''subdivides curve and moves points'''
    points = rs.DivideCurve(crv, 18, False, True)
    newPoints = []
    for i in range(len(points)):
        temp = Point(points[i], i)
        newPoints.append(temp.getNewPoint())
    
    return newPoints

def createPolyline(crv):
    '''creates scaled polyline from shifting points'''
    pts = movePoints(crv)
    polyPts = []
    for pt in pts:
        polyPts.append(pt.getCoord())
    polyline = rs.AddPolyline(polyPts)
    
    scale = random.choice([1, 1.2, 1.5, 2, 2.5, 3, 5, ])
    newPolyline = rs.ScaleObject(polyline, [0,0,0], [scale, 1, 1]) 
    return newPolyline


def main():
    #get curve
    crv = initialCrv()
    
    #generate polylines
    rs.EnableRedraw(False)
    for i in range(720):
        line = createPolyline(crv)
        rs.RotateObject(line, [0,0,0], 0.5 * i)

main()