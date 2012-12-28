import rhinoscriptsyntax as rs
import math
from random import choice


def getArea():
    return rs.GetObject("Select area", filter=4)

def createTheater(area):
    option = rs.GetInteger("Enter '1' for square, enter '2' for custom", 2)
    if option == 1:
        sqSides = math.sqrt(area)
        rec = rs.AddRectangle(rs.WorldXYPlane(), sqSides, sqSides)
    else:
        userSide = rs.GetInteger("Enter x-axis length", 300)
        ySide = area / userSide
        rec = rs.AddRectangle(rs.WorldXYPlane(), userSide, ySide)
    return rec
    
def arrayFuselages(rec):
    fuseList = []
    
    f37 = rs.GetObjects("Select 737", 0, True, True, True)
    
    b37 = rs.BoundingBox(f37)
    bRec = rs.BoundingBox(rec)
    
    len37 = rs.Distance(b37[0], b37[3])
    lenRec = rs.Distance(bRec[0], bRec[3])
    copies = int(math.ceil(lenRec / len37))
    firstCopy = rs.CopyObject(f37, (bRec[0]-b37[0]))
    fuseList.append(firstCopy)
    
    for i in range(copies-1):
        fuseList.append(rs.CopyObject(firstCopy, (b37[3]-b37[0])*(i+1)))
    
    return fuseList
    
def distortArray(fuseList, rec):
    bFuse = rs.BoundingBox(fuseList[0])
    lenFuse = bFuse[1][0] - bFuse[0][0]
    
    bRec = rs.BoundingBox(rec)
    lenRec = bRec[1][0] - bRec[0][0]
    
    xRange = lenRec - lenFuse
    step = xRange/ (len(fuseList))
    
    distortion = rs.frange(0, xRange, step)
   
    for i in range(0, len(fuseList)):
        x = choice(distortion)
        distortion.remove(x)
        
        xform = [x,0,0]
        rs.MoveObject(fuseList[i], xform)
        
    return fuseList 
    
def fillSite(fuseList, rec):
    leftEnd = []
    rightEnd = []
    
    for i in range(len(fuseList)):
        leftEnd = distCheckLeft(fuseList[i], rec, leftEnd)
        rightEnd = distCheckRight(fuseList[i], rec, rightEnd)

    return leftEnd, rightEnd       
        
def distCheckLeft(fuse, rec, leftEnd):
    
    bFuse = rs.BoundingBox(fuse)
    bRec = rs.BoundingBox(rec)
    
    lenFuse = bFuse[1][0] - bFuse[0][0]
    
    dist = bFuse[0][0] - bRec[0][0]
    if dist > lenFuse:
        xform = [-(lenFuse), 0, 0]
        fuse = rs.CopyObject(fuse, xform)
        distCheckLeft(fuse, rec, leftEnd)
    elif dist == 0:
        return leftEnd
    else:
        xform = [-(lenFuse), 0, 0]
        leftEnd.append(rs.CopyObject(fuse, xform))

    return leftEnd
        
def distCheckRight(fuse, rec, rightEnd):
    bFuse = rs.BoundingBox(fuse)
    bRec = rs.BoundingBox(rec)
    
    lenFuse = bFuse[1][0] - bFuse[0][0]
    
    dist = bRec[1][0] - bFuse[1][0]
    if dist > lenFuse:
        xform = [(lenFuse), 0, 0]
        fuse = rs.CopyObject(fuse, xform)
        distCheckRight(fuse, rec, rightEnd)
    elif dist == 0:
        return rightEnd
    else:
        xform = [lenFuse, 0, 0]
        rightEnd.append(rs.CopyObject(fuse, xform))
        
    return rightEnd
    
def endMove(ends, rec):
    lEnd = ends[0]
    rEnd = ends[1]
    move = 100
    roLeft = []
    roRight = []
    
    bRec = rs.BoundingBox(rec)
    
    for i in range(len(lEnd)):
        rs.MoveObject(lEnd[i], [move,0,0])
        bFuse = rs.BoundingBox(lEnd[i])
        
        outTest = bRec[0][0] - bFuse[0][0]
        
        if outTest > 0:
            roLeft.append(lEnd[i])
            
    for i in range(len(rEnd)):
        rs.MoveObject(rEnd[i], [-move,0,0])
        
        bFuse = rs.BoundingBox(rEnd[i])
        
        outTest = bRec[1][0] - bFuse[1][0]
        
        if outTest < 0:
            roRight.append(rEnd[i])
    
    return roLeft, roRight
    
def rotateEnds(roEnds, rec):
    rLeft = roEnds[0]
    rRight = roEnds[1]
    bRec = rs.BoundingBox(rec)
    
    for i in range(len(rLeft)):
        bBox = rs.BoundingBox(rLeft[i])
        
        bBox[1][0] -= 22.5
        bBox[2][0] -= 22.5
        
        line = rs.AddLine(bBox[1], bBox[2])
        cPt = rs.CurveMidPoint(line)
        
        dist = bBox[1][0] - bRec[0][0]
        
        angle = math.degrees(math.acos(dist / 200))
        rs.RotateObject(rLeft[i], cPt, -angle, [0,1,0])
        
    for i in range(len(rRight)):
        bBox = rs.BoundingBox(rRight[i])
        
        bBox[3][0] += 22.5
        bBox[0][0] += 22.5
        
        line = rs.AddLine(bBox[0], bBox[3])
        cPt = rs.CurveMidPoint(line)
        
        dist = bBox[0][0] - bRec[1][0]
        
        angle = math.degrees(math.acos(dist / 200))
        rs.RotateObject(rRight[i], cPt, 180-angle, [0,1,0])
    
if __name__ == '__main__':
    #area = rs.GetInteger("Enter area", 20000)
    rec = getArea()
    #rec = createTheater(area)
    fuseList = arrayFuselages(rec)
    fuseList = distortArray(fuseList, rec)
    ends = fillSite(fuseList, rec)
    roEnds = endMove(ends, rec)
    rotateEnds(roEnds, rec)