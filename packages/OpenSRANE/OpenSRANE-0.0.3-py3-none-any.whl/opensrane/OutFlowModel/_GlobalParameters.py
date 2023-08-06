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


import random as _rnd

class _GlobalParameters():
    
    
    
    def __init__(self):
        

        self.wipeAnalysis()

    def wipeAnalysisGlobal(self):    
    
        #ATTENTION: Obviously All results at time[0] should be [0]        
        #Results of OutFlow Object Should Be Liquid or Gas 
        self.t_release=None  #Time list of outFlow or release
        
        self.MassLiquidReleaseRate=None   #Mass Liquid Release rate in each step 
        self.dMassLiquid_release=None     #Mass Liquid list of OutFlow Or release in each time step (Delta Mass)
        self.TotalMassLiquid_Release=None #Total Mass Liquid list of OutFlow Or release in each time step
        
        self.MassGasReleaseRate=None      #Mass Gas Release rate in each step 
        self.dMassGas_release=None        #Mass Gas list of OutFlow Or release in each time step (Delta Mass)
        self.TotalMassGas_Release=None    #Total Mass Gas list of OutFlow Or release in each time step
        
        self.UnitObject=None

    def wipeAnalysis(self):
        self.wipeAnalysisGlobal()
        pass          
        
      
     
    def Calculate(self):
        
        #Each class calculate part is reponsible for doing the calculations of outflow and fill the liquid or gas or both parameters that are specified in __init__ part in the above
        #Important anttention: Calcualte will return 0 if it works correctly and it will returns 0 if not
        
        UnitObject=self.UnitObject #self.UnitObject is defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        return -1
        
        