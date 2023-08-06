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
from copy import deepcopy as _deepcopy
from ._GlobalParameters import _GlobalParameters

class Material(_NewClass, _GlobalParameters):
    
    
    def __init__(self,tag,name='No name', Density=None, GasDensity=None, BoilingPointGasDensity=None, 
                 Dynamic_Viscousity=None,Molar_Heat_of_Combustion=None,Stoichiometric_Concentration=None,
                 Vapour_Density=None,Volumetric_Heat_Capacity=None,Molecular_Weight=None,Molar_Volume=None,
                 Boiling_Point=None,Critical_Pressure=None,Critical_Temperature=None,Melting_Point=None,Standard_Enthalpy_of_Formation=None, Vapour_Pressure=None,Molar_Enthalpy_of_Vaporization=None,Specific_Heat_of_Vaporization=None,Molar_Heat_Capacity=None, Specific_Heat_Capacity=None,Specific_Heat_Ratio=None,Autoignition_Temperature=None,Flash_Point=None,Specific_Heat_of_Combustion=None, Lower_Flammability_Limit=None,Upper_Flammability_Limit=None, Bioconcentration_Factor=None,Liquid_Partial_Pressure_in_Atmosphere=None, ):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------

        _GlobalParameters.__init__(self)

        
        #PhysioChemical Properties
        self.name=name                                                      #Subtance name    
        self.Dynamic_Viscousity=Dynamic_Viscousity                          # 
        self.Molar_Heat_of_Combustion=Molar_Heat_of_Combustion              #Valid [x]>0 
        self.Stoichiometric_Concentration=Stoichiometric_Concentration      #Valid [x]>0
        self.Vapour_Density=Vapour_Density                                  #Valid [x]>0 
        self.Volumetric_Heat_Capacity=Volumetric_Heat_Capacity
        self.Molecular_Weight=Molecular_Weight                              #Valid [x]>0 
        self.Molar_Volume=Molar_Volume                                      #Valid [x]>0 
        self.Density=Density                                                #Valid [x]>0 
        self.GasDensity=GasDensity                                          #Valid [x]>0
        self.BoilingPointGasDensity=BoilingPointGasDensity
        self.Boiling_Point=Boiling_Point                               
        self.Critical_Pressure=Critical_Pressure                       
        self.Critical_Temperature=Critical_Temperature                 
        self.Melting_Point=Melting_Point                                    #Valid [x]>-273.15 oC
        self.Standard_Enthalpy_of_Formation=Standard_Enthalpy_of_Formation
        self.Vapour_Pressure=Vapour_Pressure                                #Valid [x]>0
        self.Molar_Enthalpy_of_Vaporization=Molar_Enthalpy_of_Vaporization
        self.Specific_Heat_of_Vaporization=Specific_Heat_of_Vaporization    #Valid[x]>0
        self.Molar_Heat_Capacity=Molar_Heat_Capacity
        self.Specific_Heat_Capacity=Specific_Heat_Capacity                  #Valid[x]>0
        self.Specific_Heat_Ratio=Specific_Heat_Ratio                        #Valid[x]>0 [Hydrogen:1.405]
        self.Autoignition_Temperature=Autoignition_Temperature
        self.Flash_Point=Flash_Point
        self.Specific_Heat_of_Combustion=Specific_Heat_of_Combustion        #Valid[x]>0
        self.Lower_Flammability_Limit=Lower_Flammability_Limit              #Valid [x] > 0 kg/m3
        self.Upper_Flammability_Limit=Upper_Flammability_Limit              #Valid [x] > 0 kg/m3
        self.Bioconcentration_Factor=Bioconcentration_Factor
        self.Liquid_Partial_Pressure_in_Atmosphere=Liquid_Partial_Pressure_in_Atmosphere  #Partial Pressure when substance is in atmosphere

        
        
        
        #Material State Formula
        # if isLiquidBooleanFunction==None or isLiquidBooleanFunction==True:  #If Function Doesn't Enter or Enter True its state cosidered as Liquid      
            # self.isLiquid=lambda P,T,SubstanceObject:True
        # elif isLiquidBooleanFunction==False:                                #If Function Enter False its state cosidered as Gas
            # self.isLiquid=lambda P,T,SubstanceObject:False
        # else:                                                               #Else According The Function that User Enter    
            # self.isLiquid=_deepcopy(isLiquidBooleanFunction)                #An important Function That Should Take Pressure and Temperature and Returns a Boolean Shows State is liquid or not(Means Gas)
            
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass        
        
        

