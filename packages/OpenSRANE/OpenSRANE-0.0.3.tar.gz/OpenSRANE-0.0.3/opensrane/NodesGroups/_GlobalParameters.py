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


import random as _rnd

class _GlobalParameters():
    
    
    
    def __init__(self,Type=None, xGlobalList=None, yGlobalList=None, zGlobalList=None, AreaList=None, IntensityList=None, 
                 pressure_probit_tag=None, radiation_probit_tag=None, Toxic_probit_tag=None):
    
        #Properties that a node should have:
        
        self.Type=Type                      #Type that defines content of the node: Social, Environmental , ...
        
        self.xGlobalList=xGlobalList                #Global xcoordinate of the node
        self.yGlobalList=yGlobalList                #Global ycoordinate of the node
        self.zGlobalList=zGlobalList                #Global zcoordinate of the node
        
        self.AreaList=AreaList                      #Area of the defined node that considered as rectangular and along main axis
        
        self.IntensityList=IntensityList            #Intensity of the node (Intendity per Area). If node is Social show the crowd per area, if environmental shows the plants per area
        
        #Probit Functions tag
        self.pressure_probit_tag=pressure_probit_tag
        self.radiation_probit_tag=radiation_probit_tag
        self.Toxic_probit_tag=Toxic_probit_tag      #Toxic probit tag can be single integer value or can be a list of the integers of multiple toxic probits for different materials
        
  

        self.wipeAnalysis()
                
    def wipeAnalysisGlobal(self): 
        
        #isDamaged list that shows the corresponding areas nodes has bean damaged or not
        self.isDamagedList=[]                       #A boolean List that shows does each node damaged or not 
        self.DamageSource=[]                        #A list of damage Source names for each node
        self.DamageSourceTag=[]                     #A list of damage Source Tags for each node
        self.DamageSourceDose=[]                    #A list of damage Source Dose for each node
        self.DamageSourceType=[]                    #A list of damage Source Type (OverPressure, Radiation, Toxic) for each node  

        self.Radiation_Intensity=[]                 #A list of Radiation intensity for each node
        self.OverPressure_Intensity=[]              #A list of OverPressure intensity for each node 
        self.Toxic_Intensity=[]                     #A list of Toxic intensity for each node 

        self.Radiation_Probit=[]                    #List of Radiation Intensity Multiplied by its corresponding Probit
        self.OverPressure_Probit=[]                 #List of OverPressure Intensity Multiplied by its corresponding Probit
        #Self.Toxic_Probit=[]                        #List of ...
        
        

    def wipeAnalysis(self):
        self.wipeAnalysisGlobal()
        pass                 
        