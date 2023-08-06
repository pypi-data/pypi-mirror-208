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

class Fragility(_NewClass,_GlobalParameters):
    '''
    This Class create a Fragility object and takes the Fragility parameters and return Fragility (probability)
    Value for Given Random Variable
    
    For 'normal' Distribution:
            the input values are mean and standard deviation of the random variables.
            
    For 'lognormal' Distribution:
            the input values are the mean and standard deviation of the normal logarithm random variables.
            Mean = the mean of ln(x) "x : random variables or magnitudes"
            StdDev = the standard deviation of ln(x) which must be positive "x : random variables or magnitudes"
    
    
    '''
    Title='Fragility'
    
    def __init__(self,tag,modename='No Fragility Mode name',Distribution_Type='normal',mean=1,StdDev=0.5):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _GlobalParameters.__init__(self)
        
        
        
        self.DistType=Distribution_Type #Type of distribution 'normal', 'lognormal','constant' 
        self.modename=modename            #Mode name
        self.mean=mean                  #mean
        self.StdDev=StdDev              #Standard Deviation
        
        self.name=f'Fragility with tag= {tag} with {Distribution_Type} distribution and mean={mean} and Standard deviation ={StdDev}'
        
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
    def GetProbability(self,RandomVariable):
                    
        if self.DistType=='normal': dist=_norm(loc=self.mean,scale=self.StdDev)
        elif self.DistType=='lognormal': dist=_lognorm(s=self.StdDev,scale=_math.exp(self.mean)) # by adding _math.exp(mean) the _lognorm act exactly like excel distribution
        elif self.DistType=='constant': dist=_constant(mean=self.mean)
        
            
        return dist.cdf(RandomVariable)
        
        
class _constant():

    '''
    costant probability distribution
    for any mean value (Fragility Paraqmeter) it returns unity as Fragility Value 
    '''
    def __init__(self,mean):
        self.mean=mean
    
    def cdf(self,RandomVariable):
        return 1
            
        
        
        
