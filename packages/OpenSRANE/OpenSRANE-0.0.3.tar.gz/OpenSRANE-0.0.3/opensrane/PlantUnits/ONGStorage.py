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


from opensrane.Misc._NewClass import _NewClass
from .ObjManager import *
from ._GlobalParameters import _GlobalParameters
import math as _math

class ONGStorage(_NewClass,_GlobalParameters):
    '''
    On Ground Storage Tank
    '''
    Title="On Gound Storage Tank"
    
    def __init__(self,tag,SiteTag=None,DikeTag=None, SafetyTag=None, SubstanceTag=None, FragilityTagNumbers=None,
                      Horizontal_localPosition=0,Vertical_localPosition=0, Surface_Roughness=None,
                      Pressure=0,Temperature=0, SubstanceVolumeRatio=None,
                      Diameter=None,Height=None,GroundTemperature=None,Ks_Soil_Thermal_conductivity=None,Alphas_Soil_thermal_diffusivity=None,
                      boundary_points_Number=20,boundary_points_height_levels=10,
                      pressure_probit_tag=None, radiation_probit_tag=None, RadiationDifferenceDose=1000):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _GlobalParameters.__init__(self,SiteTag,GroundTemperature,Ks_Soil_Thermal_conductivity,Alphas_Soil_thermal_diffusivity, pressure_probit_tag,
                                        radiation_probit_tag,Horizontal_localPosition,Vertical_localPosition,Pressure,Temperature,
                                        FragilityTagNumbers,SubstanceTag,SafetyTag,Surface_Roughness,RadiationDifferenceDose)
        
        
        self.DikeTag=DikeTag
        #Check For error Message if Containment tag Number is not defined before---
        #------------------------------------------------------------------------
        
        
        
        self.d_Storage=Diameter
        self.h_Storage=Height
        

        
        if self.d_Storage==None or self.h_Storage==None:
            pass
        else:
            self.V_unit=_math.pi*self.d_Storage**2/4*self.h_Storage #The Total Object(Tank) Volume
            
        if SubstanceVolumeRatio==None or self.V_unit==None:
            pass
        else:
            if SubstanceVolumeRatio<0:SubstanceVolumeRatio=0
            if SubstanceVolumeRatio>1:SubstanceVolumeRatio=1
            self.V_subs=self.V_unit*SubstanceVolumeRatio     #The Total Object(Tank) Containment Volume

        
        self.name=f'(ONGStorage) On Gound Storage Tank with tag {tag} with dimeter ={Diameter} and height={Height} and substance tag {SubstanceTag}'
        
        self.boundary_points_Number=boundary_points_Number   #Number of boundary points 
        self.boundary_points_height_levels=boundary_points_height_levels # number of levels that will be consider for boundary points


        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
        
    @property
    def boundary_points(self):
        N=self.boundary_points_Number
        Nh=self.boundary_points_height_levels
        h=self.h_Storage
        x0=self.Hlocalcoord
        y0=self.Vlocalcoord
        if self.d_Storage==None: return None
        R=self.d_Storage/2
        
        Phi=[i/N*2*_math.pi for i in range(N)]
        H=[i*h/Nh for i in range(Nh+1)]
        result=[]
        for h in H:
            result.extend([(x0+R*_math.cos(phi),y0+R*_math.sin(phi),h) for phi in Phi])
        
        return result
        
        
        
    #This Function is needed for ZeroLevel Analysis so Any new     
    def _isSimilar(self,Obj):
    
        '''
        This Function Sould be Availble in all PlantUnit Classes
        and it shows if Other PlantUnit Object is similar to This Object
        And the Rule of similarity are as below code.
        This similarity is used in Zerolevel Analysis to Distinguish 
        Similar Objects.
        Attention, The input Should be an PlantUnit Object
        '''
        
        if self.__class__!=Obj.__class__:
            return False
        if self.d_Storage!=Obj.d_Storage:
            return False
        if self.h_Storage!=Obj.h_Storage:
            return False
        
        return True