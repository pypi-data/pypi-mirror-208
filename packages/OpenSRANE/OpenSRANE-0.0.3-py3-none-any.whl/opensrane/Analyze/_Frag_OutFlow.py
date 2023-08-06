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

class _Frag_OutFlow():
    
    
                  
    def Analyze():
        '''
        This Function Determine the OutFlow model for Damaged Units under a HAZARD Fragility
        
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
        #Get all OutFlowModel Objects
        # OutFlowModelObjs=_opr.OutFlowModel.ObjManager.TagObjDict
        
        #get all connectors Objects
        ConnObjs=_opr.Connectors.ObjManager.TagObjDict
        #print(f'For each Fragility tag {[i.tag for i in DSLOCs.values()()]} the Corresponding LOC event is={[i.LOCList for i in DSLOCs.values()]} with coresponding probability={[i.LOCProbabilityList for i in DSLOCs.values()]}')
        

        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        #print(f'Objectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')

        #---------------------------------- Second Part: Analyze -------------------------------------------#
         
        
        ZeroResults='Start Analysis:\n'
        
        #Get DS_LOC Objects dictionaries {FragilityTag:Connectors.DS_LOC Object}
        DSLOCs={j.FragilityTag:j for i,j in ConnObjs.items() if j.__class__.__name__=='DS_LOC'}
        
        
        #For Each Damaged Plant Unit 
        for unit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.isdamaged==True and DamagedUnit.OutFlowModelObject==None and DamagedUnit.DamageLevel==0]: #For Each Damaged Plant Unit that previously it didn't calculated for outflow model
            
            #Get one OutFlow Model According Ds-Loc defined for the Fragility
            OutFlowModelObj=DSLOCs[unit.DamageFragilityTag].Give1OutFlowModel()

            unit.OutFlowModelObject=_deepcopy(OutFlowModelObj)
            unit.OutFlowModelObject.UnitObject=unit
            unit.OutFlowModelObject.Calculate()      #To calculate outFlow calculations
            unit.OutFlowModelname=unit.OutFlowModelObject.name
            unit.OutFlowModelTag=unit.OutFlowModelObject.tag
            
            
                #The below prints are for checking the results
                #print('OutFlow Calculation time=',unit.OutFlowModelObject.t_release)
                #print('OutFlow Calculation Volume in each step=',unit.OutFlowModelObject.dMassLiquid_release)
                #print('OutFlow Calculation TotalVolume in each step=',unit.OutFlowModelObject.TotalMassLiquid_Release)
                
                
            #print('random OutflowModel=',unit.OutFlowModelname)
            
            #print(f'Unit with tag {unit.tag}:')
            #print('is damaged:',unit.isdamaged)
            #print('Unit Class name=',unit.__class__.__name__)
            #print('Unit Fragility tag or mode that is damaged for:',unit.DamageFragilityTag)
            #print('Damage Level',unit.DamageLevel)
            
            #print()
            
            
            

                    
        return  
            
            