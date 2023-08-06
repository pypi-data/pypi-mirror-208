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
from copy import deepcopy as _deepcopy
from opensrane.Misc.WarningRecorder import *


class _PhysicalAssign():
    
    
                  
    def Analyze():
        '''
        This Function assign physical models to the corresponding Objects according their probability distribution and according the outflow type
        using Out_Physic connectors 
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
        #get all DS_LOC Objects
        ConnObjs=_opr.Connectors.ObjManager.TagObjDict
        #print(f'For each Fragility tag {[i.tag for i in DSLOCs.values()()]} the Corresponding LOC event is={[i.LOCList for i in DSLOCs.values()]} with coresponding probability={[i.LOCProbabilityList for i in DSLOCs.values()]}')
        

        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        #print(f'Objectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')


        #get the last damage level
        last_damage_level=[unit.DamageLevel for unit in AllUnits if unit.DamageLevel!=None]
        if last_damage_level==[]: return None #Means that no Plant unit damaged under External Excitation
        last_damage_level=max(last_damage_level)
        #---------------------------------- Second Part: Analyze -------------------------------------------#
         
        
        ZeroResults='Start Analysis:\n'
        
        #Get Out_Physic Objects dictionaries {OutFlowTag:Connectors.Out_Physic Object}
        Out_Physic={j.OutFlowTag:j for i,j in ConnObjs.items() if j.__class__.__name__=='Out_Physic'}
        
        #Convert Above disctionary to {(OutFlowTag,materialTag):Connectors.Out_Physic Object}
        temp={}
        for obj in Out_Physic.values():
            for matTag in obj.MaterialsTagList:
                temp[(obj.OutFlowTag,matTag)]=obj
        Out_Physic=temp
        del(temp)
        # print(Out_Physic)
        
        
        #For Each Damaged Plant Unit 
        for unit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.isdamaged==True and DamagedUnit.OutFlowModelObject!=None and DamagedUnit.DispersionSpreadModelObject!=None and DamagedUnit.PhysicalEffectObject==None and DamagedUnit.DamageLevel==last_damage_level]: #For Each Damaged Plant Unit that previously had outflow model But its PhysicalEffectObject=None
            
            #Check if unit material and outflow model is connected to a Physical effect or not
            if (unit.OutFlowModelTag,unit.SubstanceTag) not in Out_Physic.keys():
                warning(f'For Plant Unit with tag {unit.tag} Out_Physic connector for combination of OutFlow model with tag {unit.OutFlowModelTag} and Material or substance with tag {unit.SubstanceTag} Has not been defined so  no Physical Effect Model did not assign to this unit.')
                continue 
            
            #Get one OutFlow Model According Ds-Loc defined for the Fragility
            PhysicEffectObj=Out_Physic[(unit.OutFlowModelTag,unit.SubstanceTag)].Give1PhysicalEffectModel()
            # print('Title=',PhysicEffectObj.Title) 
            #if OutFlowModelObj!=None:?????
            unit.PhysicalEffectObject=_deepcopy(PhysicEffectObj)
            unit.PhysicalEffectObject.UnitObject=unit
            # print('unit.PhysicalEffectObject.UnitObject=',unit.PhysicalEffectObject.UnitObject)
            unit.PhysicalEffectModelname=unit.PhysicalEffectObject.name
            # print('PhysicalEffectModelname=',unit.PhysicalEffectModelname)
            unit.PhysicalEffectModelTag=unit.PhysicalEffectObject.tag
            # print()

            # print(f'**Radiation Results for unit with tag={unit.tag}=',unit.PhysicalEffectObject.RadiationBoundary(4000,2,20))

            
        # input('...')    
            

                    
        return  
            
            