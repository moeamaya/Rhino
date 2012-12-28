import rhinoscriptsyntax as rs

class FaceMe():
    
    def getPeople(self):
        """
        The purpose of this function
        is to select all the surface
        objects 'people' and return them
        Parameter: none
        Return: surface list
        by Moe
        2011_10_15
        """
        people = rs.GetObjects("Select the objects you want to face the camera", 8, 0, True )
        return people
        
    def establishRotationPoints(self,people):
        """
        The purpose of this function
        is to select first surface in the
        list and draw its base point
        and also camera base point
        the current view.
        Parameter: surface list
        Return: list of points
        by Moe
        2011_10_16
        """
        viewPt = rs.ViewCamera()
        viewZero = [viewPt[0],viewPt[1],0]
        
        boundingBoxPt = rs.BoundingBox(people[0])
        
        startPt = boundingBoxPt[0]
        endPt = boundingBoxPt[2]
        
        x1 = startPt[0]
        y1 = startPt[1]
        x2 = endPt[0]
        y2 = endPt[1]
        
        dx = (x2+x1)/2
        dy = (y2+y1)/2
        
        turnPt = rs.AddPoint([dx,dy,0])
        
        pts = [startPt, endPt, turnPt, viewZero]
        return pts
        
    def generateAngleRotation(self,pts):
        """
        The purpose of this function
        is to find the angle between
        camera and the surface normal
        through basic trig function
        Parameter: list of points
        Return: return angle
        by Moe
        2011_10_17
        """
        startPt = pts[0]
        endPt = pts[1]
        turnPt = pts[2]
        viewZero = pts[3]
        
        x1 = startPt[0]
        y1 = startPt[1]
        x2 = endPt[0]
        y2 = endPt[1]
        
        dx = (x2+x1)/2
        dy = (y2+y1)/2
        
        #move pts to origin
        tX1 = x1-dx
        tY1 = y1-dy
        
        tX2 = x2-dx
        tY2 = y2-dy
        
        #rotate 90 (trigonometry)
        xPrime1 = -tY1
        yPrime1 = tX1
        
        xPrime2 = -tY2
        yPrime2 = tX2
        
        #move final pt back to original location
        ptFinalX = xPrime1 + dx
        ptFinalY = yPrime1 + dy
        
        measurePt = [ptFinalX, ptFinalY, 0]
        rs.AddPoint(measurePt)
        
        line1 = [turnPt,measurePt]
        line2 = [turnPt,viewZero]
        
        angle = rs.Angle2(line1,line2)
        
        return angle
        
    def generateEachRotationPoint(self,people):        
        """
        The purpose of this function
        is to generate a base point for
        the list of surface people
        Parameter: surface list
        Return: base point list
        by Moe
        2011_10_18
        """
        
        cPt = []
        for i in range(len(people)):
            tempList = rs.SurfaceAreaCentroid(people[i])
            temp = tempList[0]
            cPt.append(temp)
        
        base = []
        for i in range(len(people)):
            pt = cPt[i]
            x = pt[0]
            y = pt[1]
            z = 0
            temp = [x,y,z]
            base.append(temp)
            
        return base           
    
    def rotatePeople(self,people,base,angle):
        """
        The purpose of this function
        is to rotate the surface people by
        the measured angle
        Parameter: people, base, angle
        Return: none
        by Moe
        2011_10_19
        """
        for i in range(len(people)):
            rs.RotateObject(people[i], base[i], angle[0])
    
    def correctOrientation(self, people, base, angle):
        """
        The purpose of this function
        is to rotate people in the opposite
        direction of the original rotation if
        the orginal is incorrect
        Parameter: people, base, angle
        Return: none
        by Moe
        2011_10_20
        """
        items = ("Answer", "Yes", "No"), ("Change", "Disabled", "Enabled")
        results = rs.GetBoolean("Is orientation correct?", items, (True, True) )
        if results[0] is True:
            
            #rotate opposite direction
            angle = -(2*angle[0])
            for i in range(len(people)):
                rs.RotateObject(people[i], base[i], angle)
        else:
            return None

    def main(self):
        people = self.getPeople()
        
        pts = self.establishRotationPoints(people)
        
        angle = self.generateAngleRotation(pts)
        
        base = self.generateEachRotationPoint(people)
        
        self.rotatePeople(people,base,angle)
        self.correctOrientation(people,base,angle)


fm = FaceMe()
fm.main()