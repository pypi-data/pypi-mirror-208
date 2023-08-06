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
from ._GlobalParameters import _GlobalParameters
import math as _math
import opensrane as _opr

class SimultaniousGas(_NewClass,_GlobalParameters):
    
    '''
    OutFlow Model For Gas Complete OutFlow Simulaneously
    Release_Ratio: Ratio of the substance that release simultanously. (The Following Calculations will be done on the released volume and the remain substance will be eliminated by the code)
    
    '''
    Title='SimultaniousGas'
    
    def __init__(self,tag,Release_Ratio=1):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.Release_Ratio=Release_Ratio
        
        
        self.name=f'SimultaniousGas'

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass

        
    def Calculate(self):
        
        Release_Ratio=self.Release_Ratio
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        

        
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag]
        SiteObject=_opr.Sites.ObjManager.Objlst[0]
         
        
        Pout=SiteObject.Pressure        #OutSide Pressure
        Tout=SiteObject.Temperature      #OutSide Temperature
        
        Pin=UnitObject.Pressure         #Inside Pressure
        Tin=UnitObject.Temperature       #Inside Temperature
        
        d=UnitObject.d_Storage          #Tank Diameter

            
        Vsubs=UnitObject.V_subs

     
        Rho=SubstanceObject.Density
        M=Vsubs*Rho*Release_Ratio                    #Initial Mass of the Substance
        
        

        t_release=[0,0.01]
        MassGasReleaseRate=[0, M/0.01]
        dMassGas_release=[0, M]
        TotalMassGas_Release=[0, M]
    
        self.t_release=t_release
        self.MassGasReleaseRate=MassGasReleaseRate
        self.dMassGas_release=dMassGas_release
        self.TotalMassGas_Release=TotalMassGas_Release              
            
        self.MassLiquidReleaseRate=[0 for i in self.t_release]
        self.dMassLiquid_release=[0 for i in self.t_release]   
        self.TotalMassLiquid_Release=[0 for i in self.t_release]
       
        return 0
        
        