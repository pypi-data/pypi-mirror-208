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


from opensrane.Misc._NewClass import _NewClass
from .ObjManager import *
from ._GlobalParameters import _GlobalParameters
import random as _rnd
import opensrane as _opr



class WindRose(_NewClass,_GlobalParameters):
    '''
    WindRose Class
    '''
    
    
    def __init__(self,tag,
                WindDayClassList=None,WindNightClassList=None,AlphaCOEFlist=None, 
                DayWindSpeedList=None,DayWindFreqMatrix=None,
                NightWindSpeedList=None,NightWindFreqMatrix=None):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        _GlobalParameters.__init__(self)
        
        
        self.WindDayClassList=WindDayClassList
        self.WindNightClassList=WindNightClassList
        self.AlphaCOEFlist=AlphaCOEFlist
        
        self.DayWindSpeedList=DayWindSpeedList
        self.DayWindFreqMatrix=DayWindFreqMatrix

        self.NightWindSpeedList=NightWindSpeedList
        self.NightWindFreqMatrix=NightWindFreqMatrix
        
        self.DayDirectProbability=None
        self.DayTheta=None
        self.DayCalmn=None
        
        self.NightDirectProbability=None
        self.NightTheta=None
        self.NightCalmn=None        

        self.wipeAnalysis()
    
    def wipeAnalysis(self):
        # properties that are defined in _GlobalParameters should also be reset
        self.wipeAnalysisGlobal()
        
        # properties that are not constant and among each analysis will change should be define here
        pass        
    
    
    def _CalcDirectionProbabilities(self):
        '''
        This Function Calculate the directions and their probabilities
        '''
        self.DayDirectProbability=[sum(freq) for freq in self.DayWindFreqMatrix] #the frequency of each direction
        self.NightDirectProbability=[sum(freq) for freq in self.NightWindFreqMatrix] #the frequency of each direction

        
        self.DayTheta=[i*360/len(self.DayDirectProbability) for i in range(len(self.DayDirectProbability))] #Corresponding Directions
        self.NightTheta=[i*360/len(self.NightDirectProbability) for i in range(len(self.NightDirectProbability))] 

        
        #Calculation of calmn condition for day----------------
        if sum(self.DayDirectProbability)>100: 
            #if summation of direction probabilities become greater than 100, then data will be normal 
            #to the 100 and calmn probability be ZERO!
            self.DayCalmn=0
            
            sm=sum(self.DayDirectProbability)
            self.DayWindFreqMatrix=[[i/sm*100 for i in freq] for freq in self.DayWindFreqMatrix]
            self.DayDirectProbability=[sum(freq) for freq in self.DayWindFreqMatrix]
        else:
            self.DayCalmn=100-sum(self.DayDirectProbability)
            
   
        #Calculation of calmn condition for Night---------------
        if sum(self.NightDirectProbability)>100: 
            #if summation of direction probabilities become greater than 100, then data will be normal 
            #to the 100 and calmn probability be ZERO!
            self.NightCalmn=0
            
            sm=sum(self.NightDirectProbability)
            self.NightWindFreqMatrix=[[i/sm*100 for i in freq] for freq in self.NightWindFreqMatrix]
            self.NightDirectProbability=[sum(freq) for freq in self.NightWindFreqMatrix]
        else:
            self.NightCalmn=100-sum(self.NightDirectProbability) 



        return ''
    
    
    def GetRandomWindِSample(self):
    

        #Check if CalcDirectionProbabilities didn't run yet, run it
        if self.DayDirectProbability==None or self.DayTheta==None:
            self._CalcDirectionProbabilities()
        
        #Get Sampled Day_Night condition
        if _opr.DateAndTime.ObjManager.Objlst==[]:
            raise ("Error: DateAndTime Object has not been defined yet!")
        
        #get Date Object            
        DateObj=_opr.DateAndTime.ObjManager.Objlst[0]
        
        #make a sample
        if DateObj.SampledisDay==None:
            raise ("Error: DateAndTime Object has not generated any sample yet!")
                
        Day_or_Night=DateObj.SampledisDay
        
        
        
        Day_or_Night='Day' if Day_or_Night=='Day' else 'Night'

        #Importing data to parameters
        AlphaCOEFlist=self.AlphaCOEFlist[:]

        if Day_or_Night=='Day':
            
            ClassList=self.WindDayClassList[:]
            SpeedList=self.DayWindSpeedList[:]
            WindFreqList=self.DayWindFreqMatrix[:]
            DirectionPrabab=self.DayDirectProbability[:]
            Thetalist=self.DayTheta[:]                     #[:] is very important sign to disconect parameter from the origonal reference
            Calmn=self.DayCalmn

        else:
            
            ClassList=self.WindNightClassList[:]
            SpeedList=self.NightWindSpeedList[:]
            WindFreqList=self.NightWindFreqMatrix[:]
            DirectionPrabab=self.NightDirectProbability[:]
            Thetalist=self.NightTheta[:]
            Calmn=self.NightCalmn
            
            
        #Calculate Wind Direction Cumulitative Summation
        CumDirProb=[DirectionPrabab[0]]+[sum(DirectionPrabab[0:i]) for i in range(2,len(DirectionPrabab)+1)]
        
        
        #For calm condition Calm Condition Data will be added to Last row of data
        if Calmn!=0 : 
            CumDirProb.append(100)
            WindFreqList.append([0]*len(WindFreqList[0]))
            Thetalist.append('Calmn Condition')
    
            
        RND=_rnd.random()*100  #Generate a Sample Value

        
        #The corresponding index of wind Direction
        DirRow=[r for r,val in enumerate(CumDirProb) if RND<=val][0] 
        WindDirection=Thetalist[DirRow]                               #The Wind Direction of Sample
        
        
        RND=RND-CumDirProb[DirRow-1] if DirRow>0 else RND
        DirFreqList=WindFreqList[DirRow]                                                         #WidRose Defined Values in sampled Direction
        CumSpeed=[DirFreqList[0]]+[sum(DirFreqList[0:i]) for i in range(2,len(DirFreqList)+1)]   #Cumulitative Wind Freq in Sampled Direction 



        #The corresponding index of wind Speed in Sampled Direction
        
        SpeedRow=[r for r,val in enumerate(CumSpeed) if RND<=val] 
        
        #Export Other Results
        if SpeedRow==[]:                   #means Calm Condition
            WindSpeed=0.01                 #to Avoid Formulas Error
            AlphaCOEF=None
            WindClass=None
            WindDirection=_rnd.uniform(0,360)
            isCalmn=True
        else:
            SpeedRow=SpeedRow[0]
            WindSpeed=SpeedList[SpeedRow]
            AlphaCOEF=AlphaCOEFlist[SpeedRow]
            WindClass=ClassList[SpeedRow]
            isCalmn=False
            
            
        self.WindClass=WindClass
        self.WindDirection=WindDirection
        if type(WindSpeed)==list:
            if len(WindSpeed)==1:
                WindSpeed=WindSpeed[0]
            elif len(WindSpeed)>=2:
                WindSpeed=_rnd.uniform(WindSpeed[0], WindSpeed[1])
                
        self.WindSpeed=WindSpeed
        self.AlphaCOEF=AlphaCOEF
        self.isCalmn=isCalmn
                

        return {'WindClass':WindClass, 'WindDirection':WindDirection,'WindSpeed':WindSpeed, 'AlphaCOEF':AlphaCOEF, 'isCalmn':isCalmn}

        
        
        
        
