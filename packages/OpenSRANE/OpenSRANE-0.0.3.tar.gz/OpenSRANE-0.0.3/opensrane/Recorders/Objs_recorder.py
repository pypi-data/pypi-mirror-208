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
import opensrane as _opr
import os as _os
import datetime as _dt
import _pickle as _pickle
from copy import deepcopy as _deepcopy
import gc as _gc


class Objs_recorder(_NewClass):
    '''
    
    This Object id for recording all of the objects in each scenario analysis
    tag= tag of the recorder
    filename: name of the file that data will be record in it
    SaveStep: Number of the steps of analysis that after that, data will be record on a file
    fileAppend: Does data append to a existing file or it reset existing data in the file name
    
    '''
    
    def __init__(self,tag,filename='',SaveStep=100,fileAppend=True):
         
        #---- Fix Part for each class __init__ ----
        ObjManager.Add(tag,self)
        _NewClass.__init__(self,tag)
        #------------------------------------------
        
        self.filename=filename
        self.SaveStep=SaveStep
        self.fileAppend=fileAppend
        
        if fileAppend==False:
            self._ResetRecorder()
        

        self.RecordedList=[] #List that store all recorded objects inside in each happend scenario as a dictionary and send it to pickle to save in file
        self.RecordCounter=0
        
        
    def Record(self):
        '''
        This function records all the objects and save them all in the entered filename
        '''

        self.RecordCounter +=1
        SaveStep=int(self.SaveStep)

        #If there is any damage then the data will be recorded
        if _opr.Analyze.ScenarioAnalyze.anydamage==True:
            

            CurrentScenarioDict={}
            #Get SubPackage all Objects
            CurrentScenarioDict={SubPackname:SubPackobj.ObjManager.Objlst for SubPackname,SubPackobj in _opr.Misc.GetModules() if SubPackname!='Recorders'}
            
            #Add all current object to Objects that are in memory
            self.RecordedList.append(_deepcopy(CurrentScenarioDict))

           
        return 0

    def SaveToFile(self,fileindex):

            
        #Create log file to record number of the analysis
        with open(self.filename+str(fileindex)+'.Log', "w") as f:
            f.write(f'Number of Analysis: {self.RecordCounter}')
        
        #Set the file name
        filename=self.filename+str(fileindex)+'.OPR'
        
        # Write data to the file    
        with open(filename, 'wb') as fileObj:
            _pickle.dump(self.RecordedList,fileObj,protocol=-1)
        
        
        #Clear memory
        self.RecordedList=[]
        #Set RecordCounter to zero
        self.RecordCounter=0
        

    def _MergeAndClear(self):

        filename=self.filename

        #Merge OPR Files------------------------------------------------------------------------------------
        AllScenarioList=[]
        for file in _os.listdir():
            if file[-3:]=='OPR' and file[:len(filename)]==filename and len(file)>len(filename+'.OPR'):
                
                # Read file
                with open(file, 'rb') as fileObj:
                    loaddict=_pickle.load(fileObj)
                    AllScenarioList =AllScenarioList +  loaddict if type(loaddict)==list else AllScenarioList
                #Remove file
                _os.remove(file)

        #Main file
        file=filename+'.OPR'
        
        #Check if append is true add main file scenarios to the recorded scenarios
        if self.fileAppend==True and _os.path.isfile(file)==True:
                # Read Main file
                with open(file, 'rb') as fileObj:
                    loaddict=_pickle.load(fileObj)
                
                AllScenarioList = loaddict+AllScenarioList  if type(loaddict)==list else AllScenarioList
        
        #Write to file
        with open(file, 'wb') as fileObj:
            _pickle.dump(AllScenarioList,fileObj,protocol=-1)

        
        #Merge Log files-------------------------------------------------------------------------------------
        AnalyzeNumber=0
        for file in _os.listdir():
            if file[-3:]=='Log' and file[:len(filename)]==filename and len(file)>len(filename+'.Log'):
                
                # Read file
                with open(file, 'r') as fileObj:
                    number=fileObj.read()
                    number=number.split()[-1]
                    AnalyzeNumber =AnalyzeNumber +  int(number)
                #Remove file
                _os.remove(file)        

        #Main file
        file=filename+'.Log'
        
        #Check if append is true add main file Number to the recorded number
        if self.fileAppend==True and _os.path.isfile(file)==True:
                # Read Main file
                with open(file, 'r') as fileObj:
                    number=fileObj.read()
                    number=number.split()[-1]
                    AnalyzeNumber =AnalyzeNumber +  int(number)
                
        #Write to file
        with open(file, 'w') as fileObj:
            fileObj.write(str(AnalyzeNumber))


    def _ResetRecorder(self):
        '''
        This function clear the created filename that records the objects
        '''
        #Remove all OPR files
        for file in _os.listdir():
            if file[-3:]=='OPR' and file[:len(self.filename)]==self.filename:
                _os.remove(file)

        #Remove all log files
        for file in _os.listdir():
            if file[-3:]=='Log' and file[:len(self.filename)]==self.filename:
                _os.remove(file)        
            

class Objs_recorder_loader():
    
    
    _ScenarioBank={}

    @staticmethod
    def loadScenarioBank(filename):
        
        '''
        This function Loads all recorded Scenarios into the memory
        Then you can Call each scenario using load1ScenarioOfBank method
        
        '''
        file=filename+".OPR"
        if file not in _os.listdir():
            print(f'{file} not found!')
            return -1

        global _ScenarioBank
        
        
        # Read file
        with open(file, 'rb') as fileObj:
            loaddict=_pickle.load(fileObj)
            _ScenarioBank =  loaddict if type(loaddict)==list else []
                    
            
        return len(_ScenarioBank)
      
    @staticmethod
    def load1ScenarioOfBank(ScenarioTag):
        
        '''
        This function Loads one scenario from loaded bank
        
        '''
        
        if '_ScenarioBank' not in globals(): 
            print('No Scenario bank has been loaded in the memory')
            return -1
    
        global _ScenarioBank

        #If entered tag be greater than what is recorded
        if ScenarioTag>len(_ScenarioBank)-1 : 
            print(f'Entered scenario tag ({ScenarioTag}) is greater than the maximum recorded tag ({len(_ScenarioBank)-1})')
            return -1
        
        scenarioDict= _ScenarioBank[ScenarioTag]
        
        #feed the subpackages
        for SubPackname,SubPackobj in _opr.Misc.GetModules():
            
            if SubPackname!='Recorders' and SubPackname in scenarioDict.keys():
                #replace each subpackage Objlst, Taglst, TagObjDict with what are available in the recorded scenario
                SubPackobj.ObjManager.Objlst=scenarioDict[SubPackname] if scenarioDict!={} else []
                SubPackobj.ObjManager.Taglst=[obj.tag for obj in SubPackobj.ObjManager.Objlst]
                SubPackobj.ObjManager.TagObjDict={obj.tag:obj for obj in SubPackobj.ObjManager.Objlst}
        
        scenarioDict={}
        
        return 0

    @staticmethod
    def ClearScenarioBank():
        '''
        this funtion clear loaded scenario bank from the memory
        '''
        global _ScenarioBank
        
        # if '_ScenarioBank' in globals(): del _ScenarioBank
        _ScenarioBank={}
        _gc.collect()        
        
