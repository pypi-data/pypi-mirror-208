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

class Site(_NewClass, _GlobalParameters):
    '''
    This Class Defines Site condition
    
    '''
    Title="Site Data"

    
    def __init__(self,tag, Temperature=273+20, Pressure=1*10**5, XSiteBoundary=[0],YSiteBoundary=[0],
                 g=9.81, OngroundTemprature=None, Airdensity=1.21,Humidity=0.6):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _GlobalParameters.__init__(self)
  
        self.Temperature=Temperature #Site Temperature
        self.Pressure=Pressure     #Site Atmospher Pressure

        self.XSiteBoundary=XSiteBoundary #Site Boundary X Values
        self.YSiteBoundary=YSiteBoundary #Site Boundary Y Values
        
        self.g=g                         #Gravitational Acceleration
        
        self.OngroundTemprature=OngroundTemprature
        
        self.Airdensity=Airdensity        #it is considered equal to 1.21  kg/m^3 
        
        self.Humidity=Humidity            #relative humidity of the atmosphere
        
        
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass