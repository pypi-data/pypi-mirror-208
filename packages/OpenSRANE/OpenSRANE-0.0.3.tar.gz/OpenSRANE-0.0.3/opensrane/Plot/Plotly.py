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


import plotly.graph_objects as _go
import plotly.colors as _PLcols 
from scipy.stats import norm as _norm
from scipy.stats import lognorm as _lognorm
import opensrane as _opr
import random as _rnd
import pandas as _pd
import numpy as _np
import math as _math
import plotly.figure_factory as _ff
# from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.offline import iplot as _iplot
from plotly.offline import plot as _plot
from tqdm import tqdm as _tqdm

'''

            # Get Geometry and Location Data and the Other required data
            xc=Unit.Hlocalcoord
            yc=Unit.Vlocalcoord
            
            D=Unit.d_Storage
            
 
            
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

            fig.add_shape(type="circle", xref="x", yref="y", name=name,
                x0=xc-D/2, y0=yc-D/2, x1=xc+D/2, y1=yc+D/2,
                line_color=Plcollist[Unit.DamageLevel] if (Unit.DamageLevel!=None and Unit.DamageLevel!=0) else ColBound ,fillcolor=ColNodamage if Unit.isdamaged==False else ColDamaged ,)
                # 'rgba'+Plcollist[Unit.DamageLevel][3:-1]+', 0.1)' if (Unit.DamageLevel!=None and Unit.DamageLevel!=0) else
                
            fig.add_trace(_go.Scatter(x=[xc], y=[yc], mode='markers', name='TanksData',showlegend=False,legendgroup='TanksData',
                                      marker=dict(color=ColBound),
                                     
                                      hoverinfo='text',
                                      hovertext=f'{name} (tag= {tag}) and Substance= {_opr.Substance.ObjManager[Unit.SubstanceTag].name} (tag= {Unit.SubstanceTag})'+
                                      f'<br><br>Diameter= {D} \t <br>Damage Source= {Unit.DamageSource} \t <br>with Damage SourceTag= {Unit.DamageSourceTag} \t <br>Damage Level= {Unit.DamageLevel}, Damage Source Type= {Unit.DamageSourceType}, Damage Source Dose= {Unit.DamageSourceDose}' +
                                      f'<br><br>{"OutFlowModel: <br>"+outFlowname if outFlowname!=None else ""}' +
                                      f'<br><br>{"DispersionSpreadModel: <br>"+DispSprdModelname if DispSprdModelname!=None else ""}' +
                                      f'<br><br>{"PhysicalEffectModel: <br>"+PhysicalObjname if PhysicalObjname!=None else ""}',
                                      hoverlabel=dict(bgcolor=f'rgba(0, 0, 0, 1)',
                                                bordercolor=f'rgba(255, 0, 0, 1)',
                                                font=dict(family='Balto',           #or other font family
                                                size=14,                            #or other size
                                                color=f'rgba(255, 255, 255, 1)')
                                                                ),
                                     )
                         )
                         
'''


def PlotWindRose(WindRoseTag,Draw_For_Day=True,PlotMode=1, width=None, height=None):
    #Figure Settings -------------------------------------------------------- 
    fig = _go.Figure()
    
    
    #Get WindRose Object
    obj=_opr.WindData.ObjManager.TagObjDict[WindRoseTag]
    
    #Get Day-Night Data
    if Draw_For_Day==True:
        WindSpeedList=obj.DayWindSpeedList
        WindMatrix=obj.DayWindFreqMatrix
        title='Day Wind Speed Distribution'
    else:
        WindSpeedList=obj.NightWindSpeedList
        WindMatrix=obj.NightWindFreqMatrix
        title='Night Wind Speed Distribution'
        
    for col,windspeed in enumerate(WindSpeedList):
        
        freq=[fr[col] for fr in WindMatrix]
        if len(windspeed)==2:
            name=f'{windspeed[0]}-{windspeed[1]}'
        else:
            name=f'{windspeed[0]}'
        if col+1==len(WindSpeedList):
            name=f'{windspeed[0]}'
        
        
        fig.add_trace(_go.Barpolar(
            r=freq,
            name=name,
            marker_color=f'rgba({_rnd.randint(1,255)},{_rnd.randint(1,255)},{_rnd.randint(1,255)},1)',
            ))
            
    
    
    
 
    
    #fig.update_traces(text=['North', 'N-E', 'East', 'S-E', 'South', 'S-W', 'West', 'N-W'])
    
    
    #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
    fig.update_layout(
        title=title,
        font_size=16, legend_font_size=16,
        #polar_radialaxis_ticksuffix='%',
        polar_angularaxis_rotation=90,)
    
    if height!=None:
        fig.update_layout(height=height)
    if width!=None:
        fig.update_layout(width=width)


    if PlotMode==3:
        
        return _iplot(fig)
        
    elif PlotMode==2:
        
        image_filename='WindDay.html' if Draw_For_Day==True else 'Windnight.html'
        _plot(fig,filename=image_filename,config = dict({'scrollZoom': True}))
        
    else:
        fig.show()
    


