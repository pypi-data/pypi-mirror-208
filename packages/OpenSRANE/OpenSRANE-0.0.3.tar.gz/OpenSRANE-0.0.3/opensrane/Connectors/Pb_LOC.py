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
import opensrane as _opr

class Pb_LOC(_NewClass):
    '''
    
    This Object Specify Any Probit to LOC's and their correponding Probability
    
    Or we can say that this Object, connect Probit to the LOC cases
    
    OutFlowModel===same Loss Of Containment (LOC)
    '''
    
    Title='Probit to LOC'
    
    
    def __init__(self,tag,ProbitTag,OutFlowModelTagList,LOCProbabilityList=None):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        self.ProbitTag=ProbitTag
        
        
        if type(OutFlowModelTagList)!=list:
            self.OutFlowModelTagList=list(OutFlowModelTagList) #List of LOC that is defined in OUTFlowModel 
        else:
            self.OutFlowModelTagList=OutFlowModelTagList
                
        
        if type(LOCProbabilityList)!=list: #Corresponding LOC Probability list
            self.LOCProbabilityList=list(LOCProbabilityList) 
        else:
            self.LOCProbabilityList=LOCProbabilityList
        
        if LOCProbabilityList!=None: #Normaling the probability list values 
            self.LOCProbabilityList=[i/sum(LOCProbabilityList) for i in LOCProbabilityList]

            
        self.name=f'(Pb_LOC) Probit to LOC with tag {tag} and connected to OutFlow tags={OutFlowModelTagList} with probability distribution equal to {LOCProbabilityList}'    
        
    def Give1OutFlowModel(self):
        '''
        This Function According The uniform probability Values that is defined for 
        OutFlow Models, Returns an OutFlow Models
        '''
        
        import random as _rnd
        
        if self.LOCProbabilityList==None or len(self.LOCProbabilityList)==1:
            return _opr.OutFlowModel.ObjManager[self.OutFlowModelTagList[0]]
        
            
        plist=self.LOCProbabilityList
        CProbList=[sum(plist[0:i]) for i in range(1,len(plist)+1)] #Comulitative Probability Values

        rand=_rnd.random()

        for ind,val in enumerate(CProbList):
            if rand<=val:
                return _opr.OutFlowModel.ObjManager[self.OutFlowModelTagList[ind]]
        
        
    # @staticmethod    
    # def _str2cls(name): #Convert The input OutFlow models name to their Corresponding Class
        
        # SubPackname=_opr.Misc.GetClassParrentModule('DS_LOC')[0] #name of the SubPackage of OutFlow and DS_LOC folder if in future The name of This Subpackage Changes

        # if type(name)==str:
        
            # lst=[i[1] for i in _opr.Misc.GetClasses() if i[0].upper()==name.upper() and i[2].upper()==SubPackname.upper()]
            
            # if lst==[]:
                # return None
            # else:
                # return lst[0]
                
        # else:
            
            # lst=[i[1] for i in _opr.Misc.GetClasses() if i[2].upper()==SubPackname.upper()] #List of Class Objects
            # if name in lst:
                # return name
            # else:
                # return None
       
            
        
    