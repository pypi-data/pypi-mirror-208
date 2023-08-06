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

class _Prob_OutFlow():
    
    
                  
    def Analyze():
        '''
        This Function Determine the OutFlow model for Damaged Units under a Physical Effect using Probit-OutFlow defined Object
        
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
        #get Site Object
        # site1=_opr.Sites.ObjManager.Objlst[0]
        #print('First defined site Temperature=',site1.Temperature)
                
        #get Hazard Object
        # hazard=_opr.Hazard.ObjManager.Objlst[0]
        #print('defined Hazard Magnitude type is=', hazard.DefType)
        
        #Get All defined Fragilities
        # FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict
        #print(f'Defined Fragility Tags={[tag for tag,obj in FragTagObjs.items()]}')
        
        
        #Get all OutFlowModel Objects
        # OutFlowModelObjs=_opr.OutFlowModel.ObjManager.TagObjDict
        
        #get all connectors Objects
        ConnObjs=_opr.Connectors.ObjManager.TagObjDict
        #print(f'For each Fragility tag {[i.tag for i in DSLOCs.values()()]} the Corresponding LOC event is={[i.LOCList for i in DSLOCs.values()]} with coresponding probability={[i.LOCProbabilityList for i in DSLOCs.values()]}')
        

        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        #print(f'Objectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')

        #---------------------------------- Second Part: Analyze -------------------------------------------#
        
        #get the last damage level
        last_damage_level=[unit.DamageLevel for unit in AllUnits if unit.DamageLevel!=None]
        if last_damage_level==[]: return None #Means that no Plant unit damaged under External Excitation
        last_damage_level=max(last_damage_level)
       
        
        ZeroResults='Start Analysis:\n'
        
        #Get Pb_LOC Objects dictionaries {ProbitTag:Connectors.Pb_LOC Object}
        Pb_LOC={j.ProbitTag:j for i,j in ConnObjs.items() if j.__class__.__name__=='Pb_LOC'}

        
        #For Each Damaged Plant Unit 
        for unit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.isdamaged==True and DamagedUnit.OutFlowModelObject==None and last_damage_level>0 and DamagedUnit.DamageLevel==last_damage_level]: #For Each Damaged Plant Unit that previously it didn't calculated for outflow model
            
            
            #Get one OutFlow Model According Pb_LOC defined for the Probit
            OutFlowModelObj=Pb_LOC[unit.DamageFragilityTag].Give1OutFlowModel()
            #if OutFlowModelObj!=None:?????
            unit.OutFlowModelObject=_deepcopy(OutFlowModelObj)
            unit.OutFlowModelObject.UnitObject=unit
            unit.OutFlowModelObject.Calculate()      #To calculate outFlow calculations
            unit.OutFlowModelname=unit.OutFlowModelObject.name
            unit.OutFlowModelTag=unit.OutFlowModelObject.tag
            

                    
        return  
            
            