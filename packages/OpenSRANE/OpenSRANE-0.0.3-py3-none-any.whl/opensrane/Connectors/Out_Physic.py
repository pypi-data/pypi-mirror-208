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

class Out_Physic(_NewClass):
    '''
    
    This Object connect the various physical effects (with their corresponding probabilities) to the OutFlow models
    
    OutFlowModel===same Loss Of Containment (LOC)
    '''
    
    
    Title='OutFlow to Physical Effect'
    
    def __init__(self,tag,OutFlowTag,MaterialsTagList,PhysicalEffectTagList,PhysProbabilityList=None):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        self.OutFlowTag=OutFlowTag
        
        
        if type(PhysicalEffectTagList)!=list:
            self.PhysicalEffectTagList=list(PhysicalEffectTagList) #List of LOC that is defined in OUTFlowModel 
        else:
            self.PhysicalEffectTagList=PhysicalEffectTagList
                
        if type(MaterialsTagList)!=list:
            self.MaterialsTagList= list(MaterialsTagList)
        else:
            self.MaterialsTagList= MaterialsTagList
            
        if type(PhysProbabilityList)!=list: #Corresponding LOC Probability list
            self.PhysProbabilityList=list(PhysProbabilityList) 
        else:
            self.PhysProbabilityList=PhysProbabilityList
        
        if PhysProbabilityList!=None: #Normaling the probability list values 
            self.PhysProbabilityList=[i/sum(PhysProbabilityList) for i in PhysProbabilityList]

            
        self.name=f'(Out_Physic) OutFlow to Physical Effect with tag {tag} and connected to Physical EffectTagList tags={PhysicalEffectTagList} with probability distribution equal to {PhysProbabilityList}'    
            
            
    def Give1PhysicalEffectModel(self):
        '''
        This Function According The probability Values that is defined for 
        Physical Effect Models, Returns a Physical Effect Model
        '''
        import random as _rnd
        
        if self.PhysProbabilityList==None or len(self.PhysProbabilityList)==1:
            return _opr.PhysicalEffect.ObjManager[self.PhysicalEffectTagList[0]]
        
            
        plist=self.PhysProbabilityList
        CProbList=[sum(plist[0:i]) for i in range(1,len(plist)+1)] #Comulitative Probability Values

        rand=_rnd.random()

        for ind,val in enumerate(CProbList):
            if rand<=val:
                return _opr.PhysicalEffect.ObjManager[self.PhysicalEffectTagList[ind]]
        
        
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
       
            
        
    