def PlotUnits2D(PlotMode=1,OverPressureList=[],OverPressureHeight=2, OverPressurePointNumber=20,
                RadiationList=[],RadiationHeight=2,RadiationPointNumber=20, 
                GasConcentrationlist=[],GasConcentrationHeght=2,ConcentrationPointNumber=10
                ,raw=False, width=None, height=None):
    '''
    RadiationList: list of desired radiation values to be plotted 
    RadiationHeight: height of radiation calculations
    RadiationPointNumber: Radiation Boundary Points number To plot for

    OverPressureList: list of desired OverPressure values to be plotted 
    OverPressureHeight: height of OverPressure calculations
    OverPressurePointNumber: OverPressure Boundary Points number To plot for
    
    GasConcentrationlist: list of desired Concentration values to be plotted 
    GasConcentrationHeght: heght of Concentration calculations
    ConcentrationPointNumber: Concentration Points number for numeric calculations
    
    raw: Boolean that if consider as True means that just only plot the plant without showing any damages or other events.
    '''
    
    Plcollist=_PLcols.DEFAULT_PLOTLY_COLORS*20 #List of plotly Colors
    Plcollist=['rgb(255, 0, 5)']+Plcollist[1:3]+Plcollist[4:]
    
    #Initial Figure Settings
    fig = _go.Figure()
    fig.update_layout(plot_bgcolor='white')
    ColBound=f'rgba(0, 0, 0,1)' # Boundary Colors
    ColNodamage=f'rgba(250, 250, 250,0.2)' #Undamaged Colors
    ColDamaged=f'rgba(255, 0, 5,0.2 )' #Damaged Colors

    #col2=col1.replace('0.5)','0.1)')
    
    #Get All Defined Plant Units
    UnitObj=_opr.PlantUnits.ObjManager.Objlst
    
    
    minx=None
    maxx=None
    miny=None
    maxy=None
    
    ArrowsDict={} #Dictionary that Stores the Damage level arrows
    
    #Plot Tanks
    minx,maxx,miny,maxy=_PlotTanks(fig,PlotDamagedColor=True,raw=raw)

    
    for Unit in _tqdm(UnitObj,desc='Adding Units Data'):
        
        # Onground Tanks
        if Unit.__class__==_opr.PlantUnits.ONGStorage:

            tag=Unit.tag
            name=Unit.__class__.__name__
            outFlowname=Unit.OutFlowModelname
            
            DispSprdModelname=Unit.DispersionSpreadModelname
            DispSprdObj=Unit.DispersionSpreadModelObject
            
            if DispSprdObj!=None:
                LiquidRadios=DispSprdObj.LiquidRadious[-1] if DispSprdObj.LiquidRadious!=None else None
                LiquidCenter=DispSprdObj.LiquidCenter[-1] if DispSprdObj.LiquidCenter!=None else None
            
            PhysicalObjname=Unit.PhysicalEffectModelname
            PhysicalObj=Unit.PhysicalEffectObject
            

            
            #Draw Liquid Dispersion
            if DispSprdModelname!=None and raw==False:
                if LiquidCenter!=None:
                    
                    x0=LiquidCenter[0]
                    y0=LiquidCenter[1]
                    R=LiquidRadios
                    Phi=[i/20*2*_math.pi for i in range(20)]
                    x=[x0+R*_math.cos(phi) for phi in Phi]
                    y=[y0+R*_math.sin(phi) for phi in Phi]
                    
                    fillcol=f'rgba(55, 52, 235,0.1)'
                    Boundcol=f'rgba(1, 1, 1,0.01)'
                    fig.add_scatter(x=x,y=y,fill='toself',fillcolor=fillcol,mode='lines',
                                    line=dict(color=Boundcol,width=1,
                                    shape='spline',smoothing=0.9,simplify=False,),
                                    hoverinfo='none',name=f'Liquid Dispersion',showlegend=False,legendgroup=f'Liquid Dispersion', visible='legendonly')

                    # Set The boundary
                    if minx==None:
                        minx=x0-R
                        maxx=x0+R
                        miny=y0-R
                        maxy=y0+R

                    else:
                        if x0-R<minx: minx=x0-R
                        if x0+R>maxx: maxx=x0+R
                        if y0-R<miny: miny=y0-R
                        if y0+R>maxy: maxy=y0+R
                        
            
            #Draw Gas Dispersion for BritterMcQuaid Model (Should Be Modify for Specific Entered Concentrations in the list)
            if DispSprdObj!=None and DispSprdObj.Title=='BritterMcQuaid' and GasConcentrationlist!=[] and raw==False:
                CC0=[1,0.8,0.7,0.5,0.4,0.2,0.1,0.05,0.02,0.01,0.005,0.002]
                P1s=[]
                P2s=[]
                Lvs=[]
                for c in CC0:
                    P1,P2,Lv,Lu=DispSprdObj.GiveBoundary(c)
                    P1s.append(P1)
                    P2s.append(P2)
                    Lvs.append(Lv)
                
                L1x=[Lu[0]]+[i for i,j in P1s]
                L1y=[Lu[1]]+[j for i,j in P1s]
                L2x=[Lu[0]]+[i for i,j in P2s]
                L2y=[Lu[1]]+[j for i,j in P2s]
                
                fillc=f'rgba(250, 250, 5,0.2)' if DispSprdObj.Title=='BritterMcQuaid' else f'rgba(55, 52, 235,0.1)'
                fig.add_scatter(x=L1x, y=L1y,mode='lines',line=dict(color=f'rgba(250, 250, 5,1)'),hoverinfo='none',name='GasDispersions',showlegend=False,legendgroup='GasDispersions', visible='legendonly')
                fig.add_scatter(x=L2x, y=L2y,mode='lines',line=dict(color=f'rgba(250, 250, 5,1)'),fill='tonexty',fillcolor=fillc,hoverinfo='none',name='GasDispersions',showlegend=False,legendgroup='GasDispersions', visible='legendonly')
                
                
                # Set The boundary
                if minx==None:
                    minx=min(min(L1x,L2x))
                    maxx=max(max(L1x,L2x))
                    miny=min(min(L1y,L2y))
                    maxy=max(max(L1y,L2y))

                else:
                    if min(min(L1x,L2x))<minx: minx=min(min(L1x,L2x))
                    if max(max(L1x,L2x))>maxx: maxx=max(max(L1x,L2x))
                    if min(min(L1y,L2y))<miny: miny=min(min(L1y,L2y))
                    if max(max(L1y,L2y))>maxy: maxy=max(max(L1y,L2y))   
            
            #Draw Gas Dispersion for LqdSprdGaussianGasDisp

            if DispSprdObj!=None and (DispSprdObj.Title=='LqdSprdGaussianGasDisp' or DispSprdObj.Title=='GasGaussian') and GasConcentrationlist!=[] and raw==False:
                for C in GasConcentrationlist:
                    points=DispSprdObj.GiveBoundary(C=C,z=GasConcentrationHeght,SegmentNumbers=ConcentrationPointNumber,errpercent=1)
                    fillc=f'rgba(250, 250, 5,0.2)'
                    x=[p[0] for p in points]
                    y=[p[1] for p in points]
                    fig.add_scatter(x=x, y=y,mode='lines',line=dict(color=f'rgba(250, 250, 5,1)'),fill='toself',fillcolor=fillc,hoverinfo='none',name='GasDispersions',showlegend=False,legendgroup='GasDispersions', visible='legendonly')
                    
                    # Set The boundary
                    if minx==None:
                        minx=min(x)
                        maxx=max(x)
                        miny=min(y)
                        maxy=max(y)

                    else:
                        if min(x)<minx: minx=min(x)
                        if max(x)>maxx: maxx=max(x)
                        if min(y)<miny: miny=min(y)
                        if max(y)>maxy: maxy=max(y)   
                           
      
            
            #Draw Radiation Boundary
            if PhysicalObj!=None and RadiationList!=[] and raw==False:
                # print(f'start of radiation for unit {Unit.tag}')
                
                for Rad in RadiationList:
                    Results=PhysicalObj.RadiationBoundary(Rad,RadiationHeight,RadiationPointNumber)
                    if Results!=None:
                        points=Results.values()
                        x=[i[0] for i in points if i!=None]
                        x=x+[x[0]]
                        y=[i[1] for i in points if i!=None]
                        y=y+[y[0]]
                        RadColor=f'rgba(250,50,0,{Rad/max(RadiationList)})'
                        fig.add_scatter(x=x,y=y,fill='toself',fillcolor=f'rgba(250,50,0,{Rad/max(RadiationList)*0.2})',mode='lines',
                                        line=dict(color=RadColor,width=1,
                                        shape='spline',smoothing=0.9,simplify=False,),
                                        hoverinfo='none',name=f'Radiation{Rad}',showlegend=False,legendgroup=f'Radiation{Rad}', visible='legendonly')
                                        
                        # Set The boundary
                        if min(x)<minx: minx=min(x)
                        if max(x)>maxx: maxx=max(x)
                        if min(y)<miny: miny=min(y)
                        if max(y)>maxy: maxy=max(y)
                # print('end of radiation')    
        
        
            #Draw OverPressure boundary
            if PhysicalObj!=None and OverPressureList!=[] and raw==False:
                # print(f'start of OverPressure for unit {Unit.tag}')            
            
                for OverP in OverPressureList:
                    Results=PhysicalObj.OverPressureBoundary(OverP, OverPressureHeight, OverPressurePointNumber)
                    if Results!=None and Results!=0 :
                        points=Results.values()
                        x=[i[0] for i in points if i!=None]
                        x=x+[x[0]]
                        y=[i[1] for i in points if i!=None]
                        y=y+[y[0]]
                        OverPColor=f'rgba(50,250,0,{OverP/max(OverPressureList)})'
                        fig.add_scatter(x=x,y=y,fill='toself',fillcolor=f'rgba(50,250,0,{OverP/max(OverPressureList)*0.2})',mode='lines',
                                        line=dict(color=OverPColor,width=1,
                                        shape='spline',smoothing=0.9,simplify=False,),
                                        hoverinfo='none',name=f'OverPressure{OverP}',showlegend=False,legendgroup=f'OverPressure{OverP}', visible='legendonly')
                                        
                        # Set The boundary
                        if min(x)<minx: minx=min(x)
                        if max(x)>maxx: maxx=max(x)
                        if min(y)<miny: miny=min(y)
                        if max(y)>maxy: maxy=max(y)
                        
                # print('end of OverPressure') 

                
        #Get DamageLevels Arrows Data
        
        
        if Unit.DamageLevel!=None and Unit.DamageLevel>0 and raw==False:
            
            #To consider multi damage sources (For radiations)
            DmSources=Unit.DamageSourceTag if type(Unit.DamageSourceTag)==list else [Unit.DamageSourceTag] 
            for dm in DmSources:
                SourceUnitObj=_opr.PlantUnits.ObjManager[dm]
                x,y=SourceUnitObj.Hlocalcoord, SourceUnitObj.Vlocalcoord
                ax,ay=Unit.Hlocalcoord, Unit.Vlocalcoord
                
                if Unit.DamageLevel not in ArrowsDict.keys():

                    ArrowsDict[Unit.DamageLevel]={'x':[], 'y':[], 'u':[], 'v':[]}

                ArrowsDict[Unit.DamageLevel]['x'].append(x)
                ArrowsDict[Unit.DamageLevel]['y'].append(y)
                ArrowsDict[Unit.DamageLevel]['u'].append(ax-x)
                ArrowsDict[Unit.DamageLevel]['v'].append(ay-y)
        
    # Draw nodesGroup objects like societies and ...
    NodesObjects=_opr.NodesGroups.ObjManager.Objlst
    NodeGcol=f'rgba(127, 127, 127,1)'
    for node in _tqdm(NodesObjects,desc='Adding Vulnerables Area (NodesGroup)'):
        
        x=node.xGlobalList
        y=node.yGlobalList
        damage=node.isDamagedList
        DamageSource=node.DamageSource
        DamageSourceTag=node.DamageSourceTag 
        DamageSourceDose=node.DamageSourceDose
        DamageSourceType=node.DamageSourceType
        
        if damage==[]:
            damage=[False for i in x]
            DamageSource=[None for i in x]
            DamageSourceTag=[None for i in x]
            DamageSourceDose=[None for i in x]
            DamageSourceType=[None for i in x]
            
            
        Area=node.AreaList
        r=[(a/_math.pi)**0.5 for a in Area]
        Type=node.Type
        
        
        # Set The boundary
        if min(x)<minx: minx=min(x)
        if max(x)>maxx: maxx=max(x)
        if min(y)<miny: miny=min(y)
        if max(y)>maxy: maxy=max(y)       
        
        for x0,y0,R,dam,DamageSource,DamageSourceTag,DamageSourceDose,DamageSourceType in zip(x,y,r,damage,DamageSource ,DamageSourceTag ,DamageSourceDose ,DamageSourceType):

            Phi=[i/20*2*_math.pi for i in range(20)]
            x=[x0+R*_math.cos(phi) for phi in Phi]
            y=[y0+R*_math.sin(phi) for phi in Phi]
            
            fillDam=f'rgba(255, 0, 0,0.5)'
            fillUnDam=f'rgba(127, 127, 127,0.05)'
            fig.add_scatter(x=x,y=y,fill='toself',fillcolor=fillDam if (dam==True and raw==False) else fillUnDam,mode='lines',
                            line=dict(color=NodeGcol,width=1,
                            shape='spline',smoothing=0.9,simplify=False,),
                            hoverinfo='none',name='Vulnerable Object',showlegend=False,legendgroup=Type, visible='legendonly')
            
            fig.add_trace(_go.Scatter(x=[x0], y=[y0], mode='markers', name='Vulnerable Object',showlegend=False,legendgroup=Type,
                                      marker=dict(color=NodeGcol,size=2),
                                    
                                      hoverinfo='text',
                                      hovertext=f'Node of NodeGroup (tag= {node.tag}) at x={x0} and y={y0}'+
                                      f'<br>Area= {_math.pi*R**2} , \t Radius= {R} \t , \t Type= {Type}' +
                                      f'<br><br>Damage Source Name/s : {DamageSource}' +
                                      f'<br>Damage Source Tag/s: {DamageSourceTag}' +
                                      f'<br>Damage Source Dose/s: {DamageSourceDose}' +
                                      f'<br>Damage Source Type: {DamageSourceType}',
                                      hoverlabel=dict(bgcolor=f'rgba(0, 100, 0, 1)',
                                                bordercolor=f'rgba(255, 0, 0, 1)',
                                                font=dict(family='Balto',           #or other font family
                                                size=14,                            #or other size
                                                color=f'rgba(255, 255, 255, 1)')
                                                                ), visible='legendonly'
                                     )
                         )        

        
    #Add Damage Level Arrows
    ArrowsDict={i:ArrowsDict[i] for i in sorted(ArrowsDict)} #Sort LEvels from 1 to ...
    for dmlevel,values in _tqdm(ArrowsDict.items(),desc='Adding Damage Levels'):

        qfig=_go.FigureWidget(_ff.create_quiver(x=values['x'], y=values['y'], u=values['u'], v=values['v'],angle=9*3.1415/180, scale=1,arrow_scale=0.2,line=dict(width=2,color=Plcollist[dmlevel])))
        qfig.update_traces(hoverinfo='none',fill="toself",fillcolor=Plcollist[dmlevel],name=f'DamageLevel {dmlevel}',  showlegend=False,legendgroup=f'DamageLevel {dmlevel}', visible='legendonly')
        fig.add_trace(qfig.data[0])

       
        
    # Add single TanksData for legend
    fig.add_trace(_go.Scatter(x=[None], y=[None], mode='markers',
                              marker=dict(size=8, color=ColBound),
                              name='TanksData',showlegend=True,legendgroup='TanksData',))
                              
    # Add single liquid dispersion for legend
    if raw==False: fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                              line=dict(color=f'rgba(1, 1, 1,0.01)'),
                              name='Liquid Dispersion',showlegend=True,legendgroup='Liquid Dispersion', visible='legendonly'))
                              
    # Add single GasDispersions for legend
    if raw==False: fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                              line=dict(color=f'rgba(250, 250, 5,1)'),
                              name='GasDispersions',showlegend=True,legendgroup='GasDispersions', visible='legendonly'))
    
    # Add single Radiation for legend
    if raw==False: 
        for Rad in RadiationList:
            RadColor=f'rgba(250,50,0,{Rad/max(RadiationList)})'
            fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                                    line=dict(color=RadColor),
                                    name=f'Radiation{Rad}',showlegend=True,legendgroup=f'Radiation{Rad}', visible='legendonly'))

    # Add single OverPressure for legend
    if raw==False: 
        for OverP in OverPressureList:
            OverPColor=f'rgba(50,250,0,{OverP/max(OverPressureList)})'
            fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                                    line=dict(color=OverPColor),
                                    name=f'OverPressure{OverP}',showlegend=True,legendgroup=f'OverPressure{OverP}', visible='legendonly'))
                                  
    # Add single Damage Level Arrows for legend
    #DamageLevel 0
    if raw==False: 
        if ArrowsDict!={}:
            fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                                    line=dict(color='rgba'+Plcollist[0][3:-1]+', 0.3)'),
                                    name=f'DamageLevel {0}',showlegend=True,legendgroup=f'DamageLevel {0}', visible='legendonly'))
    #Other Damage Lavels
    if raw==False: 
        for dmlevel,values in ArrowsDict.items():
            fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                                    line=dict(color='rgba'+Plcollist[dmlevel][3:-1]+', 0.3)'),
                                    name=f'DamageLevel {dmlevel}',showlegend=True,legendgroup=f'DamageLevel {dmlevel}', visible='legendonly'))

    # Add single NodesGroups for legend
    TypeSet=set()
    
    for node in NodesObjects:
        TypeSet.add(node.Type)
    
    for Type in TypeSet:      
        fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                                  line=dict(color=NodeGcol),
                                  name='Vulnerable Object',showlegend=True,legendgroup=Type, visible='legendonly'))   

    #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
    fig.update_layout(title={'text': "Plant Units",'y':0.92,'x':0.15,'xanchor': 'center', 'yanchor': 'top'},title_font=dict(size=25, color='black'),
                     height=800,width=1000,)
    
    #
    
    #Set Scale of dimenstions to be equal
    fig.update_layout(showlegend=True)#,scene=dict( annotations=annotations, ))
    #print(fig) ,fig.update_layout(autosize=True) This feature cause that the value of fig size doesn't get back in below codes
    #print(fig[ 'layout']['height'])
    Ratio=float(str(fig[ 'layout']['height']))/float(str(fig[ 'layout']['width']))
    
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
            
            
    fig.update_xaxes(title_text='x',showline=True,linewidth=2, linecolor='black',range=[minx-0.05*L1, maxx+0.05*L1],title_font=dict(size=18, family='Courier', color='black')) #mirror=True
    fig.update_yaxes(title_text='y',showline=True,linewidth=2, linecolor='black',range=[miny-0.05*L2, maxy+0.05*L2],title_font=dict(size=18, family='Courier', color='black'))#,mirror=True
    
    if height!=None:
        fig.update_layout(height=height)
    if width!=None:
        fig.update_layout(width=width)

    if PlotMode==3:
        
        return _iplot(fig)
        
    elif PlotMode==2:
        
        image_filename='PlotUnits2D.html'
        _plot(fig,filename=image_filename, config = dict({'scrollZoom': True}))
        
    else:
        fig.show(config = dict({'scrollZoom': True}))

