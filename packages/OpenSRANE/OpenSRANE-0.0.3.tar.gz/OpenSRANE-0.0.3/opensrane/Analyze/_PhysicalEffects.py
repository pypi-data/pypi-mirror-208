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

class _PhysicalEffects():
    
    
                  
    def Analyze():
        '''
        This Function Calculate the physical events effect on the undamaged units according the physical events that happens 
        for elments that has been damaged in the last step
        Then
        if the element damaged, the corresponding outflow will be assigned to the cuurent element
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
        #Get All defined Fragilities Dictionary
        FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict
        #print(f'Defined Fragility Tags={[tag for tag,obj in FragTagObjs.items()]}')
        

        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst

        
        #print(f'Ob jectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')
        
        #get the last damage level
        last_damage_level=[unit.DamageLevel for unit in AllUnits if unit.DamageLevel!=None]
        if last_damage_level==[]: return None #Means that no Plant unit damaged under External Excitation
        last_damage_level=max(last_damage_level)
        #---------------------------------- Second Part: Analyze -------------------------------------------#
         
        
        ZeroResults='Start Analysis:\n'
        

        #TotalResults is a parameter that shows Finally did we have a damaged unit or not
        TotalResults=None
        #For Each UnDamaged Plant Unit 
        for unit in [unDamagedUnit for unDamagedUnit in AllUnits if unDamagedUnit.isdamaged==False]: #For Each UnDamaged Plant Unit
            
            
            #Get Pressure and Radiation Probit Objects
            pressure_probit_obj=FragTagObjs[unit.pressure_probit_tag] if unit.pressure_probit_tag!=None else None
            radiation_probit_obj=FragTagObjs[unit.radiation_probit_tag] if unit.radiation_probit_tag!=None else None
            
            #Get unit boundary points that all 
            boundarypoints=unit.boundary_points
            

            #Define 2 important functions that handle the Vulnerability of the unit under Physical effects. Then we use them randomly
            def overpressurecase():
                #Function of checking vulnerability under overpressure physical effect
                if pressure_probit_obj==None: return None
                
                #Check for each unit that is damaged in the last level
                for damunit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.DamageLevel==last_damage_level and DamagedUnit.PhysicalEffectObject!=None]: 
                    
                    #Get the maximum dose of Overpressure on currentunit(unit) from the damaged unit(damunit)
                    Dose=[damunit.PhysicalEffectObject.OverPressure_at_Point(point[0],point[1],point[2]) for point in boundarypoints if damunit.PhysicalEffectObject.OverPressure_at_Point(point[0],point[1],point[2])!=None]
                    if Dose==[]: continue
                    Dose=max(Dose)
                    Probability_of_damage=pressure_probit_obj.GetProbability(Dose) #Get the probability of damage at calculated dose from its related defined probit
                    Rnd=_rnd.random() #Generate a random variable between 0 and 1
                    
                    if Rnd<=Probability_of_damage: #Means that the unit is damaged by the Physical effect of the damUnit
                        
                        unit.isdamaged=True
                        unit.DamageLevel=last_damage_level+1
                        unit.DamageSource=damunit.__class__.__name__
                        unit.DamageSourceTag=damunit.tag
                        unit.DamageSourceDose=Dose
                        unit.DamageSourceType='Overpressure'
                        unit.DamageFragilityTag=pressure_probit_obj.tag                

                        return 'Damaged'  
                
                return None

            def radiationcase():
                #Function of checking vulnerability under Radiation physical effect
                if radiation_probit_obj==None: return None
                
                #Check for each unit that is damaged in the last level
                TotalDose=[0 for point in boundarypoints]
                DamageSources=[]
                DamageSourcesTag=[]
                for damunit in [DamagedUnit for DamagedUnit in AllUnits if DamagedUnit.isdamaged==True and DamagedUnit.PhysicalEffectObject!=None]:
                
                    #Get the maximum dose of Radiation on currentunit(unit) from the damaged unit(damunit)
                    Dose=[damunit.PhysicalEffectObject.Thermal_Radiation_at_Point(point[0],point[1],point[2]) for point in boundarypoints if damunit.PhysicalEffectObject.Thermal_Radiation_at_Point(point[0],point[1],point[2])!=None]
                    if Dose==[]: continue
                    TotalDose=[i+j for i,j in zip(TotalDose,Dose)]
                    DamageSources.append(damunit.__class__.__name__)
                    DamageSourcesTag.append(damunit.tag)
                    
                Probability_of_damage=radiation_probit_obj.GetProbability(max(TotalDose)) #Get the probability of damage at calculated dose from its related defined probit
                Rnd=_rnd.random() #Generate a random variable between 0 and 1
                
                #Check if radiation maximum dose is greater than the LastRadiationDose+RadiationDifferenceDose 
                RadiationCheck=False
                if unit.LastRadiationDose==None:
                    unit.LastRadiationDose=max(TotalDose)
                    RadiationCheck=True
                elif unit.LastRadiationDose+unit.RadiationDifferenceDose<=max(TotalDose):
                    unit.LastRadiationDose=max(TotalDose)
                    RadiationCheck=True                    
                    
                if Rnd<=Probability_of_damage and RadiationCheck==True: #Means that the unit is damaged by the Physical effect of the damUnit AND Current Max Dose is greater than LastRadiationDose+RadiationDifferenceDose 
                    
                    unit.isdamaged=True
                    unit.DamageLevel=last_damage_level+1
                    unit.DamageSource=DamageSources
                    unit.DamageSourceTag=DamageSourcesTag
                    unit.DamageSourceDose=max(TotalDose)
                    unit.DamageSourceType='Radiation'
                    unit.DamageFragilityTag=radiation_probit_obj.tag
                    
                    return 'Damaged'
                
                return None

            #Randomly decide to check witch one be the first (Overpressure or Radiation)
            if _rnd.randint(0,1)==0:
                Results=overpressurecase()
                if Results!='Damaged': Results=radiationcase() #means that in under over pressure it doesn't damaged the check the Radiation
            else:
                Results=radiationcase()
                if Results!='Damaged': Results=overpressurecase() #means that in under Radiation it doesn't damaged the check the over pressure
            
            if Results!=None: TotalResults='Damaged'
            

                    
        return  TotalResults
            
            