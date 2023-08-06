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
import opensrane as _opr
from opensrane.DispersionSpreadModels.ObjManager import *
from opensrane.Misc.WarningRecorder import *
from opensrane.DispersionSpreadModels._GlobalParameters import _GlobalParameters
import numpy as _np
from scipy.interpolate import interp2d as _interp

class BritterMcQuaid(_NewClass,_GlobalParameters):

    # IMPORTANT ATTENTION: it is really important to remember that
    # Before using this Object, self.UnitObject should be assigned and shouldn't be empty
    '''
    Continues Gas Dispersion from a plant Unit
    Spread model for heavy Gas According CasCal Book
    
    This model is for Plant Units That had Gas Content and following a Continues Gas outFlow

    
    
    To use this model pay attention that the following parameters Have to be defined:
    WindSpeed: wind speed model should be defined before and a sampling also have to be done
    Ta: For the site, Site temperature should be defined
    T0: The plant Unit Object Have to be defined before
    Gas OutFlowModel: (dMassGas_release ) A outflow model should be defined and gas outflow parameters (dMassGas_release) should be filled before
    RhoA: Site Air Density Have to be defined (SiteObject.Airdensity)
    RhoGas: Material Gas Density at boiling point Have to be defined for the Material Object (SubstanceObject.BoilingPointGasDensity)
    g: Site gravity acceleration (SiteObject.g) Have to be defined before
    C0: is the initial gas concentration that will be hire from the GasDensity property of the Substance
    
   
    
    '''
    Title='BritterMcQuaid'
    
    
    def __init__(self,tag, MatTags, OutFlowModelTags,  MassParts=20):
        
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        _GlobalParameters.__init__(self,MatTags, OutFlowModelTags)
        
                
        self.name=f'{self.Title} with initial Concentration equal to Substance gas density'
        
        self.MassParts=int(MassParts) # Number of parts to calculate the explosive mass of the gas

    
        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        self.C0=None
    
               
    def Calculate(self):
        
        UnitObject=self.UnitObject    #self.UnitObject is defined in _GlobalParameters
        if UnitObject==None:         
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        if SubstanceObject==None: 
            warning(f'(BritterMcQuaid) in calculation of GassMass and location for Plant Unit with tag {UnitObject.tag}  \n  No substance has been defined for the object so explosion data are ignored!')
            return None
        
        
        LFL=SubstanceObject.Lower_Flammability_Limit
        UFL=SubstanceObject.Upper_Flammability_Limit
        
        if LFL==None or UFL==None:
            warning(f'(BritterMcQuaid) in calculation of GassMass and location for Plant Unit with tag {UnitObject.tag}  \n  for substance with tag {SubstanceObject.tag} LFL and UFL has not been defined Soexplosion data are ignored!')
            return None            
        
        #Set initial gas concentration equal to the Material Gas density
        C0=SubstanceObject.GasDensity
        self.C0=C0
        if C0==None:
            warning(f'(BritterMcQuaid) GasDensity for Subctance with tag {SubstanceObject.tag} used for plant unit with tag {UnitObject.tag}  \n has not been defined and so the dispersion of the gas for this unit has not been calculated')
            return None        
        
        N=self.MassParts                                         # Number of the segments along the LFL and UFL
        FLlist=[UFL-(UFL-LFL)/N*i for i in range(1,N+1)]         # list of the segments gas concentration   
        
        [xlU,ylU],[xrU,yrU],LvU,[xLu,yLu] = self.GiveBoundary(UFL/C0) # Plate Dimension in the UFL
        FL1=UFL
        
        M=0 # Explosive Mass
        
        x0,y0=(xrU+xlU)/2, (ylU+yrU)/2
        dML=0
        dMh=0
        
        for FL in FLlist:

            [xlL,ylL],[xrL,yrL],LvL,[xLu,yLu]= self.GiveBoundary(FL/C0) # Plate Dimension in the FL
            
            
            b2=((xlL-xrL)**2+(ylL-yrL)**2)**0.5 # Width of the plate
            h2=LvL
            b2cx=(xlL+xrL)/2                    # Xcenter of the plate
            b2cy=(ylL+yrL)/2                    # Ycenter of the plate
            
            b1=((xlU-xrU)**2+(ylU-yrU)**2)**0.5 # Width of the plate
            h1=LvU
            b1cx=(xlU+xrU)/2                    # Xcenter of the plate
            b1cy=(ylU+yrU)/2                    # Ycenter of the plate
            
            #Considering a cube with below dimensions and properties 
            bave=(b1+b2)/2
            have=(h1+h2)/2
            dL=((b2cx-b1cx)**2+(b2cy-b1cy)**2)**0.5
            FLave=(FL+FL1)/2
            CubCx=(b2cx+b1cx)/2 # Cube Center
            CubCy=(b2cy+b1cy)/2 # Cube Center
            
            dM=FLave*bave*have*dL
            M=M+dM
            L=((CubCx-x0)**2+(CubCy-y0)**2)**0.5 # Distance of the cube center to the center of the Upper limit boundry
            dML=dML+dM*L
            dMh=dMh+dM*have
            
            
            #Store current section data as previous step data
            [xlU,ylU],[xrU,yrU],LvU,[xLu,yLu]=[xlL,ylL],[xrL,yrL],LvL,[xLu,yLu] #Store previous dimension
            FL1=FL                                                              #Store previous concentration
        
        z=dMh/M  # Height of center explosive mass center
        
        Lm=dML/M  
        
        # 
        x=x0+(CubCx-x0)/L*Lm 
        y=y0+(CubCy-y0)/L*Lm
        
        self.GasExplosiveMass=[M]             
        self.GasExplosiveCenterX=[x] 
        self.GasExplosiveCenterY=[y]
        self.GasExplosiveCenterZ=[z]
        
        self.t_disp=[0]

        return 0
 
 
    def GasConcentration(self,x,y,z):
        
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        
        #Get the unit center location (Considered as the location of gas dispersion)
        Xc=UnitObject.Hlocalcoord
        Yc=UnitObject.Vlocalcoord
        
        #according the direction of the sample wind the the point location along the wind direction respect to the center of unit
        [x,y]=self._convertdirection(x-Xc,y-Yc)
        # print('local X and Y=')
        # print(x,y,'\n')
        
 
        #List of C/C0
        CC0=[0.1,0.05,0.02,0.01,0.005,0.002]
         
        
        X=[]  #to store all x values corresponding to the 
        Lh=[] #to store each x corresponding Lh
        Lv=[] #to store each x corresponding Lv
        
        C0=self.C0
        
        for cc in CC0:
            C=cc*C0
            # print(C)
            [xx,D,V0,g0,u,Ta,T0]=self.Concdist(C)
            # print(C)
            # print('xx,D,V0,g0,u')
            # print(xx,D,V0,g0,u)
            X.append(xx)
            lb=V0*g0*u**(-3)
            Lu=0.5*D+2*lb
            Lh0=D+8*lb
            lh=Lh0+2.5*lb**(1/3)*xx**(2/3)
            Lh.append(lh)
            Lv.append(V0/u/lh)
            
        # print('X=',X)
        # print('Lu=',Lu)
        # print('CC0=',CC0)
        # print('Lh=',Lh)
        # print('Lv=',Lv)
            
        #if x is larger than the maximum x that can have concentration
        if x>max(X):
            # print('case x>max(X)')
            return 0
        
        #if x is smaller than the minimum availabe a linear interpolation is done
        if -Lu<=x<min(X):
            # print('case -Lu<=x<min(X)')
            #interpolation values
            c2=max(CC0)
            c1=1
            x2=min(X)
            x1=0
            c=c1+(c2-c1)/(x2-x1)*(abs(x)-x1)
            
            #interpolation of cross dimension
            Lh2=min(Lh)
            Lh1=0
            x2=min(X)
            x1=-Lu
            lhx=Lh1+(Lh2-Lh1)/(x2-x1)*(x-x1)
            
            #interpolation of height dimension
            Lv2=Lv[0]
            Lv1=0
            x2=min(X)
            x1=-Lu
            lvx=Lh1+(Lv2-Lv1)/(x2-x1)*(x-x1)            
            
            
            #convert c ratio to exact c
            if abs(y)<=lhx and z<=lvx:
                c=c*C0
            else:
                c=0
            return c
        
        if x<-Lu:
            # print('case x<-Lu')
            return 0
        #if none of above case not happend means x is between maximum above cases
        
        # print('case xmin<x<xmax')
        #Get the ipper and lower values
        # print('x=',x)
        x1,x2,c1,c2=[(i,j,k,m) for i,j,k,m in list(zip(X[0:-1],X[1:],CC0[0:-1],CC0[1:])) if i<=x<=j][0]
        # print('x1,x2,c1,c2')
        # print(x1,x2,c1,c2)
        Lh1,Lh2=[(k,m) for i,j,k,m in list(zip(X[0:-1],X[1:],Lh[0:-1],Lh[1:])) if i<=x<=j][0]
        # print('Lh1,Lh2')
        # print(Lh1,Lh2)
        Lv1,Lv2=[(k,m) for i,j,k,m in list(zip(X[0:-1],X[1:],Lv[0:-1],Lv[1:])) if i<=x<=j][0]
        # print('Lv1,Lv2')
        # print(Lv1,Lv2)
        
        #Interpolation for the values
        c=c1+(c2-c1)/(x2-x1)*(abs(x)-x1)
        lhx=Lh1+(Lh2-Lh1)/(x2-x1)*(x-x1)
        lvx=Lv1+(Lv2-Lv1)/(x2-x1)*(x-x1)  
        
        #convert c ratio to exact c
        if abs(y)<=lhx and z<=lvx:
            c=c*C0
        else:
            c=0
        return c       
        
        
    def GiveBoundary(self,CC0Ratio):
        #This Function Should returns the boundary space that have concentration equal to C
        #In the Britter Model A rectangular plate has constant Concentration
        
        #For this model for any entered C program returns below values:
        # Point1:one side of the boundary rectangle
        # Point2:another side of the boundary rectangle
        # xl,yl= left coordinate of the plate
        # xr,yr= Right Coordinate of the plate
        #Lv: Plate Height
        #Lu: Backward Distance               
        #Above Parameters are defined in Figure 7.20 Casal Book
        
        #First Convert C to CC according equation7.35 (in the following according Casal C=C* and CC=C)
        UnitObject=self.UnitObject
        if UnitObject==None:
            raise 'Error: self.UnitObject is emptey and before any usage it should be assigned before'
        xc=UnitObject.Hlocalcoord
        yc=UnitObject.Vlocalcoord
        
        
        C0=self.C0
        C=CC0Ratio*C0
        # print(C)
        [xx,D,V0,g0,u,Ta,T0]=self.Concdist(C) #To get Ta and T0
        CC=C/(C+(1-C)*(Ta/T0))              #Exact Value according equation 7.35    
        C=Ta*CC/(T0*(1-CC)+Ta*CC)           #Formulla By me that is reverse of 7.35 
        # print('C/C0=',C/self.C0)
        # print('CC/C0=',CC/self.C0)

        
        

        
        if CC/C0<0.002:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (GiveBoundary()) for Plant Unit with tag {UnitObject.tag}  \n Because C/C0<0.002 it is considered equal to 0.002 and the results are according C/C0=0.002')
            CC=C0*0.002
            C=Ta*CC/(T0*(1-CC)+Ta*CC) #Because in Concdist function it returns from C* to C (Modified C)
            
        if CC/C0>1:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (GiveBoundary()) for Plant Unit with tag {UnitObject.tag}  \n  Because C/C0>1 it is considered equal to 1 and the results are according C/C0=1')
            CC=C0
            C=Ta*CC/(T0*(1-CC)+Ta*CC) #Because in Concdist function it returns from C* to C (Modified C)
                
        if CC/C0<=0.1:
            # print('case CC/C0<=0.1')
            [xx,D,V0,g0,u,Ta,T0]=self.Concdist(C)
            lb=V0*g0*u**(-3)
            Lu=0.5*D+2*lb
            Lh0=D+8*lb
            Lh=Lh0+2.5*lb**(1/3)*xx**(2/3)
            Lv=V0/u/Lh
            
            [xl,yl]=self._convertBackdirection(xx,Lh)
            [xr,y1]=self._convertBackdirection(xx,-Lh)
            [xLu,yLu]=self._convertBackdirection(-Lu,0)
            return [xl+xc,yl+yc],[xr+xc,y1+yc],Lv,[xLu+xc,yLu+yc]  
            
        # print('case 0.1<CC/C0<=1')
        #Case 0.1<CC/C0<=1 (Using linear Interpolation):
        CC=0.1*C0
        CC=Ta*CC/(T0*(1-CC)+Ta*CC)            #Because in Concdist function it returns from C* to C (Modified C)
        # print(CC)
        [xx,D,V0,g0,u,Ta,T0]=self.Concdist(CC)
        # print([xx,D,V0,g0,u,Ta,T0])
        lb=V0*g0*u**(-3)
        Lu=0.5*D+2*lb
        Lh0=D+8*lb
        Lh=Lh0+2.5*lb**(1/3)*xx**(2/3)
        Lv=V0/u/Lh
        # print(Lv)
        
        #interpolation of x along the wind direction
        c2=CC
        c1=1*C0
        x2=xx
        x1=0
        x=x1+(x2-x1)/(c2-c1)*(C-c1)

        
        
        #interpolation of cross dimension
        Lh2=Lh
        Lh1=Lh0
        x2=xx
        x1=0
        Lh=Lh1+(Lh2-Lh1)/(x2-x1)*(x-x1)
        
        #interpolation of height dimension
        Lv2=Lv
        Lv1=0
        x2=xx
        x1=-Lu
        Lv=Lv1+(Lv2-Lv1)/(x2-x1)*(x-x1)  

        
        [xl,yl]=self._convertBackdirection(x,Lh)
        [xr,yr]=self._convertBackdirection(x,-Lh)
        [xLu,yLu]=self._convertBackdirection(-Lu,0)
        return [xl+xc,yl+yc],[xr+xc,yr+yc],Lv,[xLu+xc,yLu+yc]         

        
    def Concdist(self,C):
        '''
        
        This function returns the distance corresponding to the entered Concentration value
        C=Target Concentration
        This Function gets the C0 from the Corresponding Object
        
        This Function has been provided only for BritterMcQuaid Model
        '''
        
        
        UnitObject=self.UnitObject
        
        
        
        #Import required objects
        SubstanceObject=_opr.Substance.ObjManager[UnitObject.SubstanceTag] if UnitObject.SubstanceTag!=None else None
        SiteObject=_opr.Sites.ObjManager[UnitObject.SiteTag]
        OutFlowObj=UnitObject.OutFlowModelObject
        WindSpeed=_opr.WindData.ObjManager.Objlst[0].WindSpeed
        # print(WindSpeed)
        
        if WindSpeed==None:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (Concdist()) for Plant Unit with tag {UnitObject.tag}  \n  No wind Sample has been created yet! So No Concentration calculated')
            return [0,0,0,0,0,0,1]
        if WindSpeed==0: WindSpeed=0.01

        Ta=SiteObject.Temperature #Site Temperature or air Temperature
        T0=UnitObject.Temperature
        
        
        t_release=OutFlowObj.t_release
        MassGasReleaseRate=OutFlowObj.MassGasReleaseRate
        dMassGas_release=OutFlowObj.dMassGas_release
        TotalMassGas_Release=OutFlowObj.TotalMassGas_Release
        
        if dMassGas_release==None or MassGasReleaseRate==None or TotalMassGas_Release==None or max(MassGasReleaseRate)==0:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (Concdist()) \n Because in the OutFlow Model for Plant Unit with tag {UnitObject.tag} Gas release values was empty or Zero' +
                    f'No Concentration calculated (Check Pressure of the Plant Unit and OUt Side Pressure)')
            return [0,0,0,0,0,0,1]
        
        
        RhoA=SiteObject.Airdensity
        RhoGas=SubstanceObject.BoilingPointGasDensity
        if RhoGas==None or RhoA==None:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (Concdist()) for Plant Unit with tag {UnitObject.tag}  For material with tag {SubstanceObject.tag} BoilingPointGasDensity or AirDensity of Site has not been defined so ' +
                    f'Concentration can not be calculated')
            return [0,0,0,0,0,0,1]
        
        g=SiteObject.g
        C0=self.C0
        
        if C>C0:
            warning(f'(BritterMcQuaid) in DeispersionSpreadModels in (Concdist()) for Plant Unit with tag {UnitObject.tag} Because entered C > C0, it is modified and C=C0 has been considered')
            C=C0
       
        
        #Calculations
        u=WindSpeed
        g0=g*(RhoGas-RhoA)/RhoA
        # print('g0=',g0)
        
        V0=max(MassGasReleaseRate)/RhoGas #(Gas Volume OutFlow Speed = MassOutFlow Speed/Gas Density)
        # print('V0',V0)
        D=(V0/u)**0.5
        # print(D)
        C=C/(C+(1-C)*(Ta/T0))
        # print(C)

        
        HAV=(g0**2*V0/u**5)**(1/5)
        
        CC0=C/C0
        # print(C)
        # print(C0)
        # print(CC0,'\n')
        
        if CC0<=0.1:
            x=D*self._data(CC0,HAV)
        else:
            x2=D*self._data(0.1,HAV)
            x=x2/(0.1-1)*(CC0-1)
        
        return x,D,V0,g0,u,Ta,T0
        
        
    def _data(self,CC0Value,Horizontal_Value):
        
        '''
        This function returns BritterMcQuaid Table data and for given C/C0 value and horizontal value it gives 
        vertical Axis Value
        
        This Function has been provided only for BritterMcQuaid Model
        '''
        
        c=_np.array([0.1,0.05,0.02,0.01,0.005,0.002]) # C/C0 Values
        HAV=_np.array([0.1,0.110564,0.12762,0.158262,0.199097,0.228168,0.272984,0.326602,0.371615,0.422832,
           0.516887,0.588126,0.71381,0.910965,1.22244,1.56008,2.04893,2.5776,3.03995,3.7429,4.07936]) # Horizontal Axis Values
           
        data=_np.array([
                [56.44,81.27,121.3,173.43,247.97,386.33],
                [56.71,81.27,121.3,173.43,247.94,386.27],
                [56.53,81.08,121.84,173.43,247.88,386.19],
                [56.44,80.98,122.17,173.43,246.37,386.06],
                [56.67,81.96,122.49,173.43,250.82,389.67],
                [56.82,84.01,126.36,179.75,257.5,402.75],
                [56.56,89.11,136.79,195.85,276.35,429.14],
                [58.3,96.79,148.35,221.17,313.42,461.79],
                [60.83,102.67,157.51,244.46,345.03,489.98],
                [63.47,108.47,166.89,264.46,369.27,523.4],
                [67.63,113.06,174.68,280.03,402.33,556.06],
                [69.08,112.98,174.68,284.06,417.92,566.93],
                [69.82,110.1,172.71,274.09,414.46,567.77],
                [67,101.61,159.81,251.55,392.03,533.83],
                [59.6,88.52,137.28,218.03,349.12,472.5],
                [52.19,77.65,119.31,186.29,312.09,420.58],
                [44.36,65.13,102.03,161.46,270.68,366.12],
                [38.43,56.2,88.28,139.95,235.04,324.74],
                [34.45,51.5,80.63,127.52,210.1,298.87],
                [30.39,44.59,71.85,112.12,188.62,268.33],
                [28.61,42.7,67.97,107.41,177.44,253.71],
            ])
            
        #Check the range of Entered values
        if CC0Value<min(c): 
            CC0Value=min(c)
            # print('Because of C/C0<0.002 it is considered Equal to 0.002')
            
        if CC0Value>max(c): 
            CC0Value=max(c)
            # print('Because of C/C0>0.1 it is considered Equal to 0.1')
     
        if Horizontal_Value<min(HAV): 
            Horizontal_Value=min(HAV)
            # print('Because of g0^2V0/u^5<0.1 it is considered equal to 0.1')
            
        if Horizontal_Value>max(HAV): 
            Horizontal_Value=max(HAV)
            # print('Because of g0^2V0/u^5>4.07 it is considered equal to 4.07') 
           
        f = _interp(c, HAV, data, kind='cubic')
        return float(f(CC0Value,Horizontal_Value))
        
        
