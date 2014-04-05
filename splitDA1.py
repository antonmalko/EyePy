##by: Shevaun Lewis
##date updated: 11/16/10

##This script contains functions for separating DA1 files into separate sentence and question files.

import os                 

############################################################## no touchy
## DA1splitType takes a DA1 file and returns a list with three embedded lists: sentences, questions,
## and "rejected" (trials with "-1" for the button response, or abnormally long durations)
def DA1splitType(dataFile):
    data = open(dataFile,"r")
    questions = []
    sentences = []
    rejected = []

    for line in data:
       if line != "":
           g = line.split(" ")
           if int(g[4])==2:
               sentences.extend(str(line)) 
           elif int(g[4])==6 or int(g[4])==7:
               questions.extend(str(line))
           else:
               rejected.extend(str(line))
    data.close()
    return [sentences, questions, rejected]

def DA1splitTypeFile(dataFolder, dataFilename, outFolderS, outFolderQ, outFolderR):
    subjnum = dataFilename[0:3]
    studyname = dataFilename.split(".")[0].split("-")[1]
    lists = DA1splitType(dataFolder+"/"+dataFilename)
    s = lists[0]
    q = lists[1]
    r = lists[2]

    if s != []:
        outnameS = outFolderS+"/"+subjnum+"-"+studyname+"-s.da1"
        outS = open(outnameS,"w")
        for row in s:
            outS.write(str(row))
        outS.close()

    if q != []:
        outnameQ = outFolderQ+"/"+subjnum+"-"+studyname+"-q.da1"
        outQ = open(outnameQ,"w")
        for row in q:
            outQ.write(str(row))
        outQ.close()

    if r != []:
        outnameR = outFolderR+"/"+subjnum+"-"+studyname+"-reject.da1"
        outR = open(outnameR,"w")
        for row in r:
            outR.write(str(row))
        outR.close()

## DA1splitTypeFolder takes two paths: one for the input folder and one for the output folder. It creates
## 3 folders within outFolder, one each for sentence trials, question trials, and rejected trials, and
## fills them with split DA1 files for each subject. 
def DA1splitTypeFolder(dataFolder, studyname):
    myFileList = os.listdir(dataFolder)
    outFolder = dataFolder+"/"+studyname+"-sorted"
    os.mkdir(outFolder)
    outFolderS = outFolder+"/"+studyname+"-s"
    os.mkdir(outFolderS)
    outFolderQ = outFolder+"/"+studyname+"-q"
    os.mkdir(outFolderQ)
    outFolderR = outFolder+"/"+studyname+"-reject"
    os.mkdir(outFolderR)
    
    for dataFile in myFileList:
        if dataFile[len(dataFile)-4:].lower()==".da1":
            DA1splitTypeFile(dataFolder, dataFile, outFolderS, outFolderQ, outFolderR)

    return [outFolderS, outFolderQ, outFolderR]

## DA1getExp takes a path for a data file, the number of the first condition for an experiment, and the
## number of conditions in the experiment. It returns a list of the lines in the data file that include
## trials from the desired experiment.
def DA1getExp(dataFile, expFirstCond, numConds):
    expData = []
    expCondRange = range(expFirstCond,expFirstCond+numConds)

    data = open(dataFile, "r")
    for line in data:
        if line != "":
            g = line.split(" ")
            if int(g[1]) in expCondRange:
                expData.extend(str(line))

    return expData

 
def DA1splitExpFolder(dataFolder, outFolder, expFirstCond, numConds, expname):
    myFileList = os.listdir(dataFolder)

    for dataFile in myFileList:
        trials = DA1getExp(dataFolder+"/"+dataFile, expFirstCond, numConds)
        if trials != []:
            subjnum = dataFile[0:4]
            if len(dataFile.split("-"))>2:
                end = "-"+dataFile.split("-")[2]
            else:
                end = ".da1"
            outname = outFolder+"/"+subjnum+expname+end
            outFile = open(outname, "w")
            for row in trials:
                outFile.write(str(row))
            outFile.close()
        else:
            print ("no data for "+expname+" in "+dataFile)
    
    
