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
from tqdm import tqdm as _tqdm
import multiprocessing as _mp
import numpy as _np
import os as _os

class ObjsRecorderPP():
    
   
    def Analyze(ObjsRecorer_Filename='',Number_Of_LOC_Histogram_Bins=100):
        
        '''
        ObjsRecorer_Filename: Name of the file that objects are recorded
        '''
        #If user didn't define any file 
        if ObjsRecorer_Filename=='':
            print('No file has been defined!')
            return
        
                
        #Define variables
        DamagedLevelList=[]     #list of the plant units Damage level list, each value is a Dictionary of Damage level of the plant units for each recorded scenario
        FragilityTagList=[]     #List of the plant units happend fragility tag Dictionaries, 
        LOCList=[]              #List of the PlantUnits tag and max Loss of Containment value Dictionary
        NodesGroupDamageList=[] #List of NodesGroup isDamaged Dict, each Dictionary is NodesGroupTag and corresponding Damagelist
        NodesGroupTypeDict={}   #Dictionray of each NodesGroup object that keys are tag of nodes group and values are the type of the nodes group
        NodesGroupDamProb={}    #Dictionray of each NodesGroup object that keys are tag of nodes group and values are the probability of their damage
        NodesGroupRadiationAveDict={}  #Dictionary of NodesGroup Radiation Data, and keys is Nodes Group tag and value is the list of Radiation values Average 
        NodesGroupOverPressureAveDict={}  #Dictionary of NodesGroup OverPressure Data, and keys is Nodes Group tag and value is the list of OverPressure values Average
        NodesGroupOVPProbAveDict={}     #Dictionary of NodesGroup OverPressure corresponding Probit Data, and keys is Nodes Group tag and value is the list of Probit(OverPressure) values Average 
        NodesGroupRadProbAveDict={}     #Dictionary of NodesGroup Radiation Probit Data, and keys is Nodes Group tag and value is the list of Probit(Radiation) values Average
        UnitsZeroDamageProb={}  #Probability of each PlantUnit zero level damage
        ProbOfFragilities={}    #Probability of each fragility or probit happening or governing
        DmglvlLOC={}            #Damagelevel and corresponding expected loss of containment
        HazardMagnitude=[]      #List of the hazard tags and magnitudes (tag as key and magnitude as value)
        ScenNameDamLvlDict={}   #Dictionary that its key is Scenario name and the value is its corresponding Damage level Dictionary

        NodesGroupRadiationList=[]     #list of NodesGroup Radiation Data, key: NodesGroup tag and value:Radiation Value (Just to get data)
        NodesGroupOverPressureList=[]  #list of NodesGroup OverPressure List, key: NodesGroup tag and value:Radiation Value
        NodesGroupOVPProbitList=[]
        NodesGroupRadProbitList=[]

        file=ObjsRecorer_Filename+'.Log'

        #check if file exist
        files=_os.listdir()

        if file not in files:
            print(f'{file} not found and not loaded!')
            return -1  

        if ObjsRecorer_Filename+'.OPR' not in files:
            print(f'{ObjsRecorer_Filename +".OPR"} not found and not loaded!')
            return -1           
        

        #Get Total Number of Analysis
        with open(file, 'r') as fileObj:
            TotalScenario=fileObj.read()
            TotalScenario=int(TotalScenario.split()[-1])


        #Load Scenario Bank
        NumberOfScenarios=_opr.Recorders.Objs_recorder_loader.loadScenarioBank(ObjsRecorer_Filename)

        #Star Opening all recorded files to export data
        for scenariotag in range(NumberOfScenarios):

            #Load Scenario
            _opr.Recorders.Objs_recorder_loader.load1ScenarioOfBank(scenariotag)

            #Fill variables for loaded scenario
            DamagedLevelList.append({i.tag:i.DamageLevel for i in _opr.PlantUnits.ObjManager.Objlst})
            FragilityTagList.append({i.tag:i.DamageFragilityTag for i in _opr.PlantUnits.ObjManager.Objlst})
            LOCList.append({i.tag:(i.OutFlowModelObject.TotalMassLiquid_Release if i.OutFlowModelObject!=None else None) for i in _opr.PlantUnits.ObjManager.Objlst})
            NodesGroupDamageList.append({NG.tag:([(0 if i==False else 1) for i in NG.isDamagedList] if NG.isDamagedList!=[] else [0]*len(NG.xGlobalList)) for NG in _opr.NodesGroups.ObjManager.Objlst})
            NodesGroupRadiationList.append({NG.tag:NG.Radiation_Intensity for NG in _opr.NodesGroups.ObjManager.Objlst} )
            NodesGroupOverPressureList.append({NG.tag:NG.OverPressure_Intensity for NG in _opr.NodesGroups.ObjManager.Objlst})
            NodesGroupOVPProbitList.append({NG.tag:NG.OverPressure_Probit for NG in _opr.NodesGroups.ObjManager.Objlst})
            NodesGroupRadProbitList.append({NG.tag:NG.Radiation_Probit for NG in _opr.NodesGroups.ObjManager.Objlst})
            HazardMagnitude.append({i.tag:float(i.SampledMagnitude) for i in _opr.Hazard.ObjManager.Objlst})
        
        #Remove loaded scenario
        _opr.Recorders.Objs_recorder_loader.ClearScenarioBank()

        #Modify NodesGroup Radiation and overpressure Dictionaries in better format
        NodesGroupRadiationAveDict={NG.tag:[0 for i in NG.xGlobalList] for NG in _opr.NodesGroups.ObjManager.Objlst}
        NodesGroupOverPressureAveDict={NG.tag:[0 for i in NG.xGlobalList] for NG in _opr.NodesGroups.ObjManager.Objlst}
        NodesGroupOVPProbAveDict={NG.tag:[0 for i in NG.xGlobalList] for NG in _opr.NodesGroups.ObjManager.Objlst}
        NodesGroupRadProbAveDict={NG.tag:[0 for i in NG.xGlobalList] for NG in _opr.NodesGroups.ObjManager.Objlst}
        
        #sum values
        for Dict in NodesGroupRadiationList:
            for NGtag in Dict.keys():
                NodesGroupRadiationAveDict[NGtag]=[i+j for i,j in zip(Dict[NGtag],NodesGroupRadiationAveDict[NGtag])]
        
        for Dict in NodesGroupOverPressureList:
            for NGtag in Dict.keys():
                NodesGroupOverPressureAveDict[NGtag]=[i+j for i,j in zip(Dict[NGtag],NodesGroupOverPressureAveDict[NGtag])]

        for Dict in NodesGroupOVPProbitList:
            for NGtag in Dict.keys():
                NodesGroupOVPProbAveDict[NGtag]=[i+j for i,j in zip(Dict[NGtag],NodesGroupOVPProbAveDict[NGtag])]

        for Dict in NodesGroupRadProbitList:
            for NGtag in Dict.keys():
                NodesGroupRadProbAveDict[NGtag]=[i+j for i,j in zip(Dict[NGtag],NodesGroupRadProbAveDict[NGtag])]

        #Convert above values to average
        for NGtag in NodesGroupRadiationAveDict.keys():
            NodesGroupRadiationAveDict[NGtag]=[i/TotalScenario for i in NodesGroupRadiationAveDict[NGtag]]
            NodesGroupOverPressureAveDict[NGtag]=[i/TotalScenario for i in NodesGroupOverPressureAveDict[NGtag]]
            NodesGroupOVPProbAveDict[NGtag]=[i/TotalScenario for i in NodesGroupOVPProbAveDict[NGtag]]
            NodesGroupRadProbAveDict[NGtag]=[i/TotalScenario for i in NodesGroupRadProbAveDict[NGtag]]
        

        #Modify LOCList to maximum loss value or 0
        LOCList=[{tag:(max(loss) if loss!=None else 0) for tag,loss in LossDic.items()} for LossDic in LOCList]
        #NodesGroupTypeDict
        NodesGroupTypeDict={NG.tag:NG.Type for NG in _opr.NodesGroups.ObjManager.Objlst}

        #Create Scenario Name And Damage level dicttionary
        for dmlvl in DamagedLevelList:
            ScenNameDamLvlDict["-".join(ObjsRecorderPP._LevelList(dmlvl))]=dmlvl

        #Calculate some probabilities from above results
        #------ Probability of Units Zero Level Damage
        UnitsZeroDamageProb={obj.tag:0 for obj in _opr.PlantUnits.ObjManager.Objlst}
        for DamLevelDict in DamagedLevelList:
            for tag,DamLev in DamLevelDict.items() :
                if DamLev==0: UnitsZeroDamageProb[tag]=UnitsZeroDamageProb[tag]+1

        #convert to probability
        UnitsZeroDamageProb={tag:DamLev/TotalScenario for tag,DamLev in UnitsZeroDamageProb.items()}

        #------ Probability of happening Fragilities and probits
        ProbOfFragilities={obj.tag:0 for obj in _opr.Fragilities.ObjManager.Objlst}
        for FragDict in FragilityTagList:
            for Fragtag in FragDict.values() :
                if Fragtag!=None: ProbOfFragilities[Fragtag]=ProbOfFragilities[Fragtag]+1

        #convert to probability
        ProbOfFragilities={tag:Num/TotalScenario for tag,Num in ProbOfFragilities.items()}

        #----Probability of Loss of Containment 
        ListOfLoc=[sum(list(LOCDIC.values())) for LOCDIC in LOCList]
        
        minLoc=min([i for i in ListOfLoc if i!=0])
        maxLoc=max([i for i in ListOfLoc if i!=0])
        nbins=Number_Of_LOC_Histogram_Bins
        hist, bins=_np.histogram(ListOfLoc,bins=[minLoc+(maxLoc-minLoc)/nbins*i for i in range(nbins+1)]) #length of the bins always should be one more than length of the hist
        probloc=[i/TotalScenario for i in hist] 


        #----Damagelevel and corresponding expected loss of containment
        for dam,loc in zip(DamagedLevelList,LOCList):
            for tag,dmlvl in dam.items():
                if (dmlvl not in list(DmglvlLOC.keys()) and dmlvl!=None):
                    DmglvlLOC[dmlvl]=0
                if (loc[tag]!=None and dmlvl!=None):
                    DmglvlLOC[dmlvl]=DmglvlLOC[dmlvl]+loc[tag]
                
        #convert to expected Value
        for dmlvl,loc in DmglvlLOC.items():
            DmglvlLOC[dmlvl]=loc/TotalScenario

        #----NodesGroupDamProb calculate each nodesgroup damage probability at each node
        #calculate nodesgroup tag and number of the nodes
        NodesGroupDamageList=[i for i in NodesGroupDamageList if i!={}]
        for NG in NodesGroupDamageList:
            
            NGtag=list(NG.keys())[0]
            

            #If nodes not in the NodesGroupDamProb add it as new and if is, add values to its values
            if NGtag not in list(NodesGroupDamProb.keys()):
                NodesGroupDamProb[NGtag]=NG[NGtag]
            else:
                NodesGroupDamProb[NGtag]=[i+j for i,j in zip(NodesGroupDamProb[NGtag],NG[NGtag])]


        #convert to expected Value
        for NG in NodesGroupDamProb.keys():
            NodesGroupDamProb[NG]=[i/TotalScenario for i in NodesGroupDamProb[NG]]

        
        #------ Probability of Damage levels and scenarios and subscenarios and Scenarios analyze number
        Results={} #Store scenario and number of happening (ScenariosProbability)
        ScenariosAnalyzeNumbers={} #Store scenario(key)  and number of alnazed scenarios list (Value)
        DamlvlScenDict={}   #Dictionary of damage level (key) and corresponding Scenarios set (Value)
        for ScenarioNum,damagelistrow in enumerate(DamagedLevelList):
            LevelList=ObjsRecorderPP._LevelList(damagelistrow)
            LevelList=['-'.join(LevelList[:i])  for i in range(1,len(LevelList)+1)]
            #fill DamlvlScenDict
            for lvl,name in enumerate(LevelList):
                if lvl not in DamlvlScenDict.keys():
                    DamlvlScenDict[lvl]=set([name])
                else:
                    DamlvlScenDict[lvl].update([name])

            #Fill Results for ScenariosProbability
            if LevelList!=[]: 
                
                for i in  LevelList:
                    if i not in Results.keys():
                        Results[i]=1
                    else:
                        Results[i]=Results[i]+1
            
            #Fill Results for ScenariosProbability
            if LevelList!=[]: 
                i=LevelList[-1]
                if i not in ScenariosAnalyzeNumbers.keys():
                    ScenariosAnalyzeNumbers[i]=[ScenarioNum]
                else:
                    ScenariosAnalyzeNumbers[i].append(ScenarioNum)  

        #Convert Results number to probability(value) (Scenario(key)) 
        ScenariosProbability={tag:val/TotalScenario for tag,val in Results.items()}

        #Scenarios(key) and its SubScenariosList(Value) Dictionary
        dmlvl=lambda scenario: [key for key,val in DamlvlScenDict.items() if scenario in val][0] #Find scenario damage level
        ScanariosSubScenario={Scenario:[] for Scenario in Results.keys()}
        for Scenario in ScanariosSubScenario.keys():
            ScanariosSubScenario[Scenario]=[SubScen for SubScen in Results.keys() if (dmlvl(SubScen)==dmlvl(Scenario)+1 and Scenario in SubScen)]



        Results=dict(DamagedLevelList=DamagedLevelList,
                                    FragilityTagList=FragilityTagList,
                                    LOCList=LOCList,
                                    NodesGroupDamageList=NodesGroupDamageList,
                                    NodesGroupTypeDict=NodesGroupTypeDict,
                                    NodesGroupDamageProbability=NodesGroupDamProb,
                                    TotalLOCList=ListOfLoc,
                                    LOC_bins_hist_probloc=[bins,hist,probloc],
                                    Damagelevel_eLOC=DmglvlLOC,
                                    Total_Number_Of_Scenarios=TotalScenario,
                                    UnitsZeroDamageProb=UnitsZeroDamageProb,
                                    ProbOfFragilities=ProbOfFragilities,
                                    ScenariosAnalyzeNumbers=ScenariosAnalyzeNumbers,
                                    ScenariosProbability=ScenariosProbability,
                                    ScanariosSubScenario=ScanariosSubScenario,
                                    Damagelevel_Scenario_Dict=DamlvlScenDict,
                                    HazardMagnitude=HazardMagnitude,
                                    ScenarioName_DamageLevel_Dict=ScenNameDamLvlDict,
                                    NodesGroupRadiationDict=NodesGroupRadiationAveDict,
                                    NodesGroupOverPressureDict=NodesGroupOverPressureAveDict,
                                    NodesGroup_OVP_Probit_Dict=NodesGroupOVPProbAveDict,
                                    NodesGroup_Rad_Probit_Dict=NodesGroupRadProbAveDict,)


        return Results
            
        
        
    def _LevelList(damagelistrow):
        #This function returns damage levels and corresponding tags
        #Format= (Damage Level):[tag of damaged units]

        #if no damage happened return []
        if 0 not in damagelistrow.values(): return []

        #Export data
        rslt={}
        for tag,dmlvl in damagelistrow.items():
            if dmlvl not in list(rslt.keys()) and dmlvl!=None:
                rslt[dmlvl]=str(tag)
            elif dmlvl!=None:
                rslt[dmlvl]=rslt[dmlvl]+','+str(tag)
        

        #Arrange data from 0 to ... 
        finalrslt=[]
        for dmlvl in range(max(rslt.keys())+1):
            text=f'({dmlvl}):[{rslt[dmlvl]}]'   #Convert to text format
            finalrslt.append(text)

        return finalrslt       
