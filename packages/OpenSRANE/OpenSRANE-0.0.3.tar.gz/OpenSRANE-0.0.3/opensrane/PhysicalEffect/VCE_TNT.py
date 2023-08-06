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
from ._GlobalParameters import _GlobalParameters
from opensrane.Misc.WarningRecorder import *
import math as _math
import random as _rnd
import opensrane as _opr

class VCE_TNT(_NewClass,_GlobalParameters):
    
    '''
    In this class Vapour cloud Explosion (VCE) physical effect is modeled using TNT method
    Etta = Explosion Yield Factor That is between 1% to 10% and it is recommended to be considered equal to 3%
    '''
    Title='VCE TNT method'
    
    def __init__(self,tag, Etta=0.03):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.Etta=Etta

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
    @property
    def name(self):    
        return f'VCE TNT Physical Effect for unit with tag {self.UnitObject.tag} ' if self.UnitObject!=None else 'VCE TNT Physical Effect But still No Plant unit is assigned to it'
        

       
    def OverPressure_at_Point(self,x,y,z):
        #This function returns OverPressure value at point x,y,z
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(VCE_TNT) Because of no assigned plant unit will not do any calculations')
            return 0
        
        #Get Substance that is assigned to the unit Object
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        if SubstanceObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of No substance is defined for the mnetioned Plant unit Object')
            return 0 
        
        #Get Site Pressure
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag]
        if SiteObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of No site tag has been defined for metioned Plant unit Object, So the OverPressure is returned equal 0!')
            return None 
        P0=SiteObject.Pressure   #Site Pressure
        
        
        #Import Gas Dispersion Object
        DispersionObject=UnitObject.DispersionSpreadModelObject
        if DispersionObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of no DispersionObject (DispersionObject=None) is not calculated and OverPressure is returned equal 0!')
            return 0

        
        M=DispersionObject.GasExplosiveMass
        X=DispersionObject.GasExplosiveCenterX
        Y=DispersionObject.GasExplosiveCenterY
        Z=DispersionObject.GasExplosiveCenterZ
        
        
        if M==None or X==None or Y==None or Z==None :
            warning(f'(VCE_TNT) Because for Plant Unit with tag {UnitObject.tag} There GasExplosiveMass or GasExplosiveCenter for Dispersion is None and are not calculated' +
                    f' No VCE is Calculated and OverPressure is returned equal 0 \n' +
                    f'     CHECK does substance with tag {SubstanceObject.tag} is a gas material (if is not do not assign VCE for it) or check does a gas dispersion model assigned for this material')            
            return 0

        if max(M)==0 :
            warning(f'(VCE_TNT) Because for Plant Unit with tag {UnitObject.tag} There GasExplosiveMass for Dispersion is 0 and are not calculated' +
                    f' No VCE is Calculated and OverPressure is returned equal 0 \n' +
                    f'     CHECK does substance with tag {SubstanceObject.tag} is a gas material (if is not do not assign VCE for it) or check does a gas dispersion model assigned for this material')            
            return 0
            
        M0=max(M)        # Explosive Mass
        X=X[M.index(M0)] # Explosive Mass CenterX
        Y=Y[M.index(M0)] # Explosive Mass CenterX
        Z=Z[M.index(M0)] # Explosive Mass CenterX
        M=M0
        
        Etta=self.Etta
        HTNT=4680*1000   # J/kg Blast Energy of TNT per 1 kg
        
        Hc=SubstanceObject.Specific_Heat_of_Combustion #Heat of the combustion of the material
        if Hc==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of Heat of combustion of Material with tag {SubstanceObject.tag} has not been defined, So the OverPressure is not calculated and OverPressure is returned equal 0! ')
            return 0        
        
        WTNT=Etta*M*Hc/HTNT           # Casal Formula 4.7
        
        d=((x-X)**2+(y-Y)**2+(z-Z)**2)**0.5
        
        dn=d/WTNT**(1/3)              # Casal Formula 4.3
        
        DeltaP=P0*(1/dn+4/dn**2+12/dn**3) # Casal Formula 4.8
        
         
            
        return DeltaP

    def OverPressureBoundary(self,OverPressure, Height, PointNumber):
        
        #This function returns N PointNumber location that have equal OverPressure value at z=Height
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(VCE_TNT) Because of no assigned plant unit will not do any calculations')
            return 0
        
        #Get Substance that is assigned to the unit Object
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        if SubstanceObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of No substance is defined for the mnetioned Plant unit Object')
            return 0 
        
        #Get Site Pressure
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag]
        if SiteObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of No site tag has been defined for metioned Plant unit Object, So the OverPressure is returned equal 0!')
            return None 
        P0=SiteObject.Pressure   #Site Pressure
        
        
        #Import Gas Dispersion Object
        DispersionObject=UnitObject.DispersionSpreadModelObject
        if DispersionObject==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of no DispersionObject (DispersionObject=None) is not calculated and OverPressure is returned equal 0!')
            return 0

        
        M=DispersionObject.GasExplosiveMass
        X=DispersionObject.GasExplosiveCenterX
        Y=DispersionObject.GasExplosiveCenterY
        Z=DispersionObject.GasExplosiveCenterZ
        
        
        if M==None or X==None or Y==None or Z==None :
            warning(f'(VCE_TNT) Because for Plant Unit with tag {UnitObject.tag} There GasExplosiveMass or GasExplosiveCenter for Dispersion is None and are not calculated' +
                    f' No VCE is Calculated and OverPressure is returned equal 0 \n' +
                    f'     CHECK does substance with tag {SubstanceObject.tag} is a gas material (if is not do not assign VCE for it) or check does a gas dispersion model assigned for this material')            
            return 0
            
        M0=max(M)        # Explosive Mass
        X=X[M.index(M0)] # Explosive Mass CenterX
        Y=Y[M.index(M0)] # Explosive Mass CenterX
        Z=Z[M.index(M0)] # Explosive Mass CenterX
        M=M0
 

        #Solve equation Casal 4.8 for dn to find dn
        DeltaP=OverPressure
        
        D=DeltaP/P0
        a=-1/D
        b=-4/D
        c=-12/D
        
        p=b-a**2/3
        q=2*a**3/27-a*b/3+c 
        
        Delta=q**2/4+p**3/27
        
        if Delta>0:
            dn=(-q/2+Delta**0.5)**(1/3)+(-q/2-Delta**0.5)**(1/3)-a/3
        
        elif Delta==0:
            dn=[]
            
            dn1=-2*(q/2)**(1/3)-a/3
            dn2=(q/2)**(1/3)-a/3
            
            if dn1>0: dn.append(dn1)
            if dn2>0: dn.append(dn2)
            
            if dn==[]: return 0
            
            dn=min(dn)
                    
        else:
            dn=[]
            
            dn1=2/3**0.5*(-p)**0.5*_math.sin(1/3*_math.asin(3*3**.5*q/2/((-p)**0.5)**3))-a/3
            dn1=0 if type(dn1)==complex else dn1
            if dn1>0: dn.append(dn1)
            
            dn2=-2/3**0.5*(-p)**0.5*_math.sin(1/3*_math.asin(3*3**.5*q/2/((-p)**0.5)**3)+_math.pi/3)-a/3
            dn2=0 if type(dn2)==complex else dn2
            if dn2>0: dn.append(dn2)

            dn3=2/3**0.5*(-p)**0.5*_math.cos(1/3*_math.asin(3*3**.5*q/2/((-p)**0.5)**3)+_math.pi/6)-a/3
            dn3=0 if type(dn3)==complex else dn3
            if dn3>0: dn.append(dn3)            

            if dn==[]: return 0
            
            dn=min(dn)
            
        #continue calculations             
        
        Etta=self.Etta
        HTNT=4680*1000   # J/kg Blast Energy of TNT per 1 kg
        
        Hc=SubstanceObject.Specific_Heat_of_Combustion #Heat of the combustion of the material
        if Hc==None:
            warning(f'(VCE_TNT) for Plant unit {UnitObject.tag} because of Heat of combustion of Material with tag {SubstanceObject.tag} has not been defined, So the OverPressure is not calculated and OverPressure is returned equal 0! ')
            return 0        
        
        
        WTNT=Etta*M*Hc/HTNT           # Casal Formula 4.7
        
        d=dn*WTNT**(1/3)              # Casal Formula 4.3
        
        R=d                           #Overpressure radious    
        dz=abs(Z-Height)              #Desire level respect to the explosion center  
        if dz>=R: return 0
        HR=(R**2-dz**2)**0.5         #Horizontal radious  
        
        Phi=[2*_math.pi/PointNumber*i for i in range(PointNumber)]
        
        
        Resluts={} #Dictionary that sotres data
        
        for phi in Phi:
        
            x=X+HR*_math.cos(phi)
            y=Y+HR*_math.sin(phi)
            Resluts[phi]=(x,y)
        
        
        
        return Resluts