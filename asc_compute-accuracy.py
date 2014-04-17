'''
############################################################################
###            UMD Eyetracking Data Processing Stream (2013a)            ###
############################################################################

###              Version information                ###
#######################################################
### Last updated by Wing-Yee Chow on 2/26/2013

###           What is this script for?              ###
#######################################################
### This script uses .ASC files to compute individual subjects' accuracy 
### for all trials and creates an -acc.txt file for each subject.
### It also saves a summary of all subjects' average accuracya and
### flags subjects with <80% accuracy.

###                 Instructions                    ###
#######################################################
### 1) The file names must include subject id in digits.
### 2) The output filenames will contain the subject id and an '-acc.txt' suffix.
### 3) Average accuracy info is appended to the summary file
###    "Accuracy_log.txt" every time this script is run. 


#######################################################
'''
import re, sys, os

# IK: this section is where I create my commands

# IK: this sets data and output directories
dataDir = (os.getcwd()+'/ASC-lite/')
print ('Accuracy data extracted from .asc files in ' + dataDir)
outDir = (os.getcwd()+'/Accuracy/')
if not os.path.exists(outDir):
    os.makedirs(outDir)
print ('output files created in ' + outDir)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

log=[]

dataFileList = os.listdir(dataDir)
for dataFile in dataFileList:
    # IK: this is just a file checking function, same as the one for DA1 files
    if dataFile[-4:]=='.asc':
        print 'Loading '+dataFile + '...'
        dataOut = []
        d = open(dataDir+dataFile, "r")
        # IK: we'll need to come up with a general function for extracting subj #
        # IK: it needs to be flexible!
        subj = re.findall(r'\w(\d+\w+).asc',dataFile)      # to extract subj# from filename
        if len(subj)<>1:                            # in case there're other unrelated files in this directory
            # IK: ^^ shouldn't this be already covered by asc check?
            print 'Error: Subject information not found.'
        if len(subj)==1:
            subjID = subj[0]
            print 'Subject#' + subjID
            outFile = subjID+'-acc.txt'
            if os.path.exists(outDir+outFile):
                print('The accuracy data for '+outFile+' already exist.')
            else:
                out = open(outDir+outFile,"w")
                inTrial = 0
                linenum = 0
                numCorr = 0
                for line in d:
                    l = line.strip('\n')
                    curline = l.split()
                    if len(curline)==4:
                        if (curline[2]=='TRIALID') & (inTrial == 0):
                            curTrial = curline[3]
                            ## inTrial = 0 
                            # inTrial is set to 0 everytime it hits the beginning of a trial
                            if (curTrial[-1] == '1') & ((curTrial[0]=='E')|(curTrial[0]=='F')):  
                                # ^^ this looks at all non-practice items (both experimental and fillers are included)
                                inTrial = 1  # inTrial is set to 1 when it hits a question (E/F .... D1)
                                linenum +=1
                                curTarget = 'NA'
                                curButton = 'NA'
                                curAcc = 'NA'
                                if  curTrial[0]=='F':
                                    curCond = '99'  # all fillers now have condition #99
                                else:
                                    ## to extract the condition number for experimental items
                                    findCond = re.findall(r'\w(\d+)I',curTrial)
                                    if len(findCond)<>1:
                                        print 'Error: Condition information not found.'
                                    if len(findCond)==1:
                                        curCond = findCond[0]
                                ## to extract the item number for all trials (filler and experimental)
                                findItem = re.findall(r'I(\d+)D',curTrial)
                                if len(findItem)<>1:
                                    print 'Error: Condition information not found.'
                                if len(findItem)==1:
                                    curItem = findItem[0]
                        if inTrial == 1:  # look for target and repsonse when inside a trial of interests
                            if curline[2]=='QUESTION_ANSWER':
                                curTarget = curline[3]
                            if curline[2]=='TRIAL_RESULT':
                                curButton = curline[3]  
                                # this is the button press (or the lack thereof) that ends the trial
                                curAcc = '0'        
                                # accuracy is initialized as '0' unless the third condition is fulfilled
                                if curButton == curTarget:
                                    curAcc = '1'
                                    numCorr += 1 # add one to the number of correct trials
                                elif curButton == '0':
                                    curAcc = 'NA'
                                dataOut.extend(str(linenum)+'\t'+curCond+'\t'+curItem+'\t'+curTarget+'\t'+curButton+'\t'+curAcc+'\n')
                                inTrial = 0
                for row in dataOut:
                    out.write(str(row))
                out.close()
                AccRate = float(numCorr)/float(linenum)
                print('The accuracy for '+subjID+' is...'+str(AccRate))
                log.extend(subjID+'\t'+str(linenum)+'\t'+str(numCorr)+'\t'+str(AccRate))
                if AccRate < 0.8:
                    log.extend('\t*BELOW 80%')
                log.extend('\n')
        d.close()
    
logfile = open(outDir+"Accuracy_log.txt","a")
logfile.write('Subj\tnumTrial\tnumCorrect\tAccRate\tNote\n')
for row in log:
   logfile.write(row)
logfile.close()
