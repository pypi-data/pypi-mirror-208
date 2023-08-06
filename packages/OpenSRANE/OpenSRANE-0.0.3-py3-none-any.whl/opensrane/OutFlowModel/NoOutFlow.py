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

class NoOutFlow(_NewClass,_GlobalParameters):
    '''
    This mpdel is for considering no Out flow
    The Outflow steps considered only 2 steps and the duration is considered equal to 30 minutes
    And for all outflow results, 0 assigned for each step that shows no outflow
    '''
    
    
    Title='No OutFlow'
    
    def __init__(self,tag, ReleaseDuration=30*60):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        _GlobalParameters.__init__(self)
        
        
        self.ReleaseDuration=ReleaseDuration
        
        self.name=f'NoOutFlow'
        
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
            
        t=self.ReleaseDuration
        self.t_release=[0, t]               #Time list of outFlow or release
        
        self.MassLiquidReleaseRate=[0, 0]   #Mass Liquid Release rate in each step 
        self.dMassLiquid_release=[0, 0]     #Mass Liquid list of OutFlow Or release in each time step (Delta Mass)
        self.TotalMassLiquid_Release=[0, 0] #Total Mass Liquid list of OutFlow Or release in each time step
        
        self.MassGasReleaseRate=[0, 0]      #Mass Gas Release rate in each step 
        self.dMassGas_release=[0, 0]        #Mass Gas list of OutFlow Or release in each time step (Delta Mass)
        self.TotalMassGas_Release=[0, 0]    #Total Mass Gas list of OutFlow Or release in each time step        
        
        
        
        return 0
        