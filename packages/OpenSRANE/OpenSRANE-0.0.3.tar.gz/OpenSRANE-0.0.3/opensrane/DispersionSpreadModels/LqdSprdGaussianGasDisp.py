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
from opensrane.Misc.WarningRecorder import *
from .ObjManager import *
from ._GlobalParameters import _GlobalParameters
import math as _math
import opensrane as _opr
import numpy as _np
import itertools as _it

class LqdSprdGaussianGasDisp(_NewClass,_GlobalParameters):
    
    '''
    Dispersion model for Liquids According CasCal
    IMPORTANT ATTENTION: it is really important to remember that
    Before using this Object, self.UnitObject should be assigned and shouldn't be empty
    
    '''
    Title='LqdSprdGaussianGasDisp'

    
    def __init__(self,tag, MatTags, OutFlowModelTags,MinDisThickness=0.01,Surface_Roughnesslist=[0.0001,0.0002],Surface_RoughnessThickness=[0.005,0.01],
                     Vaporization_Delta_t=10,TotalDuration=30*60,GasConstant=8.31446261815324,GasDispersionXSegments=10,
                     GasDisperstionErrorPercent=1):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        _GlobalParameters.__init__(self,MatTags, OutFlowModelTags)
        
                
        if MinDisThickness==None or MinDisThickness<=0:
            self.MinDisThickness=0.005
        else:
            self.MinDisThickness=MinDisThickness
            
        if len(Surface_Roughnesslist)>len(Surface_RoughnessThickness):
            Surface_RoughnessThickness.extend([MinDisThickness]*(len(Surface_Roughnesslist)-len(Surface_RoughnessThickness)))
        
        self.Surface_Roughnesslist=Surface_Roughnesslist
        self.Surface_RoughnessThickness=Surface_RoughnessThickness
        
        #Dictionary that stores the surface roughness values and their corresponding stiffness                
        self.Surface_RoughnesslistDict={Rough:Thick for Rough,Thick in zip(Surface_Roughnesslist,Surface_RoughnessThickness)}
        
        self.name=f'{self.Title} with minimum thickness equal to {self.MinDisThickness}'

        self.Vaporization_Delta_t=Vaporization_Delta_t
        self.GasConstant=GasConstant
        self.TotalDuration=TotalDuration
        self.GasDispersionXSegments=GasDispersionXSegments
        self.GasDisperstionErrorPercent=GasDisperstionErrorPercent

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        
        # Wind and Dispersion parameters
        self._WeatherCateGory=None
        self._windSpeed=None
        self._a=None
        self._b=None
        self._c=None
        self._d=None
        
        
        
    def Calculate(self):
    
       
        # print('start of calculation')
        UnitObject=self.UnitObject    #self.UnitObject is defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #Import required objects
        DikeObj= _opr.Safety.ObjManager[UnitObject.DikeTag] if UnitObject.DikeTag!=None else None
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag] if UnitObject.SiteTag!=None else None
        

        #Calculate Minimum Thickness
        thmin=self.MinDisThickness
        Surface_Roughness=UnitObject.Surface_Roughness
        if Surface_Roughness!=None:
            if Surface_Roughness in self.Surface_Roughnesslist:
                thmin=self.Surface_RoughnesslistDict[Surface_Roughness]         

        #####Importing Data####
        Density=SubstanceObject.Density
        LFL=SubstanceObject.Lower_Flammability_Limit
        UFL=SubstanceObject.Upper_Flammability_Limit
        
        
        ##Object Inside and Outside Data
        Xc=UnitObject.Hlocalcoord #Unit Horizontal Local center Coordinate
        Yc=UnitObject.Vlocalcoord #Unit Vertical Local center Coordinate
        
        
        #Dike Data
        Abund, HBund, Vbund=(DikeObj.Area , DikeObj.Height, DikeObj.Volume) if DikeObj!=None else (0, 0, 0)   #taking Dike Data Area, height, volume
        Surface_Roughness=UnitObject.Surface_Roughness
        
        
        
        #Unit Object Liquid Release Data
        t_release=UnitObject.OutFlowModelObject.t_release
        dMassLiquid_release=UnitObject.OutFlowModelObject.dMassLiquid_release
        TotalMassLiquid_Release=UnitObject.OutFlowModelObject.TotalMassLiquid_Release

        if TotalMassLiquid_Release==None or TotalMassLiquid_Release==[] or TotalMassLiquid_Release==[0]:
            warning(f'(LqdSprdGaussianGasDisp) for plant unit with tag={UnitObject.tag} is not calculated because its TotalMassLiquid_Release=None or 0 or []. The material tag={UnitObject.SubstanceTag} with name {SubstanceObject.name}.')
            return None
        
        
        #Calculations Part1 : Liquid Spread

        self.LiquidRadious=[]     # Radius of dispered Liquid in each moment
        self.LiquidCenter=[]      # Center of dispered Liquid in each moment   
        self.LiquidThickness=[]   # Thickness of spilled liquids        
        
        # print(11)        
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
                
 
 #Calculationspart 2: liquid evaporation if we want to consider--------------------------------------
        #Calculation are according Casal Book part 2.7.3:
        
        
        Ts=UnitObject.GroundTemperature                       #Ground Temperature
        Tpool=UnitObject.Temperature                          #Temperature of the Liquid in the plant unit considered as the Temperature of the liquid in the pool
        Apool=[3.1415*R**2 for R in self.LiquidRadious]       #List of pool Area in each time moment
        Tboil=SubstanceObject.Boiling_Point                   #Boiling_Point of the substance
        Mv=SubstanceObject.Molecular_Weight
        R=self.GasConstant
        DeltaHv=SubstanceObject.Specific_Heat_of_Vaporization #latent heat of vaporization or Specific Heat of Vaporization
        Ks=UnitObject.Ks_Soil_Thermal_conductivity            #Ks 
        AlphaS=UnitObject.Alphas_Soil_thermal_diffusivity     #Alphas
        T0=SiteObject.Temperature                             #Atmosphere Temperature
        P0=SiteObject.Pressure                                #Atmosphere Pressure
        dt=self.Vaporization_Delta_t                          #Vaporization Calculation Time distance
        TD=self.TotalDuration                                 #Total Duration of Release
        Pamb=SubstanceObject.Liquid_Partial_Pressure_in_Atmosphere   #Liquid_Partial_Pressure_in_Atmosphere of the substance
        WindSpeed=_opr.WindData.ObjManager.Objlst[0].WindSpeed
        Pv=SubstanceObject.Vapour_Pressure
        # print(WindSpeed)
        
        #Checking Part to improve robustness
        if WindSpeed==None:
            warning(f'(LqdSprdGaussianGasDisp Model) No wind Sample has been created yet! So No Concentration and so no Dispersion calculated'+
                    f' for Plant unit {UnitObject.tag} with substance tag={SubstanceObject.tag} and name={SubstanceObject.name}')
            return None
        if WindSpeed==0: WindSpeed=0.01
        uw=WindSpeed

        if LFL==None or UFL==None:
            warning(f'(LqdSprdGaussianGasDisp Model) LFL or UFL for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model (LqdSprdGaussianGasDisp) will not calculate')
            return None 
            
        if DeltaHv==None:
            warning(f'(LqdSprdGaussianGasDisp Model) Specific_Heat_of_Vaporization for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model (LqdSprdGaussianGasDisp) will not calculate')
            return None 
            
        if Pv==None:
            warning(f'(LqdSprdGaussianGasDisp Model) Vapour_Pressure for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model (LqdSprdGaussianGasDisp) will not calculate')
            return None
            
        if Mv==None:
            warning(f'(LqdSprdGaussianGasDisp Model) Molecular_Weight for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model (LqdSprdGaussianGasDisp) will not calculate')
            return None 
        
        if Tboil==None:
            warning(f'(LqdSprdGaussianGasDisp Model) Boiling_Point for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model it is imagined that Substance is in NoneBoiling Condition')
                  
        if Pamb==None:
            warning(f'(LqdSprdGaussianGasDisp Model) Liquid_Partial_Pressure_in_Atmosphere for substance with tag={SubstanceObject.tag} and name={SubstanceObject.name} is not defined'+
                  f'So for Plant Unit with tag={UnitObject.tag} Pool vaporization model it is imagined that Liquid_Partial_Pressure_in_Atmosphere=0')
            Pamb=0  


        if TotalMassLiquid_Release==None or TotalMassLiquid_Release==[] or max(TotalMassLiquid_Release)==0: #means there is no OutFlow
            return None
        
        # print(f'\n\n**************(LqdSprdGaussianGasDisp Model) ************************** for Plant unit {UnitObject.tag} with substance tag={SubstanceObject.tag} and name={SubstanceObject.name}')        
        # print('\nTotal mass released=',max(TotalMassLiquid_Release)) 
        # print(f'Substance name={SubstanceObject.name} and its Specific_Heat_of_Vaporization={SubstanceObject.Specific_Heat_of_Vaporization}')

        #Calculations Part :
        Ap=max(Apool)
        rp=max(self.LiquidRadious)
        TM=max(TotalMassLiquid_Release)  #Total Mass Released
        

        # print(12)
        if Tboil==None or (Tboil>T0 and Tpool<Tboil):
            #NonBoiling Evaporation case
            md=2*10**(-3)*uw**0.78*rp**(-0.11)*Mv*P0/R/T0*_math.log(1+(Pv-Pamb)/(P0-Pv))*Ap #Equation 2.56
            
            TDuration=TM/md
            if TDuration<TD:
                TDuration=TD
            
            t=[0, TDuration] 

            #list of Evaporation mass rate
            md=[0, md]
            
            #Total Evaporated Mass Calculation:
            MT=[0, TM]
        
        else:
            #Boiling Evaporation Case
            #Select Proper dt:
            
            # print('(LqdSprdGaussianGasDisp) Boiling Evaporation Case (Select Proper dt:) part')
            
            Mt=2*TM
            dt=2*dt
            while Mt>=TM:

                t=dt/2
                dt=dt/2
                md=Ks*(Ts-Tpool)*Ap/(3.1415*AlphaS*t)**0.5/DeltaHv     #equation 2.54 and 2.55 
                Mt=md*dt
            
            #Do main Calculations
            t=[]
            md=[]
            MT=[]  
            tt=0
            mdd=0
            Mtt=0
            
            # print('(LqdSprdGaussianGasDisp) Boiling Evaporation Case (Do main Calculations) part')

            while Mtt<=TM and tt<TD:

                t.append(tt)       #time steps of evaporation
                md.append(mdd)     #mass evaporation rate at each step
                MT.append(Mtt)     #Comulitative or Total Evaporated mass at each step
                
                tt=tt+dt           #time at next step
                mdd=Ks*(Ts-Tpool)*Ap/(3.1415*AlphaS*tt)**0.5/DeltaHv   #Evaporation Rate at next step
                Mtt=Mtt+mdd*dt     #Comulitative or Total evaporated mass at next step                                
                # print(Mtt,TM)

                
            if max(MT)<TM and tt<TD:         #To consider total release if not considered
                #Make an Hypothesis: mdd is equal to the last md
                Mtt=TM-max(MT)
                mdd=md[-1]
                dt=Mtt/mdd
                
                md.append(mdd)
                t.append(t[-1]+dt)
                MT.append(TM)
                
            
        
        self.t_dispLiquidVaporization=t
        self.LiquidVaporizationMassRate=md
        self.LiquidVaporizationMass=MT
        
          
        
        
        # print(13)
        #Calculationspart 3: Gas Dispersion in Environment
        
        #First wind Data should be load to be used in the other functions
        self._loadWindData()

        #Calculate Pool Evaporated Gas Dispersion points
        _,_,_,_,xpoints,_,zpoints,Dx,Dy,Dz,Concentrations=self._GasPoints(LFL,UFL,SegmentNumbers=self.GasDispersionXSegments,errpercent=self.GasDisperstionErrorPercent)

        #Calculate Mass of the Dispersed Gas and its Center
        Mass,CenterOfMass=self._MassCMass(Dx,Dy,Dz,xpoints,zpoints,Concentrations)
        

        #Convert Center of mass to global coordinate
        X,Y=self._convertBackdirection(CenterOfMass[0],0) #Becauls of the symetry of the current dispesion model CenterMass Y is always equal to 0
        X=X+Xc
        Y=Y+Yc
        # print(134)
        
        
        self.GasExplosiveMass=[Mass]                        # Gas mass list that is in the range of explosion (between LFL and UFL) for each instant of the time list
        self.GasExplosiveCenterX=[X]                        # list of x of A Point that specify the location of the explosive mass
        self.GasExplosiveCenterY=[Y]                        # list of y of A Point that specify the location of the explosive mass
        self.GasExplosiveCenterZ=[CenterOfMass[2]]          # list of z of A Point that specify the location of the explosive mass
              

        # print(14)
        return 1


    def _loadWindData(self):
        #This function just load required wind DATA
        #Get Wind Data
        u=_opr.WindData.ObjManager.Objlst[0].WindSpeed
        if u==None:
            warning(f'(LqdSprdGaussianGasDisp) in _loadWindData function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None
        if u==0: u=0.01
        self._windSpeed=u
        
        WeatherCateGory=_opr.WindData.ObjManager.Objlst[0].WindClass
        if WeatherCateGory==None: WeatherCateGory='F'   
        self._WeatherCateGory=WeatherCateGory

        #Calculate dispersion Coefficient (abcd)
        if WeatherCateGory=='A':
            a=0.527
            b=0.856
            c=0.28
            d=0.9
        elif WeatherCateGory=='B':
            a=0.371
            b=0.866
            c=0.23
            d=0.85
        elif WeatherCateGory=='C':
            a=0.209
            b=0.897
            c=0.22
            d=0.8
        elif WeatherCateGory=='D':
            a=0.128
            b=0.905
            c=0.2
            d=0.76            
        elif WeatherCateGory=='E':
            a=0.098
            b=0.902
            c=0.15
            d=0.73
        elif WeatherCateGory=='F':
            a=0.065
            b=0.902
            c=0.12
            d=0.67
        else:
            warning(f'(LqdSprdGaussianGasDisp) in LoadWindData function for Plant Unit with tag {UnitObject.tag}  \n  The Weather Condition if {WeatherCateGory}!!! and is not equal to ABCDEF so the requires values are considered as average of the values ')
            a=0.15
            b=0.87
            c=0.18
            d=0.7            
        
        #Store values for other usages
        self._a=a
        self._b=b
        self._c=c
        self._d=d

        return 0

 
    def GasConcentration(self,x,y,z):
        '''
        This function returns the value of concentration at point x,y,z According V.J.Clancey, “The evaporation and dispersion of flammable liquid spillages”,
        Chemical Process Hazards, Vol.5, p.80, 1974
        
        ***
        ATTENTION: Any CHANOGE in this method should be implemented in two other _LocalGasConcentration and _LocalGasConcentrationList methods
        ***
        
        '''
        
        #Get Unit Object
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #Get the Pool center location (Considered as the location of gas dispersion)
        [Xc,Yc]=self.LiquidCenter[-1]
        
        #according the direction of the sample wind the the point location along the wind direction respect to the center of unit
        [x,y]=self._convertdirection(x-Xc,y-Yc)
        
        #Now that points has changes to the local coordinate(means that considering wind blast direction from left to right and point is rotated) and point has converted to local point, so the remain calculations can be done by _LocalGasConcentration method
        C=self._LocalGasConcentration(x,y,z)

    
        return C

    def _LocalGasConcentration(self,xl,yl,zl):
        '''
        This function returns the value of concentration at point x,y,z According V.J.Clancey, “The evaporation and dispersion of flammable liquid spillages”,
        Chemical Process Hazards, Vol.5, p.80, 1974
        
        BUT THIS FUNCTION WORks ACCORDING TO THE LOCAL POINTS. MEANS THAT THE LOCAL OF THE POINTS ARE RESPECT TO THE CENTER OF THE GAS EVAPORATION POINT 
        MEANS GAS POOL CENTER and Wind is considered that blasts from left to the right
        
        
        ***
        ATTENTION: Any CHANOGE in this method should be implemented in two other _LocalGasConcentration and _LocalGasConcentrationList methods
        ***
        
        '''
        
        #Get Unit Object
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        
        #according the direction of the sample wind the the point location along the wind direction respect to the center of unit
        x,y,z=xl,yl,zl
        
        #Load Wind Data
        #If wind data has not been loaded it should be load here
        if self._a==None: self._loadWindData()
        
        #Get wind data
        u=self._windSpeed
        WeatherCateGory=self._WeatherCateGory
        
        if u==None:
            
            warning(f'(LqdSprdGaussianGasDisp) in _LocalGasConcentration function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None
       
        
        # Pool Height Calculation (h) (is height above ground level)
        if UnitObject.DikeTag==None:
            h=0
        else:
            h=UnitObject.V_subs/(max(self.LiquidRadious)**2*3.1415)
        
        
        #Convert Type of m from numpy.float to float
        m=float(max(self.LiquidVaporizationMassRate))
        
        a=self._a
        b=self._b
        c=self._c
        d=self._d
        
        
        Sigmay=2*a*x**b
        Sigmaz=c*x**d

        if x>0:
            P1=m/(2*3.1415*u*Sigmay*Sigmaz)
            P2=_math.e**(-1*y**2/2/Sigmay**2)
            P3=_math.e**(-(z-h)**2/2/Sigmaz**2)+_math.e**(-(z+h)**2/2/Sigmaz**2)
            C=(P1*P2*P3)
            
        else:
            C=0
            
        if type(C)==complex:
            C=0
    
        return C

    def _LocalGasConcentrationList(self,LocalPointsList):
        '''
        This function is same _LocalGasConcentration but for a list of the points and it returns the list of the
        Gas concentrations in the numpy array format.
        This Funtion is usefull for boundary calculations and the mass and ...
        
        
        ***
        ATTENTION: Any CHANOGE in this method should be implemented in two other _LocalGasConcentration and _LocalGasConcentrationList methods
        ***
        
        '''
        
        #Get Unit Object
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #according the direction of the sample wind the the point location along the wind direction respect to the center of unit
        xnp=_np.array([p[0] for p in LocalPointsList])
        ynp=_np.array([p[1] for p in LocalPointsList])
        znp=_np.array([p[2] for p in LocalPointsList])
        
        
        #Load Wind Data
        #If wind data has not been loaded it should be load here
        if self._a==None: self._loadWindData()
        
        #Get wind data
        u=self._windSpeed
        WeatherCateGory=self._WeatherCateGory
        
        if u==None:
            
            warning(f'(LqdSprdGaussianGasDisp) in _LocalGasConcentrationList function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None
        
        # Pool Height Calculation (h) (is height above ground level)
        if UnitObject.DikeTag==None:
            h=0
        else:
            h=UnitObject.V_subs/(max(self.LiquidRadious)**2*3.1415)
        
        
        #Convert Type of m from numpy.float to float
        m=float(max(self.LiquidVaporizationMassRate))
        
        #Get dispersion Coefficient (abcd)
        a=self._a
        b=self._b
        c=self._c
        d=self._d          
        
        
        
        Sigmay=2*a*xnp**b
        Sigmaz=c*xnp**d
        # Sigmay=[2*a*x[0]**b for x in points] 
        # Sigmaz=[c*x[0]**d for x in points]

        
        C=m/(2*3.1415*u*Sigmay*Sigmaz)* \
        _math.e**(-1*ynp**2/2/Sigmay**2)* \
        (_math.e**(-(znp-h)**2/2/Sigmaz**2)+_math.e**(-(znp+h)**2/2/Sigmaz**2))
        
        # if x!=0:
            # P1=m/(2*3.1415*u*Sigmay*Sigmaz)
            # P2=_math.e**(-1*y**2/2/Sigmay**2)
            # P3=_math.e**(-(z-h)**2/2/Sigmaz**2)+_math.e**(-(z+h)**2/2/Sigmaz**2)
            # C=(P1*P2*P3)
            
        # else:
            # C=0
            
        # if type(C)==complex:
            # C=0

        return C
            
        
    def GiveBoundary(self,C,z=None,SegmentNumbers=20,errpercent=1):
        
        #This Function Should returns the boundary space that have concentration equal to C
        #Obviously for any different model the outpout can be differ
        
        #Get Unit Object
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #Get the Pool center location (Considered as the location of gas dispersion)
        [Xc,Yc]=self.LiquidCenter[-1]      
        
        # For this Clancy Method it needs the z level and if the user do not enter the z level it is considered equal to h
        # That h is the initial level of liquid pool
        
        if z==None: z=0
        x,_=self._CenterLine(LFL=C,SegmentNumbers=2,errpercent=errpercent)

        #Load Wind data
        #If wind data has not been loaded it should be load here
        if self._a==None: self._loadWindData()
               
        
        y=[round(self._FindY(xx,z0=z,dy=1,LFL=C),5) for xx in x]
        
        #if there were no concentration equal to the LFL or C the function return None
        if max(y)==0: return [(0,0)]
        #Eliminating the y values that are 0 then devide the rest of the points to the segmentnumbers
        for i in range(2):
            yy=[v for v in y if v!=0]
            xx=[i for i,v in zip(x,y) if v!=0]

            xmin=x[x.index(min(xx))-1] if x.index(min(xx))!=0 else x[0]
            xmax=x[x.index(max(xx))+1] if x.index(max(xx))!=len(x)-1 else x[-1]
            
            
            dx=(xmax-xmin)/SegmentNumbers
            x=[xmin+i*dx for i in range(SegmentNumbers+1)]
            
            y=[round(self._FindY(xx,z0=z,dy=1,LFL=C),5) for xx in x]
        

        #Convert points to global coordinate
        points=[]

        [points.append(self._convertBackdirection(xx,yy)) for xx,yy in zip(x,y)]
        [points.append(self._convertBackdirection(xx,-yy)) for xx,yy in zip(x[::-1],y[::-1])]
        # print('xc,yc=',xc,yc)
        points=[(Xc+p[0],Yc+p[1]) for p in points]
        
        return points
        
        
    def _FindXCMax(self,dx=0.01,z=0.0):
        
        # This function Returns a point along x axis that has maximum concentration in the level equal to z (y=0)
        
        x0=0
        x=x0+dx
        
        cx0=self._LocalGasConcentration(x0,0,z)
        cx=self._LocalGasConcentration(x,0,z)
        
        while cx>=cx0:
            cx0=cx
            x0=x
            x=x0+dx
            cx=self._LocalGasConcentration(x,0,z)
            

        return x0
    def _FindZCmax(self,x=0.5,z0=0, dz=0.01):
    
        # this function returns maximum concentration along z axis in a specific x (y=0)
    
        
        z=z0+dz
        
        cz0=self._LocalGasConcentration(x,0,z0)
        cz=self._LocalGasConcentration(x,0,z)
        if cz<cz0:
            dz=-dz
            z=z0+dz
            cz0=self._LocalGasConcentration(x,0,z0)
            cz=self._LocalGasConcentration(x,0,z)
        
        while cz>=cz0 and z>=0:
            cz0=cz
            z0=z
            z=z0+dz
            cz=self._LocalGasConcentration(x,0,z)

                
        return z0
    def _FindZXCMax(self,dx=0.01,dz=0.01,err=0.01):
    
        ##This Function renutns the maximum Concentration point location of the plume
        # z0=0
        # x0=0
        
        # x=dx if dx>err else err*2
        # z=dz if dz>err else err*2
            
        # while (abs(x-x0)>err or abs(z-z0)>err):
            
            # x0=x
            # z0=z
            # x=self._FindXCMax(dx=dx, z=z)
            # z=self._FindZCmax(x=x, dz=dz)
            
            # print('dx=',x-x0,'dz=',z-z0,end='  ')
        
        # print('x,z,h=',x,z,h)
        
        #By Checking above calculations it is seen that Mostly the maximum Concentration is located in approximately dx and h 
        # Pool Height Calculation (h) (is height above ground level)
        if self.UnitObject.DikeTag==None:
            h=0
        else:
            h=self.UnitObject.V_subs/(max(self.LiquidRadious)**2*3.1415)
            
        x,z= dx,h
        
        return x,z
        
    def _CenterLine(self,LFL,SegmentNumbers=10,errpercent=1):
                
        # This function returns the center line of the plume untill the LFL
        # SegmentNumbers: The plume is diveded to SegmentNumbers segments along wind direction (Xaxis)
        # LFL: Concentration of last point
        # errpercent: Precentage of the error 
        # print(13111)
        x0,z0=self._FindZXCMax() #Location of the maximum concentration of the plume
        # print(13112)
        c0=self._LocalGasConcentration(x0,0,z0)
        # print(13113)
        xcmax=x0
        
        if c0<=LFL:
            return [0], [0]
        
        # Find Second point for interpolation 
        x1=2*x0
        z1=self._FindZCmax(x=x1,z0=z0)
        c1=self._LocalGasConcentration(x1,0,z1)
        # print(13114)
        
        x=self._interp(c0,x0,c1,x1,LFL)
        z=self._FindZCmax(x=x,z0=z1)
        c=self._LocalGasConcentration(x,0,z)
        # print(13115)
        #Find the LFL Location
        # print(1)
        while abs(c-LFL)/LFL>errpercent/100:
            
            if c0<LFL and c1<LFL:
                if c1>c0:
                    c0,x0=c,x
                else:
                    c1,x1=c,x
            elif c1>LFL and c0>LFL:
                if c1<c0:
                    c0,x0=c,x
                else:
                    c1,x1=c,x
            else:
                if abs(c1-LFL)<abs(c0-LFL):
                    c0,x0=c,x
                else:
                    c1,x1=c,x
             
            
            x=self._interp(c0,x0,c1,x1,LFL)
            z=self._FindZCmax(x=x,z0=z)
            c=self._LocalGasConcentration(x,0,z)
        # print(2)
        
        xcmin=x
        
        dx=abs(xcmax-xcmin)/SegmentNumbers
        
        
        x=[dx-(SegmentNumbers/2-i)/(SegmentNumbers/2)*dx for i in range(1,SegmentNumbers+2)]
        x=[xcmax+sum(x[0:i]) for i in range(len(x))]
        # print(21)

        z=[]
        for xx in x:
          z.append(self._FindZCmax(x=xx,z0=z0))
          z0=z[-1]
        # z=[self._FindZCmax(x=xx) for xx in x ]
        # print(3)
        
        
        return x,z    
    
    def _FindZtop(self,x,z0,dz,LFL):
        # This Function for any entered x finds the maximum Z the is not less than LFL
        #z0: intial z value
        
        z=z0
        while self._LocalGasConcentration(x,0,z)>=LFL:
            z0=z
            z=z+dz
            
        return z0
        
    def _FindY(self,x,z0,dy,LFL):
        # This Function for any entered x finds the maximum y the is not less than LFL in entered z0 level
        # z0: interested level

        #Get Unit Object
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'        
        
        #Load Wind data
        #If wind data has not been loaded it should be load here
        if self._a==None: self._loadWindData()
        
        #if Wind data is not loaded or is not available
        if self._a==None:
            warning(f'(LqdSprdGaussianGasDisp) in _FindZtop function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None        

        #Get wind data
        u=self._windSpeed
        WeatherCateGory=self._WeatherCateGory
        
        if u==None:
            
            warning(f'(LqdSprdGaussianGasDisp) in _FindZtop function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None
    
        # Pool Height Calculation (h) (is height above ground level)
        if UnitObject.DikeTag==None:
            h=0
        else:
            h=UnitObject.V_subs/(max(self.LiquidRadious)**2*3.1415)
        
        
        #Convert Type of m from numpy.float to float
        m=float(max(self.LiquidVaporizationMassRate))
        
        
        a=self._a
        b=self._b
        c=self._c
        d=self._d
        
        
        Sigmay=2*a*x**b
        Sigmaz=c*x**d
        
        z=z0
        C=LFL
        
        P1=m/(2*3.1415*u*Sigmay*Sigmaz)
        P3=_math.e**(-(z-h)**2/2/Sigmaz**2)+_math.e**(-(z+h)**2/2/Sigmaz**2)        

        #Simple Analytical Solution
        try:
            y2=-1*2*Sigmay**2*_math.log(C/P1/P3)
            
            y=(y2)**0.5 if y2>=0 else 0
            
        except:
            y=0

            

        return y
    
    def _GasPoints(self,LFL,UFL,SegmentNumbers=10,errpercent=1):
        #This function returns the Gas disperesed Points in the space and also returns the Concentration of each point
        
        #Calculate the center line of the disperesed gas
        # print(1311)
        x,z=self._CenterLine(LFL,SegmentNumbers=SegmentNumbers,errpercent=errpercent)
        # print(1312)
        
        #If C0<LFL _CenterLine returns [0] that means there is no center line so the code send [0] for parameters
        if x==[0]:
            return x,z,[0],[0],[0],[0],[0],[0],[0],[0],[0]
        
        #Load Wind data
        #If wind data has not been loaded it should be load here
        if self._a==None: self._loadWindData()
        
        #if Wind data is not loaded or is not available
        if self._a==None:
            warning(f'(LqdSprdGaussianGasDisp) in _GasPoints function for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return None
        
        a=self._a
        b=self._b
        c=self._c
        d=self._d
        
        # Sigmay=2*a*x**b
        # Sigmaz=c*x**d        
        
        dx=[i-j for i,j in zip(x[1:],x[:-1])]
        dy=[2*a*xx**b/5 for xx in x[:-1]]     #Distance of points are considered equal to 1/5 of its standard deviation
        dz=[c*xx**d/5   for xx in x[:-1]]     #Distance of points are considered equal to 1/5 of its standard deviation
        # print(1313)        
        
        #Find the maxximum z of each point on center line
        zt=[self._FindZtop(X,z0,dz=dZ,LFL=LFL) for X,z0,dZ in zip(x,z,dz)] #Find Maximum Z in each central point
        # print(1314)
        #Find the limitation of y axis of each point that has concentration greater than the LFL
        yl=[self._FindY(X,z0,dy=dY,LFL=LFL) for X,z0,dY in zip(x,z,dy)] #Find Maximum y in each central point
        # print(1315)

        #Create Points and Their Concentrations
        points=[]
        Dx=[]
        Dy=[]
        Dz=[]
        
        for i in range(len(dx)):

            # Each Center line points range
            xrange=[x[i]]
            zrange=[k*dz[i] for k in range(round((zt[i])/dz[i]+1))]
            y=round((yl[i])/dy[i]+1)
            yrange=[k*dy[i] for k in range(-y,y)]
            
            
            # Generate each point dx and dy and dz value
            cnt=[0 for p in _it.product(xrange,yrange,zrange)]
            Dx.extend([dx[i] for p in cnt])
            Dy.extend([dy[i] for p in cnt])
            Dz.extend([dz[i] for p in cnt])     
            
            
            points.extend(_it.product(xrange,yrange,zrange))

        # print(1316)
        #Calculate Concentration for each point
        Conc=self._LocalGasConcentrationList(points)
        # print(1317)
        #convert data to numpy format
        Dx=_np.array(Dx)
        Dy=_np.array(Dy)
        Dz=_np.array(Dz)
        
        xpoints=_np.array([p[0] for p in points])
        ypoints=_np.array([p[1] for p in points])
        zpoints=_np.array([p[2] for p in points])
        
        #Filter data out of the LFL UFL Range
        xpoints=xpoints[(Conc>=LFL)&(Conc<=UFL)]
        ypoints=ypoints[(Conc>=LFL)&(Conc<=UFL)]
        zpoints=zpoints[(Conc>=LFL)&(Conc<=UFL)]

        Dx=Dx[(Conc>=LFL)&(Conc<=UFL)]
        Dy=Dy[(Conc>=LFL)&(Conc<=UFL)]
        Dz=Dz[(Conc>=LFL)&(Conc<=UFL)]

        Conc=Conc[(Conc>=LFL)&(Conc<=UFL)]
                
        return x,z,zt,yl,xpoints,ypoints,zpoints,Dx,Dy,Dz,Conc
        
    def _MassCMass(self,Dx,Dy,Dz,xpoints,zpoints,Concentrations):
        # This function  claculate the mass and Center of the mass of given points and their concentrations
        # Points are considered in wind direction along x axis

        if Dx[0]==0 and len(Dx)==1: # if C0<LFL and there is no flamable gas for explosion
            return 0,(0,0,0)
            
        Mass=0
        MassX=0
        MassZ=0
        
        V=0
        
        
        for i in range(len(xpoints)):
            
            dx,dy,dz=Dx[i],Dy[i],Dz[i]
            dv=dx*dy*dz
            
            x=xpoints[i]
            z=zpoints[i]
            
            V=V+dv
            dm=dv*Concentrations[i]
            Mass=Mass+dm
            
            MassX=MassX+dm*x
            MassZ=MassZ+dm*z
            
           
            
        return Mass,(MassX/Mass,0,MassZ/Mass)
        
    @staticmethod
    def _interp(x1,y1,x2,y2,x):
        return ((y2-y1)/(x2-x1))*(x-x1)+y1 