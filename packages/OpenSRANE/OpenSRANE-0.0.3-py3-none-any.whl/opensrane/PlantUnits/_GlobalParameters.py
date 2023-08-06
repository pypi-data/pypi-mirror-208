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

class _GlobalParameters():
    '''
    In this Global Parameters that any plant unit should have and the other 
    Classes and functyions and ... use them
    '''
    
    def __init__(self,SiteTag,GroundTemperature=None,Ks_Soil_Thermal_conductivity=None,Alphas_Soil_thermal_diffusivity=None,
                      pressure_probit_tag=None, radiation_probit_tag=None,Horizontal_localPosition=None,Vertical_localPosition=None,
                      Pressure=None, Temperature=None,FragilityTagNumbers=None,SubstanceTag=None,SafetyTag=None,Surface_Roughness=None,
                      RadiationDifferenceDose=None,):
        
        
        
        #The Site tag that the PlantUnit is located in it
        self.SiteTag=SiteTag 
        if SiteTag==None:
            if _opr.Sites.ObjManager.Taglst==[]:
                raise IndexError('Still site object has not been defined and also no site tag is assigned to some Plant Units')
            else:
                self.SiteTag=_opr.Sites.ObjManager.Taglst[0]  #it is important that any objects has its sitetag and 
                

        
        self.V_unit=None  #Unit Object Total Capacity Volume
        self.V_subs=None  #Volume of Substance in the Unit Object
        
        self.Pressure=Pressure   #Unit Process Pressure
        self.Temperature=Temperature #Unit Process Temperature
        
        self.Hlocalcoord=Horizontal_localPosition #Unit Horizontal Local center Coordinate
        self.Vlocalcoord=Vertical_localPosition   #Unit Vertical Local center Coordinate
        
        self.FragilityTagNumbers=FragilityTagNumbers
        #Check For error Message if Fragility tag Number is not defined before---
        #------------------------------------------------------------------------
        
        self.SubstanceTag=SubstanceTag
        #Check For error Message if Containment tag Number is not defined before---
        #------------------------------------------------------------------------         
        self.SafetyTag=SafetyTag


        
        self.Surface_Roughness=Surface_Roughness             #Boundary Envirounment Surface Roughness
        
        if Ks_Soil_Thermal_conductivity==None:  #For Spreaded Liquid Vaporization
            self.Ks_Soil_Thermal_conductivity=0.9  
        else:
            self.Ks_Soil_Thermal_conductivity=Ks_Soil_Thermal_conductivity
            
        if Alphas_Soil_thermal_diffusivity==None:      #For Spreaded Liquid Vaporization 
            self.Alphas_Soil_thermal_diffusivity=4.3*10**(-7)
        else:
            self.Alphas_Soil_thermal_diffusivity=Alphas_Soil_thermal_diffusivity
        
        if GroundTemperature==None:   #Uses for Spreaded liquids evaporation
            self.GroundTemperature=_opr.Sites.ObjManager[self.SiteTag].Temperature
        else:
            self.GroundTemperature=GroundTemperature

        #Probit Functions tag
        self.pressure_probit_tag=pressure_probit_tag
        self.radiation_probit_tag=radiation_probit_tag
        
        
        #Safety Tags
        self.DikeTag=None
        
        #Differnce Radiation Dose to Recheck the Radiation vulnerability
        self.RadiationDifferenceDose=RadiationDifferenceDose
        

        self.wipeAnalysis()
                
    def wipeAnalysisGlobal(self): 
    
        self.isdamaged=False
        self.DamageSource=None
        self.DamageSourceTag=None
        self.DamageSourceDose=None
        self.DamageSourceType=None
        self.DamageFragilityTag=None
        self.DamageLevel=None
        
        #OutFlowModel Object, name and tags
        self.OutFlowModelTag=None
        self.OutFlowModelname=None
        self.OutFlowModelObject=None

        
        #Spread dispersion Object, name and tags
        self.DispersionSpreadModelTag=None
        self.DispersionSpreadModelname=None
        self.DispersionSpreadModelObject=None      

        
        #Physical Effect Object, name and tag
        self.PhysicalEffectModelTag=None
        self.PhysicalEffectModelname=None
        self.PhysicalEffectObject=None
        
        #Store the maximum radiation dose in the last analyzed level
        self.LastRadiationDose=None
        
        
    def wipeAnalysis(self):
        self.wipeAnalysisGlobal()
        pass    
        
        
    @property
    def boundary_points(self):       #List of baoundary Points of the element that are used for calculating OpverPressure and Radiation effects
        return None
        
    #This Function is needed for ZeroLevel Analysis that shows that is current object similar to the input object ('obj' argument in the below) or not
    def _isSimilar(self,Obj):
        return False
 
    