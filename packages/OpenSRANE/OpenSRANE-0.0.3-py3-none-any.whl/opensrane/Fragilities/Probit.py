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
from scipy.stats import norm as _norm
from scipy.stats import lognorm as _lognorm
import math as _math

class Probit(_NewClass,_GlobalParameters):
    '''
    This Class create a Probit object and takes the Probit parameters and return (probability)
    Value for Given Random Variable
    Pr=K1x+K2 (normal Distribution)
    Pr=K1*Ln(x)+K2 (lignormal Distribution)
    
    Distribution_Type= 'normal' or 'lognormal'
    ToxicMaterialslist= list of materials that are toxic and should be defined to be consider for using for this function (Obviously it doesn't have any effect on Radiation and Overpressure cases)
    MinRndVar= a value that will be consider as the minimum intensity random variable and GetProbability returns 0 for random variables less than this value (Example: if minimum radiation that injure is 4 this value should be enter 4 then for any value less or equal to 4 its probit will return 0 as the probit probability)
    '''   
    
    Title='Probit Funbction'
    
    
    def __init__(self,tag,Distribution_Type='normal',K1=1,K2=0.5,Scale_Factor=1,ToxicMaterialslist=[], MinRndVar=0):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _GlobalParameters.__init__(self)
        
        
        
        self.DistType=Distribution_Type
        self.K1=K1
        self.K2=K2
        self.Scale_Factor=Scale_Factor
        self.ToxicMaterialslist=ToxicMaterialslist
        self.MinRndVar=MinRndVar
        
        #According K1 and K2 mean and StdDev calculate as the following
        self.StdDev=1/K1
        self.mean=(5-K2)*1/K1
        
        self.name=f'Probit Function with tag= {tag} with {Distribution_Type} distribution and K1={K1} and K2 ={K2}'

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass

    
    def GetProbability(self,RandomVariable):

        if RandomVariable<=self.MinRndVar: return 0
        
        RandomVariable=RandomVariable/self.Scale_Factor
        
        if self.DistType=='normal': dist=_norm(loc=self.mean,scale=self.StdDev)
        elif self.DistType=='lognormal': dist=_lognorm(s=self.StdDev,scale=_math.exp(self.mean))
        
            
        return dist.cdf(RandomVariable)
        
    pass