def PlotIndividualRisk( PlotMode=1, NodesGroupTag=1, NodesProbabilityList=[], ContorList=[], width=None, height=None):
    '''
    NodesGroupTag: Tag of the nodesgroup that want to see its damage probability
    NodesProbabilityList: list of the nodes damage probability values. 
    ContorList: list of contor values
    
    
    '''
    
    Plcollist=_PLcols.DEFAULT_PLOTLY_COLORS*20 #List of plotly Colors
    
    #Initial Figure Settings
    fig = _go.Figure()
    fig.update_layout(plot_bgcolor='white')


    #Plot Tanks
    minx,maxx,miny,maxy=_PlotTanks(fig,PlotDamagedColor=False)
    

    # Draw NodesGroup Individual risk
    tag=NodesGroupTag

    ngobj=_opr.NodesGroups.ObjManager.TagObjDict[tag]
    x=ngobj.xGlobalList
    y=ngobj.yGlobalList
    
    z=NodesProbabilityList if ContorList==[] else []
    
    colorscale=[[0.0, "white"],
               [0.2, "rgb(31,120,180)"],
               [0.4, "rgb(178,223,138)"],
               [0.6, "rgb(51,160,44)"],
               [0.8, "rgb(251,154,153)"],
               [1.0, "rgb(227,26,28)"]]   
               
    if ContorList!=[]:
    
        for prob in NodesProbabilityList:
            
            if prob<min(ContorList):
                z.append(0)
                continue
            
            if prob>max(ContorList):
                z.append(max(ContorList))
                continue
            
            z.append(prob)
        
        
        
        # for num,cont in enumerate(ContorList):
            # colorscale.append([cont/max(NodesProbabilityList),Plcollist[num]])
            
    
    fig.add_trace(_go.Contour(x=x, y=y, z=z,
                              colorscale=colorscale,
                              opacity=0.5,
                            #   colorscale='turbo',
                            #   contours_coloring='heatmap',
                              line_width=1,
                              showlegend=False,
                              legendgroup='Individual Risk',
                              contours=dict(type="levels",
                                            start=min(z) if ContorList==[] else min(ContorList),
                                            end=max(z) if ContorList==[] else max(ContorList),)
                             )
                  )


    # Add single Individual Risk for legend
    # fig.add_trace(_go.Scatter(x=[None], y=[None], mode='lines',
                              # marker=dict(size=8, color='red'),
                              # name='Individual Risk',showlegend=True,legendgroup='Individual Risk',)) 




    #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
    fig.update_layout(title={'text': "Plant Units",'y':0.92,'x':0.15,'xanchor': 'center', 'yanchor': 'top'},title_font=dict(size=25, color='black'),
                     height=800,width=1000,)    
                     
                     
    Ratio=float(str(fig[ 'layout']['height']))/float(str(fig[ 'layout']['width']))
    
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
            
            
    fig.update_xaxes(title_text='x',showline=True,linewidth=2, linecolor='black',range=[minx-0.05*L1, maxx+0.05*L1],title_font=dict(size=18, family='Courier', color='black')) #mirror=True
    fig.update_yaxes(title_text='y',showline=True,linewidth=2, linecolor='black',range=[miny-0.05*L2, maxy+0.05*L2],title_font=dict(size=18, family='Courier', color='black'))#,mirror=True

    if height!=None:
        fig.update_layout(height=height)
    if width!=None:
        fig.update_layout(width=width)    
    

    if PlotMode==3:
        
        return _iplot(fig)
        
    elif PlotMode==2:
        
        image_filename='PlotIndividualRisk.html'
        _plot(fig,filename=image_filename,config = dict({'scrollZoom': True}))
        
    else:
        fig.show(config = dict({'scrollZoom': True}))

