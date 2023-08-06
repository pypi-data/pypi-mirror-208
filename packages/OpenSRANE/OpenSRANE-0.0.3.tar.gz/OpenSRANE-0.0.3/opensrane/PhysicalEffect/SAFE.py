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

class SAFE(_NewClass,_GlobalParameters):
    
    '''
    This Object is for safe physical effect condition means that no physical effect happened.

    '''
    Title='SAFE'
    
    def __init__(self,tag,):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
        
    @property
    def name(self):    
        return f'SAFE Physical Effect for unit with tag {self.UnitObject.tag} ' if self.UnitObject!=None else 'SAFE Physical Effect But still No Plant unit is assigned to it'
