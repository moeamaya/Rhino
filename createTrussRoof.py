import rhinoscriptsyntax as rs
import math
from random import choice

class BaseCurve():
    def __init__(self):
        self.crv = None
        self.listCrvs = None
        
        rs.AddLayer("panels")
        
        self.getTwoCurves()
        self.outputLongerCurve()
        self.useNextClass()
        
    def useNextClass(self):
        dc = Division(self.crv, self.listCrvs)       
        
    def getTwoCurves(self):
        self.listCrvs = rs.GetObjects("Select two spanning curves", 4, False, True)
        
        if len(self.listCrvs) != 2:
            return None
        else:
            return self.listCrvs
        
    def outputLongerCurve(self):
        crv1 = self.listCrvs[0]
        crv2 = self.listCrvs[1]
        
        length1 = rs.CurveLength(crv1)
        length2 = rs.CurveLength(crv2)
        
        if length1 > length2:
            self.crv = crv1
        else:
            self.crv = crv2
    
class Division():
    def __init__(self, crv, list):
        self.crv = crv
        self.listCrvs = list
        self.n = None
        
        self.testLength()
        self.useNextClass()
        
    def useNextClass(self):
        tb = TrussBase(self.n, self.listCrvs)
        
    def testLength(self):
        pt1 = rs.CurveStartPoint(self.crv)
        pt2 = rs.CurveEndPoint(self.crv)
        
        test = rs.Distance(pt1,pt2)
        
        if test > 30:
            n = 1                
            self.recursion(n)
        else:
            self.n = 1
        
    def divideCurve(self, n):
        pts = rs.DivideCurve(self.crv, n, False, True)
        n = n+1
        #print n
        pt1 = pts[0]
        pt2 = pts[1]
        
        test = rs.Distance(pt1, pt2)
        
        return n, test
        
    def recursion(self, n):
        list = self.divideCurve(n)
        n = list[0]
        test = list[1]
        
        if test > 30:
            self.recursion(n)
        else:
            #pts = rs.DivideCurve(self.crv, n, True)
            self.n = n    
    
class TrussBase():
    def __init__(self, n, list):
        self.n = n
        self.listCrvs = list
        self.pts = None
        
        self.createPoints()
        self.useNextClass()
        
    def useNextClass(self):
        tf = TrussFlange(self.pts)
        
    def createPoints(self):
        crv1 = self.listCrvs[0]
        crv2 = self.listCrvs[1]
        pts1 = rs.DivideCurve(crv1, self.n, False, True)
        pts2 = rs.DivideCurve(crv2, self.n, False, True)
        
        self.pts = [pts1,pts2]
        
class TrussFlange():
    def __init__(self, pts):
        self.pts = pts
        self.top = []
        self.bottom = []
        self.extrCrv = []
        self.b3d = []
        self.i = range(len(self.pts[0]))

        
        self.makeTopCurves()
        self.makeExtrudeCurve()
        self.make3D()
        self.makeBottomFlange()
        self.useNextClass()
        
    def useNextClass(self):
        vm = VerticalMembers(self.top, self.bottom)
               
        
    def makeTopCurves(self):
        rs.EnableRedraw(False)
        for i in self.i:
            crv1 = self.pts[0]
            crv2 = self.pts[1]
            
            self.top.append( rs.AddCurve( [crv1[i], crv2[i]] ) )
            
    def makeExtrudeCurve(self):
        rs.EnableRedraw(False)
        W = 0.1         
        basePt = self.pts[0]
        for i in self.i:
             x = basePt[i][0]
             y = basePt[i][1]
             z = basePt[i][2]
             pt1 = [(x-W), y, (z-W) ]
             pt2 = [(x+W), y, (z-W) ]
             pt3 = [(x+W), y, (z+W) ]
             pt4 = [(x-W), y, (z+W) ]
             pts = [pt1,pt2,pt3,pt4,pt1]
             self.extrCrv.append( rs.AddPolyline(pts) )
             
    def make3D(self):
        rs.EnableRedraw(False)
        for i in self.i:
            self.b3d.append( rs.ExtrudeCurve(self.extrCrv[i], self.top[i]) )
            
    def makeBottomFlange(self):
        rs.EnableRedraw(False)
        for i in self.i:
            length = rs.CurveLength(self.top[i])
            move = [0,0,-(length/15)]
            
            self.bottom.append( rs.CopyObject(self.top[i],move) )
            rs.CopyObject( self.b3d[i], move) 
        
