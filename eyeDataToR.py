#### UMD Eye-tracking script
####Edited by: Shevaun Lewis, Ewan Dunbar & Sol Lago
#1. Added code for computing first pass-skips, 'fs' [01/11/13]
####Last updated: 04/01/14

#### Concatenates data from .DA1, Eyedoctor-processed files into a format suitable for R

#### Input (from command line, in same directory as input files):
#### python eyeDataToR.py
#### Directory should contain:
#### - REG file (regions for sentences--compatible with 2-line trials)
#### - Question key file
#### - Folder with DA1 files (first 3 chars of filenames must be subject #: '003-goose-s.DA1')
#### - Folder with question DA1 files (same naming convention: '003-goose-q.DA1')
####  (use organizeDA1-command.py to sort your DA1 files appropriately)

#### Output: a single, long-format text file that can be loaded into R

## import python libraries: os for managing files, readline for tab-completion
import os
import readline
#### Import required files; these should be in the same directory
import eyeMeasures
import readInput

###################################################################################
## this part is for using with the command line

#### Get info from user:
def ask_user_questions(questions):
    readline.set_completer()
    answers = {}
    q_template = 'Please enter the {} below:\n'
    for question in questions:
        answers[question] = raw_input(q_template.format(question))
    return answers


def main():
    # think about generalizing using experiment names?

    our_questions = {
    'REG filename' : 'gardenias.reg.txt',
    'Question key filename' : 'expquestions.txt',
    'Sentence data folder': 'Gardenias-s',
    'Question data folder': 'Gardenias-q',
    'Output filename': 'huzzah.txt',
    }
    if enable_user_input:
        answr = ask_user_questions(our_questions)
    else:
        answr = our_questions
    pass



##to override the above (comment this out if using the command line prompts)
##maindirectory = os.getcwd()
##REGFILENAME = "goose_regions4.reg.txt"
##QANSFILENAME = "goose_qAns.txt"
##dataDir = maindirectory+"/goose-sorted/goose-s"
##questionDir = maindirectory+"/goose-sorted/goose-q"
##outFileName = "goose.data5.txt"

##other optional parameters:
# Min and max fixation time to be counted
lowCutoff = 80                   #should be 40 ms
highCutoff = 1000
print("fixation time settings:")
print("low cutoff: 80ms")       #FIXME: this should print whatever the value of lowCutoff is
print("high cutoff: 1000ms")    #FIXME: this should print whatever the value of highCutoff is
# List of measures to be included in the output:
#'ff' = first fixation
#'fp' = first pass
#'fs' = first-pass skips
#'rp' = regression path
#'pr' = probability of regression
#'rb' = right-bounded
#'rr' = re-read time
#'tt' = total time
measures = ["ff","fp", "fs", "rp","pr","rb","rr","tt"]
print("computing all measures")
##########################################################################################################
#### Do not edit below here

#### Read in region key, create dictionary.
#### Key = unique cond/item tag; value = [cond, item, nregions, [[xStart, yStart],[xEnd, yEnd]], ...]

regionInfo = readInput.RegionTable(REGFILENAME,0,1)

#### Read in question answer key, create dictionar.
#### Key = item number; value = [correctButton, LorR]

qAns = readInput.dictTable(readInput.readTable(QANSFILENAME))

#### Get file lists (contents of the data and question directories)

DataFileList = os.listdir(dataDir)
QFileList = os.listdir(questionDir)

#### Create dictionary for question files:
#### Key = subject number; value = question file name
qsubj = {}
for Qfile in QFileList:
    qsubj[Qfile[0:3]] = Qfile

#############################################################
#### Main loop that processes each file in the data directory

dataOutput = []                                     ## initialize output table

for dataFile in DataFileList:
    if dataFile[len(dataFile)-3:].lower()!="da1":           ## Make sure it's a DA1 file
        print ("not a DA1 file: "+dataFile)
    else:
        subjOutput = []                                 ## initialize output table for subject
        subjNum = dataFile[0:3]                         ## Assume first three characters in filename is subject number
        print ("processing", dataFile)                    ## Print file name to provide feedback to user
        data = readInput.FixationTable(dataDir+"/"+dataFile, 1,2) ## Read in and code data file --> dictionary with cond/item key
        if subjNum in qsubj:                            ## if there is a question file for the subj,
            qdata = readInput.QuestionTable(questionDir+"/"+qsubj[subjNum], 1,2) ## lookup the file and make a dict with cond/item key
        else:
            qdata = {}
            print ("no question data for "+subjNum)

        for dRow in data:                               ## Loop over keys in the data dictionary
            if dRow in regionInfo:                      ## if regionInfo has a row with a matching cond/item key
                regions = regionInfo[dRow][3:]          ## 'regions' is a list of regions for that cond/item key
                # print regions
                fixdata = data[dRow]
                fixations = fixdata[8:]                 ## fixations is a list of the fixations--[X Y starttime endtime]
                cond = fixdata[1]
                item = fixdata[2]
                order = fixdata[0]
                if subjNum in qsubj and dRow in qdata:
                    questionRT = qdata[dRow][3]             ## get RT for question from qdata dictionary
                    if qdata[dRow][4]==qAns[item][0]:       ## if buttonpress matches answer in qAns, then accuracy = 1, else 0
                        questionAcc = '1'
                    else:
                        questionAcc = '0'
                else:
                    questionAcc = 'NA'
                    questionRT = 'NA'

            else:                                       ## if no matching region info, provide feedback
                print ("no region info: "+dRow)

            for reg in regions:                         ## loop over regions (nested lists of the form [[Xstart,Ystart],[Xend,Yend]])
                regnum = str(regions.index(reg)+1)      ## number regions starting at "1"
                regXstart = str(reg[0][0])              ## start and endpoints for region, so length, line change can be computed later
                regYstart = str(reg[0][1])
                regXend = str(reg[1][0])
                regYend = str(reg[1][1])
                for measure in measures:
                    if measure == 'ff': value = str(eyeMeasures.firstFix(reg,fixations,lowCutoff, highCutoff))
                    elif measure == 'fp': value = str(eyeMeasures.firstPass(reg,fixations,lowCutoff,highCutoff))
                    elif measure == 'fs': value = str(eyeMeasures.firstSkip(reg,fixations,lowCutoff, highCutoff))
                    elif measure == 'rp': value = str(eyeMeasures.regPath(reg,fixations,lowCutoff,highCutoff))
                    elif measure == 'pr': value = str(eyeMeasures.perReg(reg,fixations,lowCutoff,highCutoff))
                    elif measure == 'rb': value = str(eyeMeasures.rightBound(reg,fixations,lowCutoff,highCutoff))
                    elif measure == 'rr': value = str(eyeMeasures.rereadTime(reg,fixations,lowCutoff,highCutoff))
                    elif measure == 'tt': value = str(eyeMeasures.totalTime(reg,fixations,lowCutoff,highCutoff))
                    outLine = [subjNum, cond, item, value, regnum, regXstart, regXend, regYstart, regYend, measure, order, questionRT, questionAcc]
                    subjOutput.append(outLine)

        dataOutput.extend(subjOutput)                   ## Attach subjOutput to main dataOutput record of data

#### Create output
myOutFile = open(outFileName, "w")                      ## Open output file for editing
myOutFile.write('subj\tcond\titem\tvalue\tregion\tXstart\tXend\tYstart\tYend\tfixationtype\torder\tquestionRT\tquestionAcc\n')     ## add header
for row in dataOutput:                                  ## Loop through rows of data
    myOutFile.write('\t'.join(row)+'\n')                ## write row with tabs btw. fields and newline at the end
myOutFile.close()
