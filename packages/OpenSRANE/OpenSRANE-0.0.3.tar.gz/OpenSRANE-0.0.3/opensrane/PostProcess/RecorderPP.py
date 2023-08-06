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

class RecorderPP():
    
    Results=None

    def Analyze(Recorer_FilenamesList=[],Number_Of_LOC_Histogram_Bins=100):

        #Define Variables
        DamagedLevelList=[]             #list of the plant units Damage level list, each value is a Dictionary of Damage level of the plant units for each scenario
        FragilityTagList=[]             #List of the plant units happend fragility tag Dictionaries, 
        LOCList=[]                      #List of the PlantUnits tag and max Loss of Containment value Dictionary
        NodesGroupDamageList=[]         #List of NodesGroup isDamaged list, each Dictionary is NodesGroupTag and corresponding Damagelist
        NodesGroupTypeDict={}           #Dictionray of each NodesGroup object that keys are tag of nodes group and values are the type of the nodes group
        NodesGroupDamProb={}            #Dictionray of each NodesGroup object that keys are tag of nodes group and values are the probability of their damage
        NodesGroupRadiationAveDict={}  #Dictionary of NodesGroup Radiation Data, and keys is Nodes Group tag and value is the list of Radiation values Average 
        NodesGroupOverPressureAveDict={}  #Dictionary of NodesGroup OverPressure Data, and keys is Nodes Group tag and value is the list of OverPressure values Average
        NodesGroupOVPProbAveDict={}     #Dictionary of NodesGroup OverPressure corresponding Probit Data, and keys is Nodes Group tag and value is the list of Probit(OverPressure) values Average 
        NodesGroupRadProbAveDict={}     #Dictionary of NodesGroup Radiation Probit Data, and keys is Nodes Group tag and value is the list of Probit(Radiation) values Average
        ListOfLoc=[]                    #List of total LOC in each scenario
        [bins,hist,probloc]=[[],[],[]]  #statistics parameters of LOC in scenarios (bins of LOC, histogram values, probability values)
        DmglvlLOC={}
        TotalScenario=None              #Total modeled scenario number
        UnitsZeroDamageProb={}          #Probability of each PlantUnit zero level damage
        ProbOfFragilities=[]            #Probablility of happening each fragility 
        HazardMagnitude=[]              #List of the hazard tags and magnitudes (tag as key and magnitude as value)
        ScenNameDamLvlDict={}            #Dictionary that its key is Scenario name and the value is its corresponding Damage level Dictionary


        files=_os.listdir()
        #Check files content one by one
        for file in Recorer_FilenamesList:
            
            #Check if file exist
            if file not in files:
                print(f'{file} not found and not loaded!')
                continue

            #Text to show the loading file started
            print('filename:',file,end=' ')
            
            with open(file, "r") as file:
                filedata = file.readlines()

            #File rows number -2 headers line is equal to the recorded scenarios number
            TotalScenario=int(filedata[0].split('-')[0][1:])
            

            #Read the type of recoder (Recorder field)
            RecordField=filedata[0].split('=')[1].split("'")[1]


            #Case Recorder is 'DamageLevel'-----------------------------------------------
            if RecordField=='DamageLevel':
                
                #Export PlantUnits objects tag
                Objstag=filedata[1].split('=')[1].split('[')[1].split(']')[0].split(',')
                Objstag=[int(i) for i in Objstag]


                # Export DamagedLevelList data
                for linedata in filedata[2:]:   #data[2:] beccause two first lines are headers
                    
                    DamagedLevelList.append({tag:(int(dmlvl) if dmlvl!='None' else None)  for tag,dmlvl in zip(Objstag,linedata.split())})
                    
                #------ Probability of Units Zero Level Damage
                UnitsZeroDamageProb={tag:0 for tag in Objstag}
                for DamLevelDict in DamagedLevelList:
                    for tag,DamLev in DamLevelDict.items() :
                        if DamLev==0: UnitsZeroDamageProb[tag]=UnitsZeroDamageProb[tag]+1

                #convert to probability
                UnitsZeroDamageProb={tag:DamLev/TotalScenario for tag,DamLev in UnitsZeroDamageProb.items()}

                #------ Probability of Damage levels and scenarios and subscenarios and Scenarios analyze number
                Results={} #Store scenario and number of happening (ScenariosProbability)
                ScenariosAnalyzeNumbers={} #Store scenario(key)  and number of alnazed scenarios list (Value)
                DamlvlScenDict={}   #Dictionary of damage level (key) and corresponding Scenarios set (Value)
                for ScenarioNum,damagelistrow in enumerate(DamagedLevelList):
                    LevelList=RecorderPP._LevelList(damagelistrow)
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

                #Create Damage Level and Corresponding Name Dictionary
                for dmlvl in DamagedLevelList:
                    ScenNameDamLvlDict["-".join(RecorderPP._LevelList(dmlvl))]=dmlvl


            #Case Recorder is 'FragilityTagList'-----------------------------------------------
            if RecordField=='FragilityTag':

                #Export PlantUnits objects tag
                Objstag=filedata[1].split('=')[1].split('[')[1].split(']')[0].split(',')
                Objstag=[int(i) for i in Objstag]

                # Export Fragility/Probit recorded data
                for linedata in filedata[2:]:    #data[2:] beccause two first lines are headers
                    
                    FragilityTagList.append({tag:(int(Fragtag) if Fragtag!='None' else None)  for tag,Fragtag in zip(Objstag,linedata.split())})

                
                #------ Probability of happening Fragilities and probits
                #find Fragilities tag (Fragtags)
                Fragtags=[]
                [Fragtags.extend([fragtag for fragtag in fragdict.values() if fragtag!=None]) for fragdict in FragilityTagList]
                Fragtags=list(set(Fragtags))

                ProbOfFragilities={tag:0 for tag in Fragtags}
                for FragDict in FragilityTagList:
                    for Fragtag in FragDict.values() :
                        if Fragtag!=None: ProbOfFragilities[Fragtag]=ProbOfFragilities[Fragtag]+1

                #convert to probability
                ProbOfFragilities={tag:Num/TotalScenario for tag,Num in ProbOfFragilities.items()}



            #Case Recorder is 'LOCList'-----------------------------------------------
            if RecordField=='LOC':

                #Export PlantUnits objects tag
                Objstag=filedata[1].split('=')[1].split('[')[1].split(']')[0].split(',')
                Objstag=[int(i) for i in Objstag]

                # Export LOC recorded data
                for linedata in filedata[2:]:    #data[2:] beccause two first lines are headers
                    
                    LOCList.append({tag:float(Loci) for tag,Loci in zip(Objstag,linedata.split())})


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


            #Case Recorder is 'NodesGroupIsDamaged'-----------------------------------------------
            if RecordField=='NodesGroupIsDamaged':

                #Export NodesGroup Tag and type
                NodesGroupTag=int(filedata[1].split()[3])
                NodesGroupType=filedata[1].split('=')[-1]

                #NodesGroupTypeDict
                NodesGroupTypeDict[NodesGroupTag]=NodesGroupType
                
                #Export Data
                for linedata in filedata[2:]:    #data[2:] beccause two first lines are headers
                    NodesGroupDamageList.append({NodesGroupTag:[int(isDam) for isDam in linedata.split()]})

                #----Probability of NodesGroup Damage
                NGtag=NodesGroupTag
                NodesGroupDamProb[NGtag]=[int(i) for i in filedata[2].split()]

                for linedata in filedata[3:]:
                    NodesGroupDamProb[NGtag]=[i+int(j) for i,j in zip(NodesGroupDamProb[NGtag],linedata.split())]

                #convert to expected Value
                NodesGroupDamProb[NGtag]=[i/TotalScenario for i in NodesGroupDamProb[NGtag]]



            #Case Recorder is 'HazardMag'-----------------------------------------------
            if RecordField=='HazardMag':
                
                #Export Hazard objects tag
                Objstag=filedata[1].split('=')[1].split('[')[1].split(']')[0].split(',')
                Objstag=[int(i) for i in Objstag]


                # Export Hazard data
                for linedata in filedata[2:]:   #data[2:] beccause two first lines are headers
                    
                    HazardMagnitude.append({tag:(float(mag) if dmlvl!='None' else None)  for tag,mag in zip(Objstag,linedata.split())})

            #Case Recorder is 'NodesRadiationOverPressure'-----------------------------------------------
            if RecordField=='NodesRadiationOverPressure':
                
                #import NodesGroup Tag and type
                NodesGroupTag=int(filedata[1].split()[5])
                NodesGroupType=filedata[1].split('=')[-1]

                #NodesGroupTypeDict
                NodesGroupTypeDict[NodesGroupTag]=NodesGroupType

                # import NodesRadiationOverPressure data
                for linedata in filedata[2:]:   #data[2:] beccause two first lines are headers

                    if NodesGroupTag not in NodesGroupRadiationAveDict.keys():
                        NodesGroupRadiationAveDict[NodesGroupTag]=[0 for i in [float(data.split(',')[0])  for data in linedata.split()]]
                        NodesGroupOverPressureAveDict[NodesGroupTag]=[0 for i in [float(data.split(',')[0])  for data in linedata.split()]]
                    
                    NodesGroupRadiationAveDict[NodesGroupTag]=[i+j for i,j in zip(NodesGroupRadiationAveDict[NodesGroupTag],[float(data.split(',')[0])  for data in linedata.split()])]
                    NodesGroupOverPressureAveDict[NodesGroupTag]=[i+j for i,j in zip(NodesGroupOverPressureAveDict[NodesGroupTag],[float(data.split(',')[1])  for data in linedata.split()])]

                #Convert to average
                NodesGroupRadiationAveDict[NodesGroupTag]=[i/TotalScenario for i in NodesGroupRadiationAveDict[NodesGroupTag]]
                NodesGroupOverPressureAveDict[NodesGroupTag]=[i/TotalScenario for i in NodesGroupOverPressureAveDict[NodesGroupTag]]
                

            #Case Recorder is 'NodesRadiationProbit'-----------------------------------------------
            if RecordField=='NodesRadiationProbit':
                
                #import NodesGroup Tag and type
                NodesGroupTag=int(filedata[1].split()[3])
                NodesGroupType=filedata[1].split('=')[-1]

                #NodesGroupTypeDict
                NodesGroupTypeDict[NodesGroupTag]=NodesGroupType


                # import NodesRadiationProbit data
                for linedata in filedata[2:]:   #data[2:] beccause two first lines are headers

                    if NodesGroupTag not in NodesGroupRadProbAveDict.keys():
                        NodesGroupRadProbAveDict[NodesGroupTag]=[0 for i in [float(data)  for data in linedata.split()]]

                    NodesGroupRadProbAveDict[NodesGroupTag]=[i+j for i,j in zip(NodesGroupRadProbAveDict[NodesGroupTag],[float(data)  for data in linedata.split()])]

                #Convert to average
                NodesGroupRadProbAveDict[NodesGroupTag]=[i/TotalScenario for i in NodesGroupRadProbAveDict[NodesGroupTag]]


            #Case Recorder is 'NodesOverPressureProbit'-----------------------------------------------
            if RecordField=='NodesOverPressureProbit':
                
                #import NodesGroup Tag and type
                NodesGroupTag=int(filedata[1].split()[3])
                NodesGroupType=filedata[1].split('=')[-1]

                #NodesGroupTypeDict
                NodesGroupTypeDict[NodesGroupTag]=NodesGroupType


                # import NodesOverPressureProbit data
                for linedata in filedata[2:]:   #data[2:] beccause two first lines are headers

                    if NodesGroupTag not in NodesGroupOVPProbAveDict.keys():
                        NodesGroupOVPProbAveDict[NodesGroupTag]=[0 for i in [float(data)  for data in linedata.split()]]

                    NodesGroupOVPProbAveDict[NodesGroupTag]=[i+j for i,j in zip(NodesGroupOVPProbAveDict[NodesGroupTag],[float(data)  for data in linedata.split()])]

                #Convert to average
                NodesGroupOVPProbAveDict[NodesGroupTag]=[i/TotalScenario for i in NodesGroupOVPProbAveDict[NodesGroupTag]]


            #Text to show the loading file ended
            print('loaded.',end=' ')
        


        RecorderPP.Results=dict(DamagedLevelList=DamagedLevelList,
                                UnitsZeroDamageProb=UnitsZeroDamageProb,
                                Total_Number_Of_Scenarios=TotalScenario,
                                FragilityTagList=FragilityTagList,
                                ProbOfFragilities=ProbOfFragilities,
                                LOCList=LOCList,
                                Damagelevel_eLOC=DmglvlLOC,
                                TotalLOCList=ListOfLoc,
                                LOC_bins_hist_probloc=[bins,hist,probloc],
                                NodesGroupDamageList=NodesGroupDamageList,
                                NodesGroupTypeDict=NodesGroupTypeDict,
                                NodesGroupDamageProbability=NodesGroupDamProb,
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

        
        return RecorderPP.Results
    


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