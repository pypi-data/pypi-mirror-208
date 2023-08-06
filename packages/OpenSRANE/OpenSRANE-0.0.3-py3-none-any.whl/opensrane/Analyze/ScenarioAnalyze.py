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
import random as _rnd
from ._Sampling import _Sampling
from ._ZeroLevel import _ZeroLevel
from ._Frag_OutFlow import _Frag_OutFlow
from ._DispSprd import _DispSprd
from ._PhysicalAssign import _PhysicalAssign
from ._PhysicalEffects import _PhysicalEffects
from ._Prob_OutFlow import _Prob_OutFlow
from ._NodesGroupsVulnerability import _NodesGroupsVulnerability
from tqdm import tqdm as _tqdm
import multiprocessing as _mp

class ScenarioAnalyze():
    
    anydamage=None                      #A parameter that shows does the analysis encounter with any damage or not

    def UniAnalyze(SavetoFile=True,fileindex=0):
        
        '''
        SavetoFile: For recorder objects it is emphasize that record data to a file or not (For unianalysis it is yes but for multiple analysis it should be no till after finishing the analysis in one time data be stored) (For objs recorder it will be save and it doesn't have any effect on them)

        fileindex: is an integer that will be add to the end of the filename to save in seperate file (For unianalysis it should be 0)

        '''
        
        #Clear previous analysis results
        _opr.Misc.wipeAnalysis()             
        
        #------------------------ First Part: Read Defined Objects -------------------------------------------#
       
                
        #Get All Plant Units
        AllUnits=_opr.PlantUnits.ObjManager.Objlst
        

        #---------------------------------- Second Part: Analyze -------------------------------------------#
        
        #Create Samples of Random Variables
        _Sampling.Sample()

        #Perform ZeroLevel Analysis
        _ZeroLevel.Analyze() 
        
        #Last Level of damage 
        LastLevel=0
                
        #Check if Any damage happened
        if True in [i.isdamaged for i in AllUnits]:

            ScenarioAnalyze.anydamage=True
        
            #Calculate OutFlow of Materials for Damaged Elements under Natural Hazards Using Fragilities
            Results=_Frag_OutFlow.Analyze() #Perform OutFlow Analysis
            
            #Domino Loop
            while True:
                        
                #Calculate Dispersion of Materials for Damaged Elements
                _DispSprd.Analyze() #Perform Dispersion Analysis
                
                #Assign Physical event to each unit Object according outflow type and physical models that defined with a probability distribution
                _PhysicalAssign.Analyze()   
                
                #Calculate Physical Effects that Happens After Physical Events on the other undamaged units
                _PhysicalEffects.Analyze()    
                
                #Check if there is any new damaged unit in the last domino chain
                CurrentMaxLevel=max([i.DamageLevel for i in AllUnits if i.DamageLevel!=None])
                if CurrentMaxLevel==LastLevel:
                    break
                
                #Set the last level of damaged elements
                LastLevel=CurrentMaxLevel
                
                #Calculate OutFlow of Materials for Damaged Elements under physical effects using Probit Functions
                Results=_Prob_OutFlow.Analyze() #Perform OutFlow Analysis from probit models                

                
            #Calculate the Vulnerable regions vulnerabilities, like population areas, grean and environmental areas and totally areas that defined by NodesGroups objjecs
            Results=_NodesGroupsVulnerability.Analyze()
        
        else:
            ScenarioAnalyze.anydamage=False
        #---------------------------- LastPart : Record Scenario -----------------------------------------------------------------#
        #Do the recordings for all Objs_recorder objects
        [obj.Record() for obj in _opr.Recorders.ObjManager.Objlst]
        
        #Save the recorded data just for recorder objects
        if SavetoFile==True:
            [obj.SaveToFile(fileindex) for obj in _opr.Recorders.ObjManager.Objlst]
            [obj._MergeAndClear() for obj in _opr.Recorders.ObjManager.Objlst]
        
        
        
        
    def MultiAnalysis(AnalysisNumber=100,isParallel=False,fileindex=0):
        
        '''
        This function implement multiple scenario analysis and record results
        AnalysisNumber: Number of analysis that user intend to do by this function
        ResetRecorder: Does the function clear the recorder file and record scenarios from zero or add new analysed scenarios to the end of the current file
        
        fileindex: is an integer that will be add to the end of the filename to save in seperate file
        '''
        
        #Do the analysis
        for i in _tqdm(range(AnalysisNumber)):
            _opr.Analyze.ScenarioAnalyze.UniAnalyze(SavetoFile=False)  #Do a unit scenario analysis and do not save for recorder objects and after the analysis in next lines the data will be store in the file (For objs recorder it will be save and it doesn't have any effect on them)
            # FR=[obj.DamageLevel for obj in _opr.PlantUnits.ObjManager.Objlst]
            # FR=[obj.DamageLevel for obj in _opr.PlantUnits.ObjManager.Objlst]
            # print(FR) #to see the damage level of objects in the ith analyzed scenario
            
        [obj.SaveToFile(fileindex) for obj in _opr.Recorders.ObjManager.Objlst] #Save the recorded data just for recorder objects   
        
        if isParallel==False:
            #Merge all created files and remove them and just put the filnal file
            [obj._MergeAndClear() for obj in _opr.Recorders.ObjManager.Objlst] 

    def MultiParallel(AnalysisNumber=100, NumberOfProcessors=3, RecorderSaveStep=5000):
        
        '''
        
        REMEMBER: The only way to use this command is to call it inside "if __name__='__main__': " 
        
        RecorderSaveStep: if user didn't define Objs_recorder then the RecorderSaveStep will be use as save step But_
                          if Objs_recorder were define its save step will be consider as savestep
        '''

        #For Recorder objects if append is false the append should be True 
        # and file should be remove here manually to avoid multipe file removing
        for obj in _opr.Recorders.ObjManager.Objlst:
            if obj.__class__.__name__=='recorder':
                if obj.fileAppend==False:
                    obj.fileAppend==True
                    obj._Deletefile()

            if obj.__class__.__name__=='Objs_recorder':
                if obj.fileAppend==False:
                    obj.fileAppend==True
                    obj._ResetRecorder()            


        #Set SaveStep
        SaveStep=None
        for obj in _opr.Recorders.ObjManager.Objlst:
            if obj.__class__.__name__=='Objs_recorder':
                SaveStep=int(obj.SaveStep)
                break
        
        #Check Number of CPUs        
        NOP=_mp.cpu_count()
        
        if NumberOfProcessors<NOP:
            NOP=NumberOfProcessors
        
        #Set the save step:
        if SaveStep==None: SaveStep=int(RecorderSaveStep)

        #Set Number of Analysis for each CPU
        AnalyzeList=AnalysisNumber/SaveStep if AnalysisNumber%SaveStep==0 else int(AnalysisNumber/SaveStep)+1
        AnalyzeList=[SaveStep for i in range(int(AnalyzeList))]
        
        #Set number of CPUs    
        pool = _mp.Pool(NOP)
        
        #Set Analyze
        print('Analysis Number of each core: ',AnalyzeList)
        pool.starmap(_opr.Analyze.ScenarioAnalyze.MultiAnalysis, [(AnalyseNumber,True,fileindex) for fileindex,AnalyseNumber in enumerate(AnalyzeList)])
        
        pool.close()

        #Merge all created files and remove them and just put the filnal file
        [obj._MergeAndClear() for obj in _opr.Recorders.ObjManager.Objlst] 


