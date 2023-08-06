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
import plotly.express as _px
import plotly.graph_objects as _go
import math as _math
from plotly.offline import iplot as _iplot
from plotly.offline import plot as _plot


class PlotPP():


    def DamageLevel_ExpectedLoss(PPResults=None,yaxistype='log',PlotMode=1,height=None,width=None, ):
        
        '''
        This function plots the expected loss of containment in each damage level

        PPResults are the results of ObjsRecorderPP or RecorderPP analysis
        
        yaxistype is the type of the yaxis ['linear', 'log', 'date', 'category','multicategory']

        '''
        dmloc=PPResults['Damagelevel_eLOC']

        fig = _px.bar(x=list(dmloc.keys()), y=list(dmloc.values()), labels={'x':'Damage level', 'y':'Expected liquid loss of Containment (kg)'},  opacity=0.75)

        #set range for lof type
        yaxisrange=None
        if yaxistype=='log':
            miny=min(list(dmloc.values()))
            #To prevent sending zero for log function
            if miny==0:
                sortlis=list(dmloc.values())
                sortlis=list(set(sortlis))
                sortlis.sort()
                miny=sortlis[1]

            miny=int(_math.log10(miny))-1

            maxy=max(list(dmloc.values()))
            maxy=int(_math.log10(maxy))+1

            yaxisrange=[miny,maxy]              #in log type plotly consider the entered values as power of ten

        fig.update_layout(
            title_text='Expected loss of containment in each damage level', # title of plot
            bargap=0.01, # gap between bars of adjacent location coordinates
            plot_bgcolor='white', 
            yaxis=dict(type=yaxistype,range=yaxisrange, showline=True, linecolor='black',linewidth=2),
            xaxis=dict(type='linear',showline=True, linecolor='black',linewidth=2)
        )
        
        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)        

        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='DamageLevel_ExpectedLoss.html'
            _plot(fig,filename=image_filename)
            
        else:
            fig.show()

    def Unit_ZeroLevel_DamageProb(PPResults=None,yaxistype='log',PlotMode=1,height=None,width=None,):
        
        '''
        This function plots each plant unit damage probability in zero level

        PPResults are the results of ObjsRecorderPP or RecorderPP analysis

        yaxistype is the type of the yaxis ['linear', 'log', 'date', 'category','multicategory']
        
        '''
        zerdamp=PPResults['UnitsZeroDamageProb']

        fig = _px.bar(x=list(zerdamp.keys()), y=list(zerdamp.values()), labels={'x':'Unit tag', 'y':'probability of damage in zero level'},  opacity=0.75)

        #set range for lof type
        yaxisrange=None
        if yaxistype=='log':
            miny=min(list(zerdamp.values()))
            #To prevent sending zero for log function
            if miny==0:
                sortlis=list(zerdamp.values())
                sortlis=list(set(sortlis))
                sortlis.sort()
                miny=sortlis[1]

            miny=int(_math.log10(miny))-1

            yaxisrange=[miny,0]              #in log type plotly consider the entered values as power of ten


        fig.update_layout(
            title_text='Expected unit zero level damage', # title of plot
            bargap=0.01, # gap between bars of adjacent location coordinates
            plot_bgcolor='white',
            yaxis=dict(type=yaxistype,showline=True, linecolor='black',linewidth=2,range=yaxisrange),
            xaxis=dict(type='linear',showline=True, linecolor='black',linewidth=2), 
        )

        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)        

        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='Unit_ZeroLevel_DamageProb.html'
            _plot(fig,filename=image_filename)
            
        else:
            fig.show()

    def Fragilities_Probits_Probability(PPResults=None,yaxistype='log',PlotMode=1,height=None,width=None,):
        
        '''
        This function plots each fragility and probit happening probability

        PPResults are the results of ObjsRecorderPP or RecorderPP analysis

        yaxistype is the type of the yaxis ['linear', 'log', 'date', 'category','multicategory']
        
        '''
        FragProbHapp=PPResults['ProbOfFragilities']

        fig = _px.bar(x=list(FragProbHapp.keys()), y=list(FragProbHapp.values()), labels={'x':'Fragility tag', 'y':'probability of Fragility Happening'},  opacity=0.75)

        #set range for lof type
        yaxisrange=None
        if yaxistype=='log':
            miny=min(list(FragProbHapp.values()))
            #To prevent sending zero for log function
            if miny==0:
                sortlis=list(FragProbHapp.values())
                sortlis=list(set(sortlis))
                sortlis.sort()
                miny=sortlis[1]

            miny=int(_math.log10(miny))-1

            yaxisrange=[miny,0]              #in log type plotly consider the entered values as power of ten

        fig.update_layout(
            title_text='Expected Fragility/Probit happening', # title of plot
            bargap=0.01, # gap between bars of adjacent location coordinates
            plot_bgcolor='white',
            yaxis=dict(type=yaxistype,showline=True, linecolor='black',linewidth=2,range=yaxisrange),
            xaxis=dict(type='linear',showline=True, linecolor='black',linewidth=2) 
        )

        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)        

        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='Fragilities_Probits_Probability.html'
            _plot(fig,filename=image_filename)
            
        else:
            fig.show()


    def Expected_Total_LOC(PPResults=None,yaxistype='log',PlotMode=1,height=None,width=None,):
        
        '''
        This function plots expected total loss of containment

        PPResults are the results of ObjsRecorderPP or RecorderPP analysis

        yaxistype is the type of the yaxis ['linear', 'log', 'date', 'category','multicategory']
        
        '''

        bins,hist,probloc=PPResults['LOC_bins_hist_probloc']
        TotalLOCList=PPResults['TotalLOCList']

        bins=[(i+j)/2 for i,j in zip(bins[:-1],bins[1:])] #to get the average of the data (length of the bins is always one value greater than hist and probloc)


        fig = _px.histogram(x=TotalLOCList, nbins=400,log_y=True,log_x=False,width=700,height=600,histnorm='probability',
                            labels={'x':'Totla Loss (kg)', 'y':'Probability'},opacity=0.75)

         #set range for lof type
        yaxisrange=None
        if yaxistype=='log':
            probloc=list(set(probloc))
            probloc.sort()
            if probloc[0]==0:probloc.pop(0)
            miny=min(probloc)
            miny=int(_math.log10(miny))-1
            yaxisrange=[miny,0]              #in log type plotly consider the entered values as power of ten


        fig.update_layout(bargap=0.2,
                          plot_bgcolor='white', 
                          yaxis=dict(type=yaxistype,showline=True, linecolor='black',linewidth=2,range=yaxisrange),
                          xaxis=dict(type='linear',showline=True, linecolor='black',linewidth=2))
        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)        

        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='Expected_Total_LOC.html'
            _plot(fig,filename=image_filename)
            
        else:
            fig.show()

        # fig = px.bar(x=bins, y=hist, labels={'x':'Totla Loss', 'y':'count'},  opacity=0.75)
        # fig.update_layout(
        #     title_text='Sampled Results', # title of plot
        #     bargap=0.01, # gap between bars of adjacent location coordinates
        # )
        # fig.show()
        # fig = px.bar(x=bins, y=probloc, labels={'x':'Totla Loss', 'y':'Probability'},  opacity=0.75)
        # fig.update_layout(
        #     title_text='Sampled Results', # title of plot
        #     bargap=0.01, # gap between bars of adjacent location coordinates
        # )
        # fig.show()

    def ScenarioProbability(PPResults=None,yaxistype='log',DamageLevel=[],ScenarioList=[],PlotMode=1,height=None,width=None,):

        '''
        This function plots Scenarios versus their probability value in all damage levels

        PPResults are the results of ObjsRecorderPP or RecorderPP analysis
        
        DamageLevel = List of damage level that user want to watch the results

        ScenarioList=List of scenarios that want to be shown in graph. (for Empty it means that plot all scenarios)

        yaxistype is the type of the yaxis ['linear', 'log', 'date', 'category','multicategory']

        '''

        ScenProb=PPResults['ScenariosProbability']
        DamLvlScenDict=PPResults['Damagelevel_Scenario_Dict']

        if DamageLevel!=[]:
            ScenLevel=[]
            [ScenLevel.extend(scenlist) for dmlvl,scenlist in DamLvlScenDict.items() if dmlvl in DamageLevel]
            ScenProb={scen:prob for scen,prob in ScenProb.items() if scen in ScenLevel}
        
        if ScenarioList!=[]:
            ScenProb={scen:prob for scen,prob in ScenProb.items() if scen in ScenarioList}

        fig=_go.Figure()
        fig.add_scatter(y=list(ScenProb.values()),mode='lines',marker=dict(color='red'),line=dict(color='blue'),
                        hoverinfo='text',
                        hovertext=[f'Scenario Name = {key}<br>Probability = {val}' for key,val in ScenProb.items()],
                        hoverlabel=dict(bgcolor='gray',font=dict(size=14,color='yellow')))

         #set range for lof type
        yaxisrange=None
        if yaxistype=='log':
            miny=min(list(ScenProb.values()))
            miny=int(_math.log10(miny))-1
            yaxisrange=[miny,0]              #in log type plotly consider the entered values as power of ten

        fig.update_layout(yaxis=dict(type=yaxistype,showline=True, linecolor='black',linewidth=2,title='Probability',titlefont=dict(family='Balto', size=16, color='black'),range=yaxisrange),#type['-', 'linear', 'log', 'date', 'category','multicategory']
                        xaxis=dict(type='linear',showline=True, linecolor='black',linewidth=2,title='Scenario',titlefont=dict(family='Balto', size=16, color='black'),),
                        plot_bgcolor='white', )
        if height!=None:
            fig.update_layout(height=height)
        if width!=None:
            fig.update_layout(width=width)        

        if PlotMode==3:
        
            return _iplot(fig)
            
        elif PlotMode==2:
            
            image_filename='ScenarioProbability.html'
            _plot(fig,filename=image_filename)
            
        else:
            fig.show()
        # fig.update_xaxes(dict(zerolinecolor="black",
        #                       title='x',
        #                       titlefont=dict(family='Balto', size=18, color='black'),
        #                             ))
        # fig.update_yaxes(dict(zerolinecolor="black",
        #                       title='y',
        #                       titlefont=dict(family='Balto', size=18, color='black'),
        #                             ))


        