def _PlotTanks(fig,PlotDamagedColor=True,raw=False):
    
    #raw: Boolean that if consider as True means that just only plot the plant without showing any damages or other events.

    Plcollist=_PLcols.DEFAULT_PLOTLY_COLORS*20 #List of plotly Colors
    Plcollist=['rgb(255, 0, 5)']+Plcollist[1:3]+Plcollist[4:]

    ColBound=f'rgba(0, 0, 0,1)' # Boundary Colors
    ColNodamage=f'rgba(250, 250, 250,0.2)' #Undamaged Colors
    ColDamaged=f'rgba(255, 0, 5,0.2 )' #Damaged Colors
    
    
    
    #Get All Defined Plant Units
    UnitObj=_opr.PlantUnits.ObjManager.Objlst
    
    
    minx=None
    maxx=None
    miny=None
    maxy=None
    
    for Unit in _tqdm(UnitObj,desc='Plotting ONGStorage Tanks'):
        
        # Onground Tanks
        if Unit.__class__==_opr.PlantUnits.ONGStorage:
            
            # Get Geometry and Location Data and the Other required data
            xc=Unit.Hlocalcoord
            yc=Unit.Vlocalcoord
            
            D=Unit.d_Storage
            
            tag=Unit.tag
            name=Unit.__class__.__name__
            outFlowname=Unit.OutFlowModelname
            DispSprdModelname=Unit.DispersionSpreadModelname
            DispSprdObj=Unit.DispersionSpreadModelObject
          
            PhysicalObjname=Unit.PhysicalEffectModelname
            PhysicalObj=Unit.PhysicalEffectObject
            
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
            fig.add_shape(type="circle", xref="x", yref="y", name=name,
                x0=xc-D/2, y0=yc-D/2, x1=xc+D/2, y1=yc+D/2,
                
                line_color=ColBound ,fillcolor='rgba'+Plcollist[Unit.DamageLevel][3:-1]+', 0.3)' if (Unit.isdamaged==True and PlotDamagedColor==True and Unit.DamageLevel!=None and raw==False) else ColNodamage,)
                # 'rgba'+Plcollist[Unit.DamageLevel][3:-1]+', 0.1)' if (Unit.DamageLevel!=None and Unit.DamageLevel!=0) else

            #Add Tanks Center Point and Data                
            fig.add_trace(_go.Scatter(x=[xc], y=[yc], mode='markers', name='TanksData',showlegend=False,legendgroup='TanksData',
                                      marker=dict(color=ColBound),
                                     
                                      hoverinfo='text',
                                      hovertext=f'{name} (tag= {tag}) and Substance= {_opr.Substance.ObjManager[Unit.SubstanceTag].name} (tag= {Unit.SubstanceTag})'+
                                      f'<br><br>Diameter= {D} \t <br>Damage Source= {Unit.DamageSource} \t <br>with Damage SourceTag= {Unit.DamageSourceTag} \t <br>Damage Level= {Unit.DamageLevel}, Damage Source Type= {Unit.DamageSourceType}, Damage Source Dose= {Unit.DamageSourceDose}' +
                                      f'<br><br>{"OutFlowModel: <br>"+outFlowname if outFlowname!=None else ""}' +
                                      f'<br><br>{"DispersionSpreadModel: <br>"+DispSprdModelname if DispSprdModelname!=None else ""}' +
                                      f'<br><br>{"PhysicalEffectModel: <br>"+PhysicalObjname if PhysicalObjname!=None else ""}',
                                      hoverlabel=dict(bgcolor=f'rgba(0, 0, 0, 1)',
                                                bordercolor=f'rgba(255, 0, 0, 1)',
                                                font=dict(family='Balto',           #or other font family
                                                size=14,                            #or other size
                                                color=f'rgba(255, 255, 255, 1)')
                                                                ),
                                     )
                         )
    return minx,maxx,miny,maxy
    
