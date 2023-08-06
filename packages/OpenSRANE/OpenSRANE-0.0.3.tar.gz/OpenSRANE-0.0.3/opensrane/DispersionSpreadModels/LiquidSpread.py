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


#This is a Sample File and any new Model is better to be constructed by a copy of this file
from opensrane.Misc._NewClass import _NewClass
from .ObjManager import *
from opensrane.Misc.WarningRecorder import *
from ._GlobalParameters import _GlobalParameters
import math as _math
import opensrane as _opr

class LiquidSpread(_NewClass,_GlobalParameters):
    
    '''
    Dispersion model for Liquids According Casal
    
    In this module user should remember only the dispersion of the liquid will be model and 
    the evaporation of the liquid has not been consider
    
    if a dike wall defined for the current plant unit, then the code cosider area equal to the
    area of the dike but in circular shape. Else according the minimum thickness the raduis of circular dispersion 
    will be determine.
    
    IMPORTANT ATTENTION for developers: it is really important to remember that
    Before using this Object, self.UnitObject should be assigned and shouldn't be empty
    
    MatTags=List of Material Tags that this Model Should Be consider for them
    OutFlowModelTags= List of OutFlow models tag that this model can be consider for them
    
    MinDisThickness= minimum thichness of the liquid if no roughness has defined
    Surface_Roughnesslist=list of the surfaces roughness values
    Surface_RoughnessThickness=list of the liquid thicknesses corresponding to the Surface roughness values
    
    '''
    Title='LiquidSpreadModel'
    
    def __init__(self,tag, MatTags, OutFlowModelTags,MinDisThickness=0.01, Surface_Roughnesslist=[0.0001,0.0002],Surface_RoughnessThickness=[0.005,0.01]):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        _GlobalParameters.__init__(self,MatTags, OutFlowModelTags)
        
                
        if MinDisThickness==None or MinDisThickness<=0:
            self.MinDisThickness=0.01
        else:
            self.MinDisThickness=MinDisThickness
            
        if len(Surface_Roughnesslist)>len(Surface_RoughnessThickness):
            Surface_RoughnessThickness.extend([MinDisThickness]*(len(Surface_Roughnesslist)-len(Surface_RoughnessThickness)))
        
        self.Surface_Roughnesslist=Surface_Roughnesslist
        self.Surface_RoughnessThickness=Surface_RoughnessThickness
        
        #Dictionary that stores the surface roughness values and their corresponding stiffness                
        self.Surface_RoughnesslistDict={Rough:Thick for Rough,Thick in zip(Surface_Roughnesslist,Surface_RoughnessThickness)}

        self.name=f'{self.Title} with minimum thickness equal to {self.MinDisThickness}'

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass

        
    def Calculate(self):
    
        UnitObject=self.UnitObject    #self.UnitObject is defined in _GlobalParameters
        if UnitObject==None:         
            warning(f'(LiquidSpreadModel) for Dispersion model (LiquidSpreadModel) with tag {self.tag} the corresponing self.UnitObject is Not assigned, So Dispersion calculations stoped')
            return -1
            
        #Import required objects
        DikeObj= _opr.Safety.ObjManager[UnitObject.DikeTag] if UnitObject.DikeTag!=None else None
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag] if UnitObject.SiteTag!=None else None
        
         
        #####Importing Data####
        thmin=self.MinDisThickness
        Density=SubstanceObject.Density
        
        
        ##Object Inside and Outside Data
        Xc=UnitObject.Hlocalcoord #Unit Horizontal Local center Coordinate
        Yc=UnitObject.Vlocalcoord #Unit Vertical Local center Coordinate
        
        
        #Dike Data
        Abund, HBund, Vbund=(DikeObj.Area , DikeObj.Height, DikeObj.Volume ) if DikeObj!=None else (0, 0, 0)   #taking Dike Data Area, height, volume
        
        #Calculate Minimum Thickness
        thmin=self.MinDisThickness
        Surface_Roughness=UnitObject.Surface_Roughness
        if Surface_Roughness!=None:
            if Surface_Roughness in self.Surface_Roughnesslist:
                thmin=self.Surface_RoughnesslistDict[Surface_Roughness]
        
        
        #Unit Object Liquid Release Data
        t_release=UnitObject.OutFlowModelObject.t_release
        dMassLiquid_release=UnitObject.OutFlowModelObject.dMassLiquid_release
        TotalMassLiquid_Release=UnitObject.OutFlowModelObject.TotalMassLiquid_Release
        if TotalMassLiquid_Release==None or TotalMassLiquid_Release==[] or TotalMassLiquid_Release==[0]:
            warning(f'(LiquidSpread) for plant unit with tag={UnitObject.tag} is not calculated because its TotalMassLiquid_Release=None or 0 or []. The material tag={UnitObject.SubstanceTag} with name {SubstanceObject.name}.')
            return -1

        
        
        #Calculations Part1 : Liquid Spilling

        self.LiquidRadious=[]     # Radius of dispered Liquid in each moment
        self.LiquidCenter=[]      # Center of dispered Liquid in each moment   
        self.LiquidThickness=[]   # Thickness of spilled liquids        
        
  
        for i,t in enumerate(t_release):
            
            self.LiquidCenter.append((Xc,Yc))
            AreaR=TotalMassLiquid_Release[i]/thmin/Density     # Radius of dispered Liquid in each moment

            if Abund==0 or AreaR<=Abund:
                Radius=(AreaR/3.1415)**0.5
                self.LiquidRadious.append(Radius)
                self.LiquidThickness.append(thmin)
            else:
                Radius=(Abund/3.1415)**0.5
                self.LiquidRadious.append(Radius)
                self.LiquidThickness.append(TotalMassLiquid_Release[i]/Abund/Density)

                
        self.t_disp=t_release        
                
              
                      
        self.t_dispLiquidVaporization=[0]     
        self.LiquidVaporizationMassRate=[0]   
        self.LiquidVaporizationMass=[0]       
        self.GasExplosiveMass=[0]             
        self.GasExplosiveCenter=[0]     
        
        

        
        return 0
