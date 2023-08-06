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

class Liquid10min(_NewClass,_GlobalParameters):
    
    
    Title='Liquid10Min'
    
    def __init__(self,tag):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.name=f'Liquid10Min'

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
            
            
        '''
        This Model is for Calculating 10 minutes outflow
        '''
        
        time=10
        dt=60
        
        t_release=[i for i in range(time)]
        MassLiquidReleaseRate=[UnitObject.V_subs/time for i in range(time)]
        dMassLiquid_release=[UnitObject.V_subs/time*dt for i in range(time)]
        TotalMassLiquid_Release=[sum(dMassLiquid_release[0:i]) for i in range(1,len(dMassLiquid_release)+1)]
        
        
        self.t_release=t_release
        self.MassLiquidReleaseRate=MassLiquidReleaseRate
        self.dMassLiquid_release=dMassLiquid_release   
        self.TotalMassLiquid_Release=TotalMassLiquid_Release   

        self.MassGasReleaseRate=[0 for i in self.t_release]
        self.dMassGas_release=[0 for i in self.t_release]
        self.TotalMassGas_Release=[0 for i in self.t_release]        
        
        return 0
        
        