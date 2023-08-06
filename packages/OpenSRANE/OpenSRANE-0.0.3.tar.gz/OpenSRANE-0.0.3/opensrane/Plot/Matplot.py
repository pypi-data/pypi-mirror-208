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


import matplotlib.pyplot as _plt
from scipy.stats import norm as _norm
from scipy.stats import lognorm as _lognorm
import opensrane as _opr
import pandas as _pd
import numpy as _np
# from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.offline import iplot as _iplot
import random as _rnd

def PlotUnits2D():
    
    
    #Initial Figure Settings
    #Initial Plot Settings---------------------------------------

    fig, ax = _plt.subplots(figsize=(12, 10), dpi=80)
    font1 = {'family':'serif','color':'blue','size':18}
    font2 = {'family':'serif','color':'darkred','size':14}
    _plt.title("PlantUnits",fontdict = font1,loc='left')
    _plt.xlabel("X",fontdict = font2)
    _plt.ylabel("Y",fontdict = font2)
    
    ColBound=[0, 18/255, 255/255] # Boundary Colors
    ColNodamage=[0, 18/255, 255/255] #Undamaged Colors
    ColDamaged=[255/255, 0, 5/255] #Damaged Colors

    
    #Get All Defined Plant Units
    UnitObj=_opr.PlantUnits.ObjManager.Objlst
    
    
    minx=None
    maxx=None
    miny=None
    maxy=None
    
    
    for Unit in UnitObj:
        
        # Onground Tanks
        if Unit.__class__==_opr.PlantUnits.ONGStorage:
            
            # Get Geometry and Location Data
            xc=Unit.Hlocalcoord
            yc=Unit.Vlocalcoord
            
            D=Unit.d_Storage
            
            tag=Unit.tag
            name=Unit.__class__.__name__
            
            
            
            # Set The boundary
            if minx==None:
                minx=xc-D/2
                maxx=xc+D/2
                miny=yc-D/2
                maxy=yc+D/2

            else:
                if xc-D/2<minx: minx=xc-D/2
                if xc+D/2>maxx: maxx=xc+D/2
                if yc-D/2<miny: miny=yc-D/2
                if yc+D/2>maxy: maxy=yc+D/2
                
                
            
            
            # Add Tank Shape
            
            if Unit.isdamaged==False:
                col2=ColNodamage
            else:
                col2=ColDamaged
                
            ax.add_patch(_plt.Circle((xc, yc), D/2,  alpha=0.3, linestyle ='-',linewidth =1,edgecolor =ColBound,facecolor =col2))
            ax.scatter(xc, yc, color = ColBound, marker = 'o', s = 10)

            

    
          
    #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------

    Ratio=10/12
    
    L1, L2 = maxx-minx, maxy-miny
    xc, yc= (maxx+minx)/2 , (maxy+miny)/2

    if L2/L1>Ratio:
        L1=L2/Ratio
        minx=xc-L1/2
        maxx=xc+L1/2
    else:
        
        L2=L1*Ratio
        miny=yc-L2/2
        maxy=yc+L2/2
            
            
    _plt.xlim(minx-0.05*L1,maxx+0.05*L1)  
    _plt.ylim(miny-0.05*L2,maxy+0.05*L2)
    _plt.show()
    

    return


def PlotFragilities(StdNumber=3,NPoints=100):
    

    stdN=StdNumber
    N=NPoints
    
    #Initial Plot Settings---------------------------------------
    _plt.figure(figsize=(12, 10), dpi=80)
    font1 = {'family':'serif','color':'blue','size':18}
    font2 = {'family':'serif','color':'darkred','size':14}
    _plt.title("Fragility Curves",fontdict = font1,loc='left')
    _plt.xlabel("Random Variables",fontdict = font2)
    _plt.ylabel("Probability",fontdict = font2)
    
    
    #Get All defined Fragilities
    FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict


    #Calculate Range of random of random variables---------------------------------
    data={} #Dictionary for storing data
    x=[]    #Random Variables range
    for tag,FragObj in FragTagObjs.items():

        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':
            minv=FragObj.mean-stdN*FragObj.StdDev
            maxv=FragObj.mean+stdN*FragObj.StdDev
            x=x+[minv+(maxv-minv)/N*x for x in range(N-1)]

    x=filter(lambda x:x>=0,x) #Only Positive Random Variables Have meaning    
    x=set(x) 
    x=list(x)
    x.sort()
    


    #Calculate Probablity for each distribution and plot it------------------------------------ 

    for tag,FragObj in FragTagObjs.items():

        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':

            y=[FragObj.GetProbability(x) for x in x]
            lbl=f'tag{tag}, {FragObj.modename}'
            _plt.fill_between(x,y,color=(_rnd.random(), _rnd.random(), _rnd.random(), 0.3),label=lbl)
            _plt.grid(color = 'green', linestyle = '--', linewidth = 0.4)
            _plt.legend(loc=2)
            _plt.draw()
     

    _plt.xlim(0, max(x))
    _plt.ylim(0, 1.05)    

    return 


def PlotHazard():
    '''
    The First Hazard Object that are defined by the user, is drawn using This Function
    '''
    
    #Initial Plot Settings---------------------------------------
    _plt.figure(figsize=(12, 10), dpi=80)
    font1 = {'family':'serif','color':'blue','size':18}
    font2 = {'family':'serif','color':'darkred','size':14}
    _plt.title("Hazard Curve",fontdict = font1,loc='left')
    _plt.xlabel("Magnitude",fontdict = font2)
    _plt.ylabel("Probability",fontdict = font2)

    
    #Get The first Hazard Object
    HazarbObj=_opr.Hazard.ObjManager.Objlst[0]


    #Get Hazard Curve Values----------------------------------------------------
    x=HazarbObj.Magnitude
    y=HazarbObj.Probabilities  
    
    
    lbl='Defined Hazard'
    _plt.xlim(min(x), max(x))
    _plt.ylim(min(y), max(y))
    _plt.fill_between(x,y,color=(_rnd.random(), _rnd.random(), _rnd.random(), 0.3),label=lbl)
    _plt.grid(color = 'green', linestyle = '--', linewidth = 0.4)
    _plt.legend(loc=1)
    _plt.draw()
    
    return
