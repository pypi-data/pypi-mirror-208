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


import random as _rnd
import opensrane as _opr

class _GlobalParameters():
    
    '''
    IMPORTANT ATTENTION:: it is really important to remember that
    Before using this Object, self.UnitObject should be assigned and shouldn't be empty
    '''
    
    
    
    def __init__(self,MatTags,OutFlowModelTags):
        
        # Connection of the materials and outflow model and for any material with outflow event that its tag is available in 
        # OutFlowModelTags, this Model will be used for both Gas dispersion and liquid spread
        self.MatTags=MatTags                       # List of materials That this model is applicable for them
        self.OutFlowModelTags=OutFlowModelTags     # List of outflow models that this model is valid for them
        
        self.wipeAnalysis()
                
    def wipeAnalysisGlobal(self):    
        #Results of Dispersion or spread Object Should Be Liquid or Gas state 
        #Attention: Below lists should be valued if you have liquid spread and you shouldn't left them empty 
        self.t_disp=None                       # Time list of Dispersion
        self.LiquidRadious=None                # Radius list of dispered Liquid in each moment
        self.LiquidCenter=None                 # Center list of dispered Liquid in each moment   
        self.LiquidThickness=None              # Thickness list of spilled liquids
        self.t_dispLiquidVaporization=None     # Time of Liquid Vaporization
        self.LiquidVaporizationMassRate=None   # Rate of Vaporization of the liquid
        self.LiquidVaporizationMass=None       # Total mass of Vaporization of the liquid
        
        self.GasExplosiveMass=None             # Gas mass list that is in the range of explosion (between LFL and UFL) for each instant of the time list
        self.GasExplosiveCenterX=None          # list of x of A Point that specify the location of the explosive mass
        self.GasExplosiveCenterY=None          # list of y of A Point that specify the location of the explosive mass
        self.GasExplosiveCenterZ=None          # list of z of A Point that specify the location of the explosive mass
        
        
        #This property (UnitObject) Should Be assigned to the created Dispersion Objects Before Any calculations
        self.UnitObject=None
        
        #Sampled wind direction
        self.WindDirection=None
    
    def wipeAnalysis(self):
        self.wipeAnalysisGlobal()
        pass    
        
      
     
    def Calculate(self):
        
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'


        # Parameters that should be determine by the calculations (Obviously not all of them and some of them are can be ignored for example Gas parameters are not needed for the liquid dispersion model)
        
        self.t_disp=None                       
        self.LiquidRadious=None                
        self.LiquidCenter=None                 
        self.LiquidThickness=None              
        self.t_dispLiquidVaporization=None     
        self.LiquidVaporizationMassRate=None   
        self.LiquidVaporizationMass=None       
        
        self.GasExplosiveMass=None             
        self.GasExplosiveCenter=None       

        
        return
    
    
    def GasConcentration(self,x,y,z):
        '''
        This function returns the value of concentration at point x,y,z 
        '''

        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
            
    
        return None
        
    def GiveBoundary(self,C):
        #This Function Should returns the boundary space that have concentration equal to C
        #Obviously for any different model the outpout can be differ
        pass
        
    def GiveBoundary(self,CC0Ratio):
        #This Function Should returns the boundary space that have concentration equal to C/C0 Ratio (C0 is initial Concentration)
        #In the Britter Model A rectangular plate has constant Concentration
        pass
        
        
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
        
        if WindDir=='Calm Condition': #To Avoid Program Stopping Modeling
            self.WindDirection=_rnd.uniform(0,360)
            WindDir=self.WindDirection
        

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