# /* ****************************************************************** **
# **    OpeSRANE - Open Software for Risk Assessment of Natech Events   **
# **                                                                    **
# **                                                                    **
# **                                                                    **
# ** (C) Copyright 2023, Mentioned Regents in 'COPYRIGHT' file.         **
# **                                                                    **
# ** All Rights Reserved.                                               **
# **                                                                    **
# ** Commercial use of this program without express permission of the   **
# ** owner (The Regents), is                                            **
# ** strictly prohibited.  See file 'COPYRIGHT'  in main directory      **
# ** for information on usage and redistribution,  and for a            **
# ** DISCLAIMER OF ALL WARRANTIES.                                      **
# **                                                                    **
# ** Developed by:                                                      **
# **   Bijan SayyafZadeh (OpenSRANE@Gmail.com)                          **
# **   MehDi Sharifi                                                    **
# **   Abdolreza S. Moghadam                                            **
# **   Eslam Kashi                                                      **
# **                                                                    **
# ** ****************************************************************** */

'''
 Written: Bijan Sayyafzadeh
 Created: 2022
 
 Revision: -
 By & Date: -
'''


import opensrane as _opr
import random as _rnd

class _GlobalParameters():
    
    
    
    def __init__(self):


        
        self.wipeAnalysis()
                
    def wipeAnalysisGlobal(self):  
    
        #Results of OutFlow Object Should Be Liquid or Gas 
        self.t_release=None  #Time list of outFlow or release
        self.UnitObject=None
        
        #For Conver and ConvertBack Direction (Not Sure for any further usage)
        self.WindDirection=None

    def wipeAnalysis(self):
        self.wipeAnalysisGlobal()
        pass         

     
    def Calculate(self):
        
        UnitObject=self.UnitObject #self.UnitObject is defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        return 
        
    def Thermal_Radiation_at_Point(self,x,y,z):
        #This function returns Thermal Radiation Value at point x,y,z
        return None
        
    def RadiationBoundary(self,Radiation,Height,PointNumber):
        #This function returns N PointNumber location that have equal radiation value (Radiation) at z=Height
        return None
        
    def OverPressure_at_Point(self,x,y,z):
    
        #This function returns OverPressure value at point x,y,z
        return None

    def OverPressureBoundary(self,OverPressure, Height, PointNumber):
    
        #This function returns N PointNumber location that have equal OverPressure value at z=Height
        
        return None
    
    def Toxic_at_Point(self,x,y,z):
        #This function returns Toxic Dose Value at point x,y,z
        return None
        
        
    def _convertdirection(self,DeltaX,DeltaY):
        '''
        This function returns the location of the point respect to the wind direction
        North = 0
        West  = 270
        and ...
        
        DeltaX=LocationX-referenceX (or center X)
        DeltaY=LocationY-referenceY (or center Y)
        
        For example if the center of the gas dispersion is x= 10 and the location of the target point is x=15
        then Deltax=15-10
        
        
        When the wind in 0 it means that it is blasting from the north and it is from North to south
        So Wind Direction is : Direction+180 respec to the north and anticloclwise 
        
        '''
        import math as math
        WindDir=_opr.WindData.ObjManager.Objlst[0]
        WindDir=WindDir.WindDirection
        if WindDir==None:
            print('Wind Sampling Has not been done and so ')
            return None
        
        # if WindDir=='Calm Condition': #To Avoid Program Stopping Modeling
            # self.WindDirection=_rnd.uniform(0,360)
            # WindDir=self.WindDirection
        

        Direction=WindDir+180+90 #Direction respect to the right axis and anticlockwise #180 is because of wind direction is apposite of its angle and 90 is becuse it is considered that zero angle is in the right side not to the north
        Directionx=Direction*math.pi/180 #convert to Radian
        Directiony=Directionx+math.pi/2
        
        #Unit vector of the wind Direction
        DirVecx=[math.cos(Directionx),math.sin(Directionx)]
        DirVecy=[math.cos(Directiony),math.sin(Directiony)]
        
        #Vector of the Location
        Vec=[DeltaX,DeltaY]
        
        #cross Product of vectors to get the length of the vector along the wind direction
        X=DirVecx[0]*Vec[0]+DirVecx[1]*Vec[1]
        Y=DirVecy[0]*Vec[0]+DirVecy[1]*Vec[1]
        
        return [X,Y]
        
    def _convertBackdirection(self,X,Y):
        '''
        This function returns back to the global the location of the point respect to the wind direction
        North = 0
        West  = 270
        and ...
        
        X,Y are the coordinate resulted from _convertdirection(DeltaX,DeltaY) Function:
        X= Horizontal Location of the point respect to the center (0,0) and the along the wind Direction
        Y= Vertical Location of the point respect to the center (0,0) and the along the wind Direction
        
        
        For example if the center of the gas dispersion is (10,15) and the location of the target point is X=5 and Y=0 and wind direction is from south to north
        then x=10 and y=15+5=20
        
        '''

        import math as math
        WindDir=_opr.WindData.ObjManager.Objlst[0]
        WindDir=WindDir.WindDirection
        if WindDir==None:
            print('Wind Sampling Has not been done and so ')
            
        if WindDir=='Calm Condition':
            WindDir=self.WindDirection
            

        Direction=WindDir+180+90 #Direction respect to the right axis and anticlockwise
        Directionx=-1*Direction*math.pi/180 #convert to Radian #-1 is to rotate it back
        Directiony=Directionx+math.pi/2
        
        
        #Unit vector of the wind Direction
        DirVecx=[math.cos(Directionx),math.sin(Directionx)]
        DirVecy=[math.cos(Directiony),math.sin(Directiony)]
        
        #Vector of the Location
        Vec=[X,Y]
        
        #cross Product of vectors to get the length of the vector along the wind direction
        X=DirVecx[0]*Vec[0]+DirVecx[1]*Vec[1]
        Y=DirVecy[0]*Vec[0]+DirVecy[1]*Vec[1]
        
        return [X,Y]        