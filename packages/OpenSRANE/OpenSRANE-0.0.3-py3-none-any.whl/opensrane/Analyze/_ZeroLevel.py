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

class _ZeroLevel():
    
    
                  
    def Analyze():
        '''
        This Function Perform The Zero level Damage Analysis for Units under Defined Hazard Magnitude
        '''
    
        #------------------------ First Part: Read Defined Objects -------------------------------------------#

        #get Hazard Object
        hazard=_opr.Hazard.ObjManager.Objlst[0]       
        
        #Get All defined Fragilities
        FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict
        #print(f'Defined Fragility Tags={[tag for tag,obj in FragTagObjs.items()]}')
        
        
        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        #print(f'Objectgs Tags={[i.tag for i in AllUnits]} and Corresponding Fragilites={[i.FragilityTagNumbers for i in AllUnits]}')

        #---------------------------------- Second Part: Analyze -------------------------------------------#
         
        
        ZeroResults='Start Analysis:\n'
        
        #Get Sampled Magnitude
        RNDMag=hazard.SampledMagnitude
        ZeroResults=ZeroResults + f'Generated Magnitude=\033[1m {RNDMag} \033[0m \n'
        
        #Calculate Plant Units that Damaged
        for unit in AllUnits:

            FragTaglist=unit.FragilityTagNumbers #Get the Fragility tag list
            #print(FragTaglist)
            TagProbdict={tag:FragTagObjs[tag].GetProbability(RNDMag) for tag in FragTaglist} #get the correspondint fragilities probability in Random Generated Magnitude
            TagProbdict=dict(sorted(TagProbdict.items(),key=lambda x: x[1]))
            #print(TagProbdict)
            Rnd=_rnd.random() #Generate a random variable between 0 and 1
            
            #Now here We should define witch Fraqgility Happend for each plant unit
            for tag,value in TagProbdict.items():
                if Rnd<=value:
                    unit.isdamaged=True
                    unit.DamageSource=hazard.__class__.__name__
                    unit.DamageSourceTag=hazard.tag
                    unit.DamageSourceDose=RNDMag
                    unit.DamageSourceType='NaturalHazard'
                    unit.DamageFragilityTag=tag
                    unit.DamageLevel=0
                                       
                    ZeroResults=ZeroResults + f'PlantUnit with tag {unit.tag} Damage condition is \033[1m {unit.isdamaged} \033[0m \n'
                    ZeroResults=ZeroResults + f'and Generated Random Value is=\033[1m {Rnd} \033[0m \n and the list of the Fragility,Prob is \033[1m{TagProbdict}\033[0m \n'
                    ZeroResults=ZeroResults + f'and the \033[1m Damage Fragility tag is {unit.DamageFragilityTag}\033[0m \n'
                    
                    break
                    
        return ZeroResults            
            