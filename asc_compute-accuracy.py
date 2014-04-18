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
# to-do:
# docstrings
# get_subj_n exceptions or prints
# testing


#################################################
## Parsing ASC files
#################################################

def sanity_check(item_list):
    """Checks for emtpy items in a list using python's all() function, which 
    returns True only if all elements of a list/tuple are non-empty or not False.
    """
    return all((all(item) for item in item_list))


ParsingException = Exception('''There were problems searching for entries.
Please check your ASC file for corrupt entries''')


def parse_asc_file(f_name):
    # IK: will need to explain these regexes
    trial_filter = 'TRIALID ([EF]\d+)I(\d+)D1\s.*' 
    target_key = 'QUESTION_ANSWER (\d+)\s.*'
    response_key = 'TRIAL_RESULT (\d+)\s'
    # IK: think about var names here a bit
    collect = trial_filter + target_key + response_key
    # relevant_entry = 'TRIALID [EF]\w+1\s.*?QUESTION_ANSWER (\d+)\s.*?TRIAL_RESULT (\d+)\s'
    rgx = re.compile(collect, re.DOTALL)
    with open(f_name) as asc_file:
        asc_file_string = asc_file.read()
        extracted = rgx.findall(asc_file_string)
        if sanity_check(extracted):
            return extracted
        else:
            raise ParsingException


#################################################
## Writing subject per-item data to files
#################################################

def not_filler(item_row):
    """Checks whether the first element of an item contains 'F', for 'filler'.
    """
    return not item_row[0].startswith('F')


def reformat_condition(item):
    condition = item[0]
    if condition.startswith('F'):
        return ('99',) + item[1:]
    else:
        return (condition[1:],) + item[1:]


def prep_for_writing(subj_n, item_list):
    no_fillers = filter(not_filler, per_item_correct)
    clean_conditions = (reformat_condition(item) for item in item_list)
    include_subjects = [(subj_n,) + item for item in clean_conditions]
    return include_subjects


#################################################
## Processing each subject
#################################################

def filter_by_condition(cond_list, item_list):
    return [item for item in item_list if item[0] in cond_list]


def correctness(item):
    return item + (int(target_key == response_key),)


def subj_accuracy_stats(subj_number, item_list):
    n_correct = sum(item['is correct'] for item in item_list)
    n_total =  len(item_list)
    accuracy = float(row['N correct']) / row['N total']
    notes = '*Below 80%' if row['accuracy'] < 0.8 else ''
    # IK: this function should return accuracy, #correct, total#, maybe more?
    return (subj_number, n_correct, n_total, accuracy, notes)


def create_row_dicts(fields_list, items_list):
    # IK: this should go into a separate file, I think
    return [dict(zip(fields, item)) for item in items_list]


def empty_subj_row(subj_number):
    # fields = ['subject', 'N correct', 'N total', 'accuracy', 'notes/flag']
    values = [subj_number] + ['NA'] * (len(fields) - 1)
    return dict(zip(fields, values))


def process_subj(subj_n_file_path, out_dir, conditions):
    subject_fields = [
    'subject',
    'condition',
    'item',
    'target key',
    'response key'
    'correct'
    ]
    subj_number, f_path = subj_n_file_path
    subj_output_name = os.path.join(out_dir, subj_number) + '.csv'
    try:
        parsed_asc = parse_asc_file(f_path)
        # this is where one can insert filtering by condition list, smthng like:
        if conditions:
            parsed_asc = filter_by_condition(conditions, parsed_asc)
        per_item_correct = [correctness(item) for item in parsed_asc]
        formatted = prep_for_writing(subj_number, per_item_correct)
        write_to_csv(subj_output_name,
            create_row_dicts(subject_fields, formatted),
            subject_fields)
        return subj_accuracy_stats(subj_number, per_item_correct)
    except ParsingException as e:
        print('Error parsing file: ', f_path)
        print(e)
        return empty_subj_row(subj_number)

#################################################
## User Input, Files and Directories
#################################################

def get_subj_num(file_name):
    subj_n_rgx = re.compile('\d+')
    matches = subj_n_rgx.findall(file_name)
    if not matches:
        # IK: revise this line
        print "Unable to find subject number, please check this file name: " + file_name
    elif len(matches) > 1:
        # IK: maybe print the list of matches?
        print "Can't seem to decide which to choose" + file_name
    return matches[0]
    

def path_and_number(folder_name, file_name):
    file_path = os.path.join(folder_name, file_name)
    subj_number = get_subj_num(file_name)
    return (subj_number, file_path)


def parse_and_analyze(asc_dir, out_dir, conditions):
    # IK: rename ^^ this
    # IK: define list of fields or get it from user
    asc_file_list = (f_name in os.listdir(asc_dir) if f_name.endswith('.asc'))
    subj_list = (path_and_number(asc_dir, f_name) for f_name in asc_file_list)
    accuracy_data = [process_subj(f_name, out_dir, conditions)
                                    for f_name in asc_file_list]
    # IK: write this data to a file

def ask_for_conditions():
    #ask the user
    cond_string = input('Please enter the conditions you are interested in, separated by spaces.')
    cond_list = cond_string.strip().split()
    if len(cond_list) == 0:
        print("Unable to detect any conditions, will look at all trials.")
    return cond_list


def main():
    # IK: maybe ask user for directory input?
    ASC = ''
    OUTPUT = ''
    relevant_conditions = ask_for_conditions()
    # IK: definitely ask user for list of conditions
    parse_and_analyze(ASC, OUTPUT, relevant_conditions)


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
