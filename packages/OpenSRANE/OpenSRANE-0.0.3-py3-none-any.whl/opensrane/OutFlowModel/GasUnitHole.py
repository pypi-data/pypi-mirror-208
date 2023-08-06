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


#This is a Sample File and any new Model is better to be constructed by a copy of this file
from opensrane.Misc._NewClass import _NewClass
from .ObjManager import *
from opensrane.Misc.WarningRecorder import *
from ._GlobalParameters import _GlobalParameters
import math as _math
import opensrane as _opr

class GasUnitHole(_NewClass,_GlobalParameters):
    
    '''
    OutFlow Model From a hole in the body of a plant unit thas has filled of gas
    for a continues release and constant outflow rate 
    Casal Book part 2.3.1
    Cd=Discharge Coefficient - [1]
    
    
    '''
    # P0=Initial internal Pressure 
    # T0=Initial internal temperature 
    # Ah=Cross Section area hole m^2 [Sample:  ]
    # Cd=Discharge Coefficient - [0.62 for this case]
    # Gamma=Cp/Cv; Specific Heat Ratio of gas  [Hydrogen:1.405]
    # z=Compresibility Factor at P0 and T0 (For Ideal Gas = 1)
    # M= Molecular weight (kg/mol)
    # R=Gas Constant J/(mol.K) 8.314
    # qs= Mass flow rate (kg/s)

    

    Title='GasUnitHole'
    
    def __init__(self,tag,Hole_Diameter=0.01, Total_t=20, Cd=1, Gas_Constant=8.31446261815324):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.Hole_Diameter=Hole_Diameter
        self.Total_t=Total_t
        self.Cd=Cd                                   #The discharge coefficient
        self.Gas_Constant=Gas_Constant

        
        self.name=f'Gas From UnitHole with Diameter= {Hole_Diameter}, Total t= {Total_t} and Cd= {Cd} '


        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
        
    def Calculate(self):
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #Import required Data:
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag]
        SiteObject=_opr.Sites.ObjManager.Objlst[0]
         
        Pa=SiteObject.Pressure          #OutSide Pressure
        Ta=SiteObject.Temperature       #OutSide Temperature
        
        P0=UnitObject.Pressure          #Inside Pressure
        T0=UnitObject.Temperature       #Inside Temperature
        
        V_subs=UnitObject.V_subs        #Volume of Substance contained in the plant unit
        Density=SubstanceObject.Density #Density of the substance inside the plant unit
        
        #Check is data enough to calculate the total mass of the containment
        if V_subs==None or Density==None:
            warning(f'(GasUnitHole Model) Volume of substance in the Unit with tag={UnitObject.tag} or Density of the Substance with the tag={SubstanceObject.tag} was not defined By the User '+
                    f'So for the mentioned plant unit, the total outflow mass of the gas has not been checked and it is calculated according the total time defined by the user')
            TotalMass=None
        else: 
            TotalMass=V_subs*Density
            
        #Check if P0 and T0 were not defined by the user
        if P0==None or T0==None:
            warning(f'Pressure and Temperature for Unit with tag={UnitObject.tag} were not defined By the User '+
                  f'So the code do not calculate any Gas Outflow (GasUnitHole Model) for this Plant Unit')
            return -1 

        #Check if P0=0 or T0=0
        if  P0==0 or T0==0:
            warning(f'Pressure or Temprature for Unit with tag={UnitObject.tag} entered equal Zero and it cause a devision By Zero Error '+
                  f'So the code do not calculate any Gas Outflow (GasUnitHole Model) for this Plant Unit')
            return -1
        
        Gamma=SubstanceObject.Specific_Heat_Ratio
        #Check if Gamma has not been assign to the material
        if Gamma==None:
            warning(f'Unit with tag={UnitObject.tag} With materialTag {SubstanceObject.tag} Has no Gamma (specific heat ratio) for its material'+
                  f'So the code do not calculate any Gas Outflow (GasUnitHole Model) for this Plant Unit')
            return -1
        
        M=SubstanceObject.Molecular_Weight
        #Check if Molecular_Weight has not been assign to the material
        if M==None:
            warning(f'Molecular_Weight for materialTag {SubstanceObject.tag} used in Unit with tag={UnitObject.tag} Has not defined By the user'+
                  f'So the code do not calculate any Gas Outflow (GasUnitHole Model) for this Plant Unit')
            return -1        
        
        z=1 #Compresibility considered equal to 1
        
        R=self.Gas_Constant
        
        Ah=3.1415*self.Hole_Diameter**2/4
        Cd=self.Cd
        
        T=self.Total_t
        
        
        #Calculations
        if P0>((Gamma+1)/2)**(Gamma/(Gamma-1))*Pa: # (2.16)
            Psi=1                                  # (2.20)
        else:
            Psi=(2/(Gamma-1)*((Gamma+1)/2)**((Gamma+1)/(Gamma-1))*(Pa/P0)**(2/Gamma)*(1-(Pa/P0)**((Gamma-1)/Gamma)))**0.5 # (2.21)
            
        qs=Ah*Cd*P0*Psi*(Gamma*(2/(Gamma+1))**((Gamma+1)/(Gamma-1))*M/z/T0/R)**0.5 # (2.19)
        # print('Ah,Cd,P0,Psi,Gamma,M,z,T0,R')
        # print(Ah,Cd,P0,Psi,Gamma,M,z,T0,R)
        
        #Check Volume of the release 
        if TotalMass!=None and T*qs>TotalMass: T=round(TotalMass/qs)
            
        self.t_release=[0, T]
        self.MassGasReleaseRate=[0, qs]
        self.dMassGas_release=[0, qs*T]
        self.TotalMassGas_Release=[0, qs*T]
        
        
        self.MassLiquidReleaseRate=[0 for i in self.t_release]
        self.dMassLiquid_release=[0 for i in self.t_release]   
        self.TotalMassLiquid_Release=[0 for i in self.t_release] 
        
        
        return 0
        
        