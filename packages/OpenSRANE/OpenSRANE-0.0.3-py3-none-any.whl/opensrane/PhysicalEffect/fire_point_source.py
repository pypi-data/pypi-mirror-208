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
import random as _rnd
import opensrane as _opr

class fire_point_source(_NewClass,_GlobalParameters):
    
    '''
    In this function the geometry of the fire on the pool is calculated and then the fire heat radiation will be calculated
    reference for This File: Casal Evaluation of the Effects and Consequences of Major Accidents in Industrial Plants 2nd Wdition
    Chapter 3: Fire Accidents
    
    minf: is burning velocity for an infinite diameter pool. some sample values are presented in table 3.8 cascal book
    k: constant according table 3.8 cascal book
    '''
    Title='Fire Point Source Physical Effect'
    
    def __init__(self,tag,minf=0.055,k=1.5):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        
        _GlobalParameters.__init__(self)
        
        self.minf=minf      # minf is burning velocity for an infinite diameter pool. some sample values are presented in table 3.8 cascal book 
        self.k=k            # k: constant according table 3.8 cascal book

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass
        
    @property
    def name(self):    
        return f'Fire Point Source Physical Effect for unit with tag {self.UnitObject.tag} ' if self.UnitObject!=None else 'Fire Point Source Physical Effect But still No Plant unit is assigned to it'
        

    def Thermal_Radiation_at_Point(self,x,y,z):
        #This function calculate the thermal radiation in point x,y,z
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(Fire_Point_Source) Because of no assigned plant unit will not do any calculations')
            return None
        
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag]
        if SiteObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of No site tag has been defined for metioned Plant unit Object')
            return None 
            
        Hr=SiteObject.Humidity   #Site Humidity
        Ta=SiteObject.Temperature #Site Temperature or air Temperature
        if Ta==None or Hr==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of Ambient Temperature (Ta) or Site Humidity (Hr) has not been defined for the site with tag{UnitObject.SiteTag}')
            return None
        
    
        #Get Substance that is assigned to the unit Object
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        if SubstanceObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of No substance is defined for the mnetioned Plant unit Object')
            return None  

        
        #get burning rate of unit of area (m)
        GEOM=self._fireGeometry()
        if GEOM==None:
            return None         
        [H,Hmax,D,Dprin,alpha,m]=GEOM
        
        
        mprime=m*_math.pi*D**2/4                                     #Total Burning Rate (kg/s)
        Ettarad=0.35*_math.exp(-0.05*D)                              # 3.15 cascal book
        DeltaHc=SubstanceObject.Specific_Heat_of_Combustion          #heat of combustion of the pool substance )j/kg
        if DeltaHc==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because for its substance with tag {UnitObject.SubstanceTag} Specific_Heat_of_Combustion has not been defined')
            return None

        Qr=Ettarad*mprime*DeltaHc                                    # 3.14 cascal book (combustion energy that is transferred as thermal radiation)
        
        Pwa=_math.exp(23.18986-3816.42/(Ta-46.13))                   # 3.19 cascal book  (saturated water vapor pressure at the atmospheric temperature)
        Pw=Pwa*Hr                                                    # 3.18 cascal book  (partial pressure of water in the atmosphere)
        
        DIST=self._DistanceToFireCenterGeometry(x,y,z)         #Distance parameters According fig 3.4 cascal book
        if DIST==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of None return from _DistanceToFireCenterGeometry, is not calculated!')
            return None
        [Lp,d,phi,xf,yf]=DIST
        
        if Pw*d<10**4:
            tau=1.53*(Pw*d)**(-0.06)                                 # 3.17 cascal book (water vapor content)
        elif 10**4<=Pw*d<=10**5:
            tau=2.02*(Pw*d)**(-0.09)
        else:
            tau=2.85*(Pw*d)**(-0.12)
            
        
        I=Qr*tau*_math.cos(phi)/4/_math.pi/Lp**2
        
        return I
        
        
        
        
    def _DistanceToFireCenterGeometry(self,x,y,z):
        #This function returns the distance of the desire point to the geometric center of the fire According fig 3.4 cascal book
    
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(Fire_Point_Source) Because of no assigned plant unit will not do any calculations')
            return None
            
        
        #Import Liquid Dispersion Object
        DispersionObject=UnitObject.DispersionSpreadModelObject
        if DispersionObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of no DispersionObject (DispersionObject=None) is not calculated!')
            return None
        
        #Last Position of liquid pool center 
        if DispersionObject.LiquidCenter==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of its DispersionObject Has no LiquidCenter list () is not calculated!')
            return None
        [xp,yp]=DispersionObject.LiquidCenter[-1]
        # print('xp,yp=',xp,yp)
        
        
        
        #import Dike Obj
        DikeObj= _opr.Safety.ObjManager[UnitObject.DikeTag] if UnitObject.DikeTag!=None else None
        
        #get dike height
        if DikeObj==None:
            zc=0
        else:
            zc=DikeObj.Height
            
        
        
        #Get the unit center location (Considered as the refrence location [0,0])
        Xc=UnitObject.Hlocalcoord
        Yc=UnitObject.Vlocalcoord
        # print('Xc,Yc=',Xc,Yc)
        
        #according the direction of the sample wind the the point location along the wind direction respect to the center of unit 
        #means that center of the 
        [x,y]=self._convertdirection(x-Xc,y-Yc)        #Point Position respect to the center of the Unit Object
        [xp,yp]=self._convertdirection(xp-Xc,yp-Yc)    #Center of pool Position respect to the center of the Unit Object
            
        #Calculate pool Flame geometry
        [H,Hmax,D,Dprin,alpha,m]=self._fireGeometry()
        

        zf=H*_math.cos(alpha)/2+zc                                                               #Z center of the fire
        xf=xp+(Dprin-D)/2+H*_math.sin(alpha)/2 if Dprin!=0 else xp+H*_math.sin(alpha)/2          #X Center of the fire
        yf=yp                                                                                    #Y Center of the fire 
        Rf=D/2                                                                                   #Fire Radious thet is cosidered equal pool Radious 
        
        Hdist=((x-xf)**2+(y-yf)**2)**0.5
        Vdist=abs(zf-z)
        
        Lp=(Hdist**2+Vdist**2)**0.5                                           #According fig 3.4 cascal book
        phi=_math.atan(Vdist/Hdist) if  Hdist!=0 else _math.atan(Vdist/Rf)    #According fig 3.4 cascal book 
        d=(Hdist-Rf)/_math.cos(phi)                                           #According fig 3.4 cascal book (In this formoula alpha is not considered and consequently the slope of the fire is not consider and should be modify)
        
        if d<=0:                                       #Added by my own
            d=0.01
        

        #return the position of fire center in global coordinate
        [xf,yf]=self._convertBackdirection(xf,yf)
        xf,yf=xf+Xc, yf+Yc
        
        return Lp,d,phi,xf,yf
        
        
        
    def _fireGeometry(self):
        # This function returns the Geometric dimension of the fire

        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(Fire_Point_Source) Because of no assigned plant unit will not do any calculations')
            return None
            
            
        #Import required objects
        DispersionObject=UnitObject.DispersionSpreadModelObject
        if DispersionObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of no DispersionObject (DispersionObject=None) is not calculated!')
            return None
        
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag]

        if SiteObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} is not calculated, because of no site tag is defined for mentioned Plant unit')
            return None  
            
        RhoA=SiteObject.Airdensity
        g=SiteObject.g
        
        
        if _opr.WindData.ObjManager.Objlst==[]:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} is not calculated, because of no wind Object is not defined')
            return None            
        WindSpeed=_opr.WindData.ObjManager.Objlst[0].WindSpeed
        
        if WindSpeed==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} is not calculated, because of no wind sampling')
            return None

        
        if DispersionObject.LiquidRadious==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of Pool Radious (DispersionObject.LiquidRadious==None) is not calculated!')
            return None
        
        D=max(DispersionObject.LiquidRadious)
        if D==0:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of Pool Radious=0 (DispersionObject.LiquidRadious==0) is not calculated!')
            return None
        D=D*2
        
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        if SubstanceObject==None:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} because of No substance is defined for the mnetioned Plant unit Object')
            return None        
        
        Density=SubstanceObject.Density
        if Density==None or Density==0:
            warning(f'(Fire_Point_Source) for Plant unit {UnitObject.tag} is not calculated!, because of Density of substance wi tag={SubstanceObject.tag} with name {SubstanceObject.name} is 0 or None.')
            return None           
        
        
        minf=self.minf
        k=self.k
        uw=WindSpeed
        #Calculations
        m=minf*(1-_math.exp(-k*D)) #Casal 3.40 (Burning rate of unit area) (kg/m2/s)
        y=m/Density                #Casal 3.42
        
        uc=(g*m*D/RhoA)**(1/3)      #Page 107 Formula (cascal book)

        
        if uw>=uc:
            ustar=uw/uc
        else:
            ustar=1
            
        H=D*7.74*(m/RhoA/(g*D)**0.5)**0.375*(ustar)**(-0.1)    #flame length formula 3.43
        
        Hmax=D*1.52*(H/D)                                      #maximum of flame length formula 3.44
        
        if ustar<=1:
            alpha=_math.acos(1)                                #flame tilt
        else:
            alpha=_math.acos(1/ustar**0.5)
            
        Dprin=D*1.5*(uw**2/g/D)**0.069                         #flame drag Casal 3.47
        if Dprin<=D: Dprin=0
        
        return H,Hmax,D,Dprin,alpha,m
        
        
    def RadiationBoundary(self,Radiation,Height,PointNumber):
        
        
        #This function returns N PointNumber location that have equal radiation value (Radiation) at z=Height
        Resluts={}
        
        z=Height
        N=PointNumber
        I=Radiation
        
        UnitObject=self.UnitObject #self.UnitObject has been defined in _GlobalParameters
        if UnitObject==None:         
            warning('(Fire_Point_Source) Because of no assigned plant unit will not do any calculations')
            return None        
        
        #Get the unit center location (Considered as the refrence location [0,0])
        Xc=UnitObject.Hlocalcoord
        Yc=UnitObject.Vlocalcoord
        
        if self.Thermal_Radiation_at_Point(Xc,Yc,z)==None:
            warning('(fire_point_source) RadiationBoundary is not calculated because Thermal_Radiation_at_Point==None for PlantUnit with tag= {UnitObject.tag} ')
            return None
            
        if self._DistanceToFireCenterGeometry(Xc,Yc,z)==None:
            warning('(fire_point_source) RadiationBoundary is not calculated because _DistanceToFireCenterGeometry==None for PlantUnit with tag= {UnitObject.tag} ')
            return None
        
        #Set Xc, Yc = Center of Fire
        [Lp,d,phi,Xc,Yc]=self._DistanceToFireCenterGeometry(Xc,Yc,z)
            
        Phi=[i*2*_math.pi/N for i in range(N)]
        
        
        sign = lambda x: (1, -1)[x<0] #Sign Function
        

        for phi in Phi:
        
            #Check The Maximum Avalability
            RR=[]
            II=[]
            R=[i*10 for i in range(-100,-20)]+[i/2 for i in range(-400,400)]+[i*10 for i in range(20,100)]
            
            for r in R:
            
                x=Xc+r*_math.cos(phi)
                y=Yc+r*_math.sin(phi)
                I1=self.Thermal_Radiation_at_Point(x,y,z)
                RR.append(r)
                II.append(I1)
            # print('')
            # print(f'for <<phi={phi}>> Max(II)=',max(II), 'I=',I)
            
            if max(II)<I:
                # print('Err (It will send None because) max(II)<I=',max(II),I)
                Resluts[phi]=None
                continue
                
                            
                    
            if min(II)<I:
                # print('O.K. min(II)<I<max(II) ->:')
                for r in R[::-1]:
                    
                    x=Xc+r*_math.cos(phi)
                    y=Yc+r*_math.sin(phi)
                    I1=self.Thermal_Radiation_at_Point(x,y,z)
                    if I1>=I:
                        R1=r
                        I1=I1
                        R=R1+(R2-R1)/(I2-I1)*(I-I1)
                        x=Xc+R*_math.cos(phi)
                        y=Yc+R*_math.sin(phi)
                        # print('phi,R,(x,y)=',phi,R,(x,y))
                        Resluts[phi]=(x,y)
                        break
                        
                    R2=r
                    I2=I1
                continue
                
            
        
        #The below part is for some rare condition and uses linear interpolation to find the point---------------------------
            R0=1000*sign(_math.sin(phi)) if _math.sin(phi)!=0 else 1000*sign(_math.cos(phi))
            x=Xc+R0*_math.cos(phi)
            y=Yc+R0*_math.sin(phi)
            I0=self.Thermal_Radiation_at_Point(x,y,z)
            R1=1100*sign(_math.sin(phi)) if _math.sin(phi)!=0 else 1100*sign(_math.cos(phi))
            x=Xc+R1*_math.cos(phi)
            y=Yc+R1*_math.sin(phi)           
            I1=self.Thermal_Radiation_at_Point(x,y,z)
            
            cnt=True
            cntr=0
            sides=False

            
            while abs(I-I0)/I>5/100 and abs(I-I1)/I>5/100 and cnt==True:
                
                if sides==False:
                    x=Xc+R1*_math.cos(phi)
                    y=Yc+R1*_math.sin(phi)
                    I1=self.Thermal_Radiation_at_Point(x,y,z)
                    
                
                    if I0<=I<=I1 or I0>=I>=I1:
                        sides=True
                        cntr=0
                        
                    else:
                    
                        R=R1+(I-I1)*(R0-R1)/(I0-I1)
                    
                        #To avoid convergance problems
                        while abs(R)>10000: R=R/_rnd.randint(2,10)
                        # if max(abs(R-R0),abs(R-R1))>2*abs(R1-R0): R=R1+R0/2

                        R0=R1
                        I0=I1
                        R1=R
                        cntr+=1
                            
                        if cntr>110: 
                            warning(f'(fire_point_source) (RadiationBoundary) for plant unit {UnitObject.tag} is not calculated because distance for radiation {Radiation} at phi {phi} is greater than 1000 meter linear interpolation coudnt find proper answer')
                            cnt==False
                
                            
                else:
                
                    R=(R0+R1)/_rnd.randint(2,5)
                    x=Xc+R*_math.cos(phi)
                    y=Yc+R*_math.sin(phi)
                    IR=self.Thermal_Radiation_at_Point(x,y,z)
                    if I1>IR>=I: R1,I1=R,IR
                    if I1<IR<=I: R1,I1=R,IR
                    if I0>IR>=I: R0,I0=R,IR
                    if I0<IR<=I: R0,I0=R,IR

                   
                    
                    cntr+=1                    
                    if cntr>100: #After 100 times return Not Solved
                        warning(f'(fire_point_source) (RadiationBoundary) for plant unit {UnitObject.tag} is not calculated because distance for radiation {Radiation} at phi {phi} is greater than 1000 meter linear interpolation coudnt find proper answer')
                        cnt==False
               
            Resluts[phi]=(x,y) if cnt==True else None
        
  

  
        #Modify None Values by considering the minimum Radiuse (R)
        R=[]
        R=[((j[0]-Xc)**2+(j[1]-Yc)**2)**0.5 for i,j in Resluts.items() if j!=None]
        # print('Resluts=',Resluts)
        # print('R=',R)

        if R!=[]:
        
            for key,value in Resluts.items():
                keys=list(Resluts.keys())
                keys=[i for i in keys if i>=key]+[i for i in keys if i<key]

                if value==None:
                    
                    (x,y)=[Resluts[k] for k in keys if Resluts[k]!=None][0]
                    R=((x-Xc)**2+(y-Yc)**2)**0.5
                    x=Xc+R1*_math.cos(phi)
                    y=Yc+R1*_math.sin(phi)                       
                    Resluts[key]=(x,y)
                    
        else:
            #print(f'(fire_point_source) (RadiationBoundary) for plant unit {UnitObject.tag} is not calculated because distance for radiation {Radiation} for all angels returned []')
            Resluts=None
            
   
        return Resluts
            