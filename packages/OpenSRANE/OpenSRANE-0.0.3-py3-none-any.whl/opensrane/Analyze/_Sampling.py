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
import random as _rnd

class _Sampling():
    
    
                  
    def Sample():
        '''
        This Function Performs Sampling part and generate samples of Requiared random variables
        
        It is very important that pay attention that any sampling of objects only should be done here
        And they should be store in objects variables and anywhere that we need them to avoid any mistake 
        Just use the sampled values and do not generate them agian that is wrong (Obviously in any Monte Carlo simulation only one time we can do sampling)

        '''
        #get Date Object
        DateObj=_opr.DateAndTime.ObjManager.Objlst[0]
        
        #get Wind Object
        WindObj=_opr.WindData.ObjManager.Objlst[0]

        #get Hazard Object
        hazard=_opr.Hazard.ObjManager.Objlst[0]

        #Generate a date sample
        DateObj.SampleisDay()
        
        #Genrate a Wind Sample
        WindObj.GetRandomWindِSample()
        
        #Generate a Hazard Magnitude Sample
        hazard.SampleRandomMagnitude()  

                    
        return 0            
            