def PlotFragilities(StdNumber=3,NPoints=100, FragilityTagList=[],PlotMode=1, width=None, height=None):
    '''
    All Fragilities that are defined by the user, Are drawn using This Function
    FragilityTagList = list of fragilities tag that user want to plot
    '''

    stdN=StdNumber
    N=NPoints
    
    #Get All defined Fragilities
    FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict
    FragTagObjs={i:j for i,j in FragTagObjs.items() if i in FragilityTagList} if FragilityTagList!=[] else FragTagObjs


    #Calculate Range of random of random variables----------------------------------------------------
    x=[]    #Random Variables range
    for tag,FragObj in FragTagObjs.items():
        # print(tag)
        # print(FragObj.DistType)
        
        if FragObj.Title!='Fragility': continue
        
        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':
            minv=FragObj.mean-stdN*FragObj.StdDev
            maxv=FragObj.mean+stdN*FragObj.StdDev
            x=x+[minv+(maxv-minv)/N*x for x in range(N-1)]

    x=filter(lambda x:x>=0,x) #Only Positive Random Variables Have meaning    
    x=set(x) 
    x=list(x)
    x.sort()
    
    

    fig = _go.Figure() 
    #Calculate Probablity for each distribution and add it to fig-------------------------------------------------------- 
    
    for tag,FragObj in FragTagObjs.items():
        
        if FragObj.Title!='Fragility': continue

        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':

            y=[FragObj.GetProbability(x) for x in x]
            name=f'tag {tag}, Modename={FragObj.modename}'
            fillType='tozeroy'
            col1=f'rgba({_rnd.randint(1,255)},{_rnd.randint(1,255)},{_rnd.randint(1,255)},0.5)'
            col2=col1.replace('0.5)','0.1)')
            fig.add_scatter(x = x, y=y ,text=name,name=name,
                            marker=dict(color=col1),
                            showlegend=True, mode='lines',fill=fillType,
                            fillcolor=col2) 
            

    if x!=[]: #Means that we have Fragilities
    
        #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
        fig.update_xaxes(title_text='Random Variables',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, max(x)],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
        fig.update_yaxes(title_text='Probability',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, 1.05],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
        fig.update_layout(title={'text': "Fragilities",'y':0.9,'x':0.13,'xanchor': 'center', 'yanchor': 'top'},height=800)
        fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,bordercolor="Black", borderwidth=2))
        
        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)
        #fig.update_traces(hovertemplate="<b>%{text}</b><br><br>" +"Random Variable: %{x}<br>" +"Probability: %{y}<br>" +"<extra></extra>",)
        
    
        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='PlotFragilities.html'
            _plot(fig,filename=image_filename,config = dict({'scrollZoom': True}))
            
        else:
            fig.show(config = dict({'scrollZoom': True}))

    else:
        print('There is No fragility function to Draw!')



