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

class _DispSprd():


    '''
    This function perform analysis to assign spread dispersion model to each damaged plant unit
    IMPORTANT ATTENTION: it is really important to remember that
    Before using this Object, self.UnitObject should be assigned and shouldn't be empty
    
    '''
    
    
                  
    def Analyze():
        '''
        This Function assigns the Dispersion spread model to the objects and also calculate the 
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
       #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        #print(f'Objectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')
        
        #Get All Dispersion Spread Objects
        DispSprdObjs=_opr.DispersionSpreadModels.ObjManager.Objlst

        #---------------------------------- Second Part: Analyze -------------------------------------------#
        
        #get the last damage level
        last_damage_level=[unit.DamageLevel for unit in AllUnits if unit.DamageLevel!=None]
        if last_damage_level==[]: return None #Means that no Plant unit damaged under External Excitation
        last_damage_level=max(last_damage_level)
        
        
        ZeroResults='Start Analysis:\n'
        
        
        #For Each Damaged Plant Unit 
        for unit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.isdamaged==True and DamagedUnit.OutFlowModelTag!=None and DamagedUnit.DispersionSpreadModelObject==None and DamagedUnit.DamageLevel==last_damage_level]: #For Each Damaged Plant Unit that previously it didn't calculated for outflow model
            
            #Get unit OutFlow and Substance tag
            OutFlowtag=unit.OutFlowModelTag
            SubstanceTag=unit.SubstanceTag

            #Search for Dispersion Spread Model (object) that is compatible With the Unit Substance and Type Of OutFlow
            for DispSprdmodel in DispSprdObjs:
                

                if OutFlowtag in DispSprdmodel.OutFlowModelTags and SubstanceTag in DispSprdmodel.MatTags:
                    #Assign Dispersion spread model data and object to the plant Unit
                    unit.DispersionSpreadModelTag=DispSprdmodel.tag
                    unit.DispersionSpreadModelname=DispSprdmodel.name
                    unit.DispersionSpreadModelObject=_deepcopy(DispSprdmodel)
                    #print('unittag= ',unit.tag, ' DispersionTag=',unit.DispersionSpreadModelTag)
                    
                    #Assign unit Object to the Assigned unit Dispersion spread object and then do calculations
                    unit.DispersionSpreadModelObject.UnitObject=unit  
                    unit.DispersionSpreadModelObject.Calculate()     #To do calculations if needed
                    break  #Attention : Now it means that Only one Dispesion or spread model can be consider for 
            
            
        return  
            
            