class VerticalMembers():
    def __init__(self, t, b):
        self.top = t
        self.bottom = b
        self.pts1 = []
        self.pts2 = []
        self.extrCurve = []
        self.i = range(len(self.top))
        self.j = []
        
        self.divideCurve()
        self.drawExtrudeCurve()
        self.makeMembers()
        self.useNextClass()
        
    def useNextClass(self):
        cb = CrossBracing(self.pts1,self.pts2,self.extrCurve)       
        
    def divideCurve(self):
        for i in self.i:
            self.pts1.append( rs.DivideCurve(self.top[i], 10, False) )
            self.pts2.append( rs.DivideCurve(self.bottom[i], 10, False) )         
        
    def drawExtrudeCurve(self):
        W = 0.035
        self.j = range(11)
        
        for i in self.i:
            for j in self.j:
                x = self.pts1[i][j][0]
                y = self.pts1[i][j][1]
                z = self.pts1[i][j][2]
                pt1 = [(x-W), (y-W), z]
                pt2 = [(x+W), (y-W), z]
                pt3 = [(x+W), (y+W), z]
                pt4 = [(x-W), (y+W), z]
                pts = [pt1, pt2, pt3, pt4, pt1]
                
                self.extrCurve.append( rs.AddPolyline(pts) )
            
        
    def makeMembers(self):
        rs.EnableRedraw(False)
        path = []
        for i in self.i:
            for j in self.j:
                pt1 = self.pts1[i][j]
                pt2 = self.pts2[i][j]
                path.append( rs.AddLine(pt1, pt2) )
        index = range(len(path))
        for i in index:
            rs.ExtrudeCurve( self.extrCurve[i], path[i] )
            
class CrossBracing():
    def __init__(self,t,b,c):
        self.pts1 = t
        self.pts2 = b
        
        self.i = range(len(self.pts1))
        self.j = range(len(self.pts1[0]))
        
        self.makeMembers()
        self.useNextClass()
        
    def useNextClass(self):
        cb = ConnectionBetween(self.pts1, self.pts2)       
        
    def makeMembers(self):
        mesh = rs.GetObject("Select mesh to test", rs.filter.mesh)
        half = math.floor( len(self.pts1[0])/2 )
        W = 0.2
        S = 10
        length = range(8,12)
    
        for i in self.i:
            for j in self.j:
                if j < half:
                    pt1 = self.pts1[i][j]
                    pt2 = self.pts2[i][j+1]
                    
                    temp = rs.AddLine(pt1,pt2)
                    X = choice(length)
                    Y = choice(length)
                    Z = choice(length)
                    path = rs.ScaleObject(temp, pt1, [X,Y,Z])
                    
                    #crv = rs.AddCircle(pt1, W)
                    #rs.ExtrudeCurve(crv, path)
                    
                    cmx = rs.CurveMeshIntersection(path, mesh)
                    if cmx:
                        crv = rs.AddCircle(pt1, W)
                        rs.ExtrudeCurve(crv, path)
                    else:
                        rs.DeleteObject(path)
                        
                    
                if j > half:
                    pt1 = self.pts1[i][j]
                    pt2 = self.pts2[i][j-1]
                    path = rs.AddLine(pt1,pt2)
                    crv = rs.AddCircle(pt1, W)
                    rs.ExtrudeCurve(crv, path)
        
class ConnectionBetween():
    def __init__(self, t, b):
        self.pts1 = t
        self.pts2 = b
        
        self.i = range(len(self.pts1)-1)
        self.j = range(len(self.pts1[0]))
        
        self.line1 = []
        self.line2 = []
        
        self.makeCurves()
        self.useNextClass()
        
    def useNextClass(self):
        rp = RoofPanels(self.pts1)
        
    def makeCurves(self):
        for i in self.i:
            for j in self.j:
                pt = self.pts1[i][j]
                pt2 = self.pts2[i][j]
                x = pt[0]
                y = pt[1]
                z = pt[2]
                xPt = [x, y-1,z]
                yPt = [x, y, z+1]
                plane = rs.PlaneFromFrame( pt, xPt, yPt )
                plane2 = rs.PlaneFromFrame( pt2, xPt, yPt )
                
                crv = rs.AddCircle(plane, 0.1)
                crv2 = rs.AddCircle(plane2, 0.1)
                
                
                line1 = rs.AddLine( self.pts1[i][j], self.pts1[i+1][j] )
                line2 = rs.AddLine( self.pts2[i][j], self.pts2[i+1][j] )
                
                rs.ExtrudeCurve(crv, line1)
                rs.ExtrudeCurve(crv2, line2)
                
class RoofPanels():
    def __init__(self, t):
        self.pts1 = t
        
        self.i = range(len(self.pts1)-1)
        self.j = range(0, len(self.pts1[0])-1, 2)

        self.makePanels()
        
    def makePanels(self):
        rs.EnableRedraw(False)
        index = choice(range(3))
        
        for i in self.i:
            for j in self.j:
                pt1 = self.pts1[i][j]
                pt2 = self.pts1[i][j+1]                           
                pt3 = self.pts1[i+1][j]
                pt4 = self.pts1[i+1][j+2]
                
                line = rs.AddLine(pt1,pt2)
                line2 = rs.AddLine(pt3,pt4)
                
                loft = [line,line2]
                panel = rs.AddLoftSrf(loft)
                
                rs.ObjectLayer(panel, "panels")
                
bc = BaseCurve()    