def PlotProbits(StdNumber=3,NPoints=100,ProbitTag=None,PlotMode=1,  width=None, height=None):
    '''
    All Fragilities that are defined by the user, Are drawn using This Function
    '''

    stdN=StdNumber
    N=NPoints
    
    #Get All defined Fragilities
    FragTagObjs=_opr.Fragilities.ObjManager.TagObjDict


    #Calculate Range of random of random variables----------------------------------------------------
    x=[]    #Random Variables range
    dx=None
    for tag,FragObj in FragTagObjs.items():
        # print(tag)
        # print(FragObj.DistType)
        if ProbitTag!=None and tag!=ProbitTag: continue
        if FragObj.Title!='Probit Funbction': continue
        
        
        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':
            minv=FragObj.mean-stdN*FragObj.StdDev
            maxv=FragObj.mean+stdN*FragObj.StdDev
            print('minv,maxv',minv,maxv)
            
            #Get the minimum distance between random values
            if dx==None:dx=(maxv-minv)/N*FragObj.Scale_Factor
            if (maxv-minv)/N*FragObj.Scale_Factor<dx: dx=(maxv-minv)/N*FragObj.Scale_Factor
            
            x=x+[(minv+(maxv-minv)/N*x)*FragObj.Scale_Factor for x in range(N-1)]
    
    #Fill Gaps
    x.sort()
    xx=[]
    for i,j in list(zip(x[0:-1],x[1:])):

        if abs(j-i)>dx: xx.extend([abs(min(i,j))+m*dx for m in range(int(abs(i-j)/dx)+1)])
        
    x=x+xx    
    
    x=filter(lambda x:x>=0,x) #Only Positive Random Variables Have meaning    
    x=set(x) 
    x=list(x)
    x.sort()
    # print('x=',x)


    
    

    fig = _go.Figure() 
    #Calculate Probablity for each distribution and add it to fig-------------------------------------------------------- 
    
    for tag,FragObj in FragTagObjs.items():
    
        if ProbitTag!=None and tag!=ProbitTag: continue
        if FragObj.Title!='Probit Funbction': continue

        if FragObj.DistType=='normal' or FragObj.DistType=='lognormal':

            y=[FragObj.GetProbability(x) for x in x]
            # print(y)
            name=f'Probit tag = {tag}'
            fillType='tozeroy'
            col1=f'rgba({_rnd.randint(1,255)},{_rnd.randint(1,255)},{_rnd.randint(1,255)},0.5)'
            col2=col1.replace('0.5)','0.1)')
            fig.add_scatter(x = x, y=y ,text=name,name=name,
                            marker=dict(color=col1),
                            showlegend=True, mode='lines',fill=fillType,
                            fillcolor=col2) 
            

    if x!=[]: #Means that we have Fragilities
    
        #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
        fig.update_xaxes(title_text='Random Variables',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, max(x)],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
        fig.update_yaxes(title_text='Probability',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, 1.05],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
        fig.update_layout(title={'text': "Probits",'y':0.9,'x':0.13,'xanchor': 'center', 'yanchor': 'top'})
        fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,bordercolor="Black", borderwidth=2))
        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)
        #fig.update_traces(hovertemplate="<b>%{text}</b><br><br>" +"Random Variable: %{x}<br>" +"Probability: %{y}<br>" +"<extra></extra>",)
        
    
        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='PlotProbits.html'
            _plot(fig,filename=image_filename,config = dict({'scrollZoom': True}))
            
        else:
            fig.show(config = dict({'scrollZoom': True}))
        
    else:
        print('There is No fragility function to Draw!')




