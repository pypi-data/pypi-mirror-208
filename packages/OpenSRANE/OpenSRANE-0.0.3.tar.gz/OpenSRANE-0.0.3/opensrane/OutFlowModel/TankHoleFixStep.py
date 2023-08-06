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

class TankHoleFixStep(_NewClass,_GlobalParameters):
    
    '''
    OutFlow Model For Liquid Or Gas OutFlow From a Tank
    reference for Liquid Out Flow: Casal Evaluation of the Effects and Consequences of Major Accidents in Industrial Plants 2nd Wdition
    Page 29 Chapter 2
    
    '''
    Title='TankHoleFixStep'
    
    def __init__(self,tag,Hole_Diameter=0.01,Hole_Height_FromBot=0,delta_t=0.1, Cd=1, StepNumber=1000):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.Hole_Diameter=Hole_Diameter
        self.Hole_Height_FromBot=Hole_Height_FromBot
        self.delta_t=delta_t
        self.Cd=Cd                                   #The discharge coefficient
        self.StepNumber=StepNumber
        
        self.name=f'TankHoleFixStep with Diameter= {Hole_Diameter} and with Height(From Bot)= {Hole_Height_FromBot} and dt= {delta_t} and Cd= {Cd} '

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass

        
    def Calculate(self):
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        

        
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag]
        SiteObject=_opr.Sites.ObjManager.Objlst[0]
         
        
        Pout=SiteObject.Pressure        #OutSide Pressure
        Tout=SiteObject.Temperature      #OutSide Temperature
        
        Pin=UnitObject.Pressure         #Inside Pressure
        Tin=UnitObject.Temperature       #Inside Temperature
        
        d=UnitObject.d_Storage          #Tank Diameter

        StepNumber=self.StepNumber
        
        Vsubs=UnitObject.V_subs
        if Vsubs==None:
            warning (f'(TankHoleDuration outflow model) is not calculated for unit Object with tag {UnitObject.tag} because no dimension or Substance volume (V_subs) is defined for mentioned plant unit')
            return -1
            
        h=Vsubs/(_math.pi*d**2/4)      #Liquid Height in the Tank
        
        h=h-self.Hole_Height_FromBot   #Liquid Height from Hole level 
        dt=self.delta_t
        dh=self.Hole_Diameter
        
        
        #Constant Parameters
        Aor=_math.pi*dh**2/4
        Rho=SubstanceObject.Density
        Cd=self.Cd
        g=SiteObject.g
        At=_math.pi*d**2/4
        m0=At*h*Rho                     #Initial Mass of the Substance
        V0=At*h                         #Initial Volume of the Substance
        
        
        #Check Of Correct Condition
        if h<=0:    #The condition that Level of hole be higher than level of liquid or be equal
        
            warning(f'(TankHoleFixStep) For Plant Unit with tag={UnitObject.tag} OutFlow is not calculated Because h={Vsubs/(_math.pi*d**2/4)}<Hole_Height_FromBot={self.Hole_Height_FromBot} and results = [0]')
    
            t_release=[0]
            MassLiquidReleaseRate=[0]
            dMass_release=[0]
            TotalMass_Release=[0]
        
        elif Pin<=Pout-Rho*g*h:
            warning(f"Error: (TankHoleFixStep) in unit with tag:{UnitObject.tag} Internal Pressure is less than -Rho*g*h+Pout that cause negetive value under" +
                    f"square root inside TankHole out flow model formula for liquid " +
                    f"Pin-Pout={Pin-Pout} and -Rho*g*h={-1*Rho*g*h}")
            return -1
            
        else:
            #CalCulations
            t_release=[]
            MassLiquidReleaseRate=[]
            dMass_release=[]
            TotalMass_Release=[]
            
            t=0
            V=0
            mdot=0
            dm=0
            while V<=V0 and mdot>=0 and len(t_release)<=StepNumber:
                
                t_release.append(t)
                MassLiquidReleaseRate.append(mdot)
                dMass_release.append(dm)
                TotalMass_Release.append(V*Rho)
                
                t=t+dt
                tav=(t+(t-dt))/2
                mdot=Aor*Rho*Cd*_math.sqrt(2*((Pin-Pout)/Rho+g*h))-Rho*g*Cd**2*Aor**2/At*tav
                
                dm=mdot*dt
                dv=dm/Rho
                V=V+dv


            #if the maximum Volume has not been added to the results
            if V>V0 and TotalMass_Release[-1]<V0*Rho or mdot<0:

                mdot=Aor*Rho*Cd*_math.sqrt(2*((Pin-Pout)/Rho+g*h))-Rho*g*Cd**2*Aor**2/At*tav #(2.5)
                dm=V0*Rho-TotalMass_Release[-1]
                dt=dm/mdot
                t=t_release[-1]+dt
                mdot=Aor*Rho*Cd*_math.sqrt(2*((Pin-Pout)/Rho+g*h))-Rho*g*Cd**2*Aor**2/At*t #(2.5)
                dm=V0*Rho-TotalMass_Release[-1]
                dt=dm/mdot
                t=t_release[-1]+dt
                
                t_release.append(t)
                MassLiquidReleaseRate.append(mdot)
                dMass_release.append(dm)
                TotalMass_Release.append(V0*Rho)  
                
            
            self.t_release=t_release
            self.MassLiquidReleaseRate=MassLiquidReleaseRate
            self.dMassLiquid_release=dMass_release   
            self.TotalMassLiquid_Release=TotalMass_Release   
            
            self.MassGasReleaseRate=[0 for i in self.t_release]
            self.dMassGas_release=[0 for i in self.t_release]
            self.TotalMassGas_Release=[0 for i in self.t_release]  
            
        
        return 0
        
        