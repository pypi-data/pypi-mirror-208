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
from scipy.interpolate import interp1d as _interpo
import random as _rnd

class Earthquake(_NewClass,_GlobalParameters):
    
    
    def __init__(self,tag,DefType='PGA',Magnitude=[],Probabilities=[]):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        _GlobalParameters.__init__(self)
        
        
        self.DefType=DefType                 #Type of earthquake Hazard Definition
        self.Magnitude=Magnitude             #Earthquake Magnitude Values 
        self.Probabilities=Probabilities     #Corresponding 

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass

    def SampleRandomMagnitude(self,rnd=None):
        '''
        returns a Magnitude according generated a uniform random value between 0 and 1
        '''
        if rnd==None or rnd>1 or rnd<0:
           rnd=_rnd.random()
        
        if rnd<min(self.Probabilities): 
            self.SampledMagnitude=max(self.Magnitude)
        elif rnd>max(self.Probabilities): 
            self.SampledMagnitude=0
        else:
            f=_interpo(self.Probabilities,self.Magnitude)
            self.SampledMagnitude=f(rnd)
        
        return self.SampledMagnitude