def PlotHazard(PlotMode=1, width=None, height=None):
    '''
    The First Hazard Object that are defined by the user, is drawn using This Function
    '''

    
    #Get The first Hazard Object
    HazarbObj=_opr.Hazard.ObjManager.Objlst[0]


    #Get Hazard Curve Values----------------------------------------------------
    x=HazarbObj.Magnitude
    y=HazarbObj.Probabilities

    #Figure Settings -------------------------------------------------------- 
    fig = _go.Figure() 
   
    name='Defined Hazard'
    fillType='tozeroy'
    col1=f'rgba({_rnd.randint(1,255)},{_rnd.randint(1,255)},{_rnd.randint(1,255)},0.5)'
    col2=col1.replace('0.5)','0.1)')
    fig.add_scatter(x = x, y=y ,text=name,name=name,
                    marker=dict(color=col1),
                    showlegend=True, mode='lines',fill=fillType,
                    fillcolor=col2) 
            


    #Plotly Settings ---------------------------------------------------------------------------------------------------------------------------------------
    fig.update_xaxes(title_text='Magnitude',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, max(x)],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
    fig.update_yaxes(title_text='Probability',showline=True,linewidth=2, linecolor='black',mirror=True,range=[0, 1.05],title_font=dict(size=18, family='Courier', color='black'),showspikes=True)
    fig.update_layout(title={'text': "Hazard Curve",'y':0.92,'x':0.16,'xanchor': 'center', 'yanchor': 'top'},height=800,title_font=dict(size=22,  color='black'))
    fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="right",x=0.99,bordercolor="Black", borderwidth=2))
    if height!=None:
        fig.update_layout(height=height)
    if width!=None:
        fig.update_layout(width=width)
        
    
    if PlotMode==3:
        
            return _iplot(fig)
            
    elif PlotMode==2:
        
        image_filename='PlotHazard.html'
        _plot(fig,filename=image_filename,config = dict({'scrollZoom': True}))
        
    else:
        fig.show(config = dict({'scrollZoom': True}))
