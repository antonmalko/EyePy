# UMD Eye-tracking script
# Edited by: Shevaun Lewis, Ewan Dunbar & Sol Lago
# 1. Added code for computing first pass-skips, 'fs' [01/11/13]
# Last updated: 04/01/14

# Concatenates data from .DA1, Eyedoctor-processed files into a format
# suitable for R

# Input (from command line, in same directory as input files):
# python eyeDataToR.py
# Directory should contain:
# - REG file (regions for sentences--compatible with 2-line trials)
# - Question key file
# - Folder with DA1 files (first 3 chars of filenames must be subject #: '003-goose-s.DA1')
# - Folder with question DA1 files (same naming convention: '003-goose-q.DA1')
# (use organizeDA1-command.py to sort your DA1 files appropriately)

# Output: a single, long-format text file that can be loaded into R

# import python libraries: os for managing files, readline for tab-completion
import os
import readline
# import regular expressions
import re
# import csv writing functionality
from csv import DictWriter
# Import required files; these should be in the same directory
import eyeMeasures
from readInput import *

#
# this part is for using with the command line

# Get info from user:


def ask_user_questions(question_sequence):
    '''Given a sequence of items (can be a list or a dictionary, anything
    that supports iteration), prints prompts for every item in the shell
    so that the user can input a value for every item.
    Returns a dictionary of (item_name : user_input) pairings.
    '''
    # set tab auto-completion, but only for current folder
    readline.parse_and_bind("tab: complete")
    # define question prompt template and return variable
    q_template = 'Please enter the {} below:\n'
    answers = {}

    for question in question_sequence:
        answers[question] = raw_input(q_template.format(question))
    return answers


CUTOFF_PROMPT = '''The current cutoff settings are as follows.
low: {0}
high: {1}
Would you like to change them?
(type any variation on "yes" to change or anything else to proceed with current settings)\n'''


# IK: think about maybe setting default values for cutoffs?
# IK: think about converting cutoffs to floats?
def verify_cutoff_values(low_cutoff, high_cutoff, prompt=CUTOFF_PROMPT):
    '''Routine for verifying cutoff values with the person running the program.
    Arguments:
    low_cutoff -> the value for the low cutoff
    high_cutoff -> the value for the high cutoff
    prompt -> how to prompt the user to change the values, has a default value,
    so it's optional

    This function first prints the cutoff values and asks the user if they want
    to change them. If their answer is yes, returns user-defined cutoffs, otherwise
    returns passed cutoffs unchanged.
    '''
    decision = raw_input(prompt.format(low_cutoff, high_cutoff))
    # define regular expression that checks for "yes" answers
    yes_rgx = re.compile('y(:?e[sa]|up)?', re.IGNORECASE)
    if bool(yes_rgx.match(decision)):
        # if user says something matching yes_rgx, ask them to input their own cutoffs
        user_cutoffs = ask_user_questions(['low cutoff', 'high cutoff'])
        # return their responses converted to integers
        return (int(user_cutoffs['low cutoff']), int(user_cutoffs['high cutoff']))
    # if user doesn't want to change stuff, return passed args unchanged
    return (low_cutoff, high_cutoff)


def write_to_csv(file_name, data, header, **kwargs):
    '''Writes data to file specified by filename.

    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of dictionaries each of which
    must not contain keys absent in the 'header' argument
    :type header: list
    :param header: list of columns to appear in the output
    :type **kwargs: dict
    :param **kwargs: parameters to be passed to DictWriter.
    For instance, restvals specifies what to set empty cells to by default or
    'dialect' loads a whole host of parameters associated with a certain csv
    dialect (eg. "excel").
    '''
    with open(file_name, 'w') as f:
        output = DictWriter(f, header, **kwargs)
        output.writeheader()
        output.writerows(data)


def is_DA1_file(filename):
    '''Checks if a file name has DA1 extension.
    Currently accepts both ".da1" and ".DA1" files.
    Retunrs a boolean (True or False).
    '''
    return filename.endswith('.da1') or filename.endswith('.DA1')


def get_subj_num(filename):
    return filename[0:3]


def read_question_tables(question_dir):
    file_list = os.listdir(question_dir)
    subj_nums = (get_subj_num(f_name) for f_name in file_list)
    question_tables = (QuestionTable(os.path.join(question_dir, f_name))
        for f_name in file_list)
    return dict(zip(subj_nums, question_tables))


def create_file_paths(sentence_dir):
    file_list = os.listdir(sentence_dir)
    subj_nums = (get_subj_num(f_name) for f_name in file_list)
    file_paths = (os.path.join(sentence_dir, f_name)
        for f_name in file_list)
    return dict(zip(subj_nums, file_paths))


def unpack_trial_data(row_dict, trial):
    row_dict['order'] = trial[0]
    row_dict['cond'] = trial[1]
    row_dict['item'] = fixdata[2]
    return row_dict


def unpack_region_data(row_dict, region):
    # number regions starting at "1"
    row_dict['region'] = str(regions.index(reg) + 1)
    # start and endpoints for region, so length, line change can be
    # computed later
    row_dict['regXstart'] = str(reg[0][0])
    row_dict['regYstart'] = str(reg[0][1])
    row_dict['regXend'] = str(reg[1][0])
    row_dict['regYend'] = str(reg[1][1])
    return row_dict


def set_question_RT_Acc(row_dict, cond_item, subj_qs, answer):
    try:
        row_dict['questionRT'] = subj_qs[cond_item][3]
        row_dict['questionAcc'] = int(subj_qs[cond_item][4] == answer[0])
    except:
        row_dict['questionRT'] = 'NA'
        row_dict['questionAcc'] = 'NA'
    return row_dict


def collect_measures(row_dict, region, fixations):
    measures = {
    'ff': firstFix,
    'fp': firstPass,
    'fs': firstSkip,
    'rp': regPath,
    'pr': perReg,
    'rb': rightBound,
    'tt': totalTime
    }
    row_list = []
    for measure in measures:
        measure_calc = measures[measure]
        # will need to think about cutoff values
        row_dict['value'] = measure_calc(region, fixations)
        row_list.append(row_dict)
    return row_list


def main(enable_user_input=True):
    # IK: think about generalizing using experiment names?

    default_files = {
        'REG filename': 'gardenias.reg.txt',
        'Question key filename': 'expquestions.txt',
        'Sentence data folder': 'Gardenias-s',
        'Question data folder': 'Gardenias-q',
        'Output filename': 'huzzah.txt',
    }
    our_questions = [
        'REG filename',
        'Question key filename',
        'Sentence data folder',
        'Question data folder',
        'Output filename',
    ]

    if enable_user_input:
        file_names = ask_user_questions(our_questions)
    else:
        file_names = default_files

    lowCutoff, highCutoff = verify_cutoff_values(80, 1000)

    # Read in region key, create dictionary.
    # Key = unique cond/item tag; value = [cond, item, nregions, [[xStart,
    # yStart],[xEnd, yEnd]], ...]
    table_of_regions = RegionTable(file_names['REG filename'], 0, 1)

    # Read in question answer key, create dictionar.
    # Key = item number; value = [correctButton, LorR]
    answer_key = dictTable(readTable(file_names['Question key filename']))

    # Get file lists (contents of the data and question directories)
    sentences_by_subj = create_file_paths(file_names['Sentence data folder'])
    # create dictionary of question responses by subject
    questions_by_subj = read_question_tables(file_names['Question data folder'])

    dataOutput = []

    for subj_num, data_file_path in sentences_by_subj.items():
        row_dict = {}
        row_dict['subj'] = subj_num
        if is_DA1_file(data_file_path):

            print 'Processing ', os.path.basename(data_file_path)
            fixation_table = FixationTable(data_file_path, 1, 2)
            subj_questions = lookup_question(subj_num, questions_by_subj)

            for cond_item in fixation_table:
                try:
                    regions = region_table[cond_item]
                except:
                    raise 'Missing region information for this cond/item: ' + cond_item

                # this may need to be revised, IK
                row_dict = unpack_trial_data(row_dict, fixation_table[cond_item])
                row_dict = set_question_RT_Acc(row_dict,
                    cond_item,
                    subj_questions,
                    answer_key[row_dict['item']])
                # fixations is a list of the fixations--[X Y starttime endtime]
                fixations = fixation_table[cond_item][8:]
                # loop over regions (nested lists of the form
                # [[Xstart,Ystart],[Xend,Yend]])
                for region in regions:
                    row_dict = unpack_region_data(row_dict, region)
                    dataOutput += collect_measures(row_dict, region, fixations)
        else:
            print("This is not a DA1 file: {}\nSkipping...".format(data_file_path))


    # Create output header
    output_header = [
    'subj',
    'cond',
    'item',
    'value',
    'region',
    'Xstart',
    'Xend',
    'Ystart',
    'Yend',
    'fixationtype',
    'order',
    'questionRT',
    'questionAcc'
    ]

    write_to_csv(file_names['Output filename'],
        dataOutput,
        output_header,
        delimiter='\t')


def lookup_question(number, question_tables):
    try:
        return question_tables[number]
    except:
        print("No question data for subject " + number)
        return {}


def process_file(subj_num, data_file_path, question_tables, region_table):
    pass



# #
# # Main loop that processes each file in the data directory

# dataOutput = []  # initialize output table

# for dataFile in DataFileList:
#     ## Make sure it's a DA1 file
#     if is_DA1_file(dataFile):
#         print ("This is not a DA1 file: {}\nSkipping...".format(dataFile))
#     else:
#         ## initialize output table for subject
#         subjOutput = []
#         ## Assume first three characters in filename is subject number
#         subjNum = dataFile[0:3]
#         ## Print file name to provide feedback to user
#         print ("processing", dataFile)
#         ## Read in and code data file --> dictionary with cond/item key
#         data = FixationTable(dataDir + "/" + dataFile, 1, 2)
#         ## if there is a question file for the subj,
#         if subjNum in qsubj:
#             ## lookup the file and make a dict with cond/item key
#             qdata = QuestionTable(questionDir + "/" + qsubj[subjNum], 1, 2)
#         else:
#             qdata = {}
#             print ("no question data for " + subjNum)

#         ## Loop over keys in the data dictionary
#         for dRow in data:
#             ## if regionInfo has a row with a matching cond/item key
#             if dRow in regionInfo:
#                 ## 'regions' is a list of regions for that cond/item key
#                 regions = regionInfo[dRow][3:]
#                 # print regions
#                 fixdata = data[dRow]
#                 fixations = fixdata[8:]
#                     # fixations is a list of the fixations--[X Y starttime
#                     # endtime]
#                 cond = fixdata[1]
#                 item = fixdata[2]
#                 order = fixdata[0]
#                 if subjNum in qsubj and dRow in qdata:
#                     ## get RT for question from qdata dictionary
#                     questionRT = qdata[dRow][3]
#                     # if buttonpress matches answer in qAns, then accuracy = 1,
#                     # else 0
#                     if qdata[dRow][4] == qAns[item][0]:
#                         questionAcc = '1'
#                     else:
#                         questionAcc = '0'
#                 else:
#                     questionAcc = 'NA'
#                     questionRT = 'NA'

#             ## if no matching region info, provide feedback
#             else:
#                 print ("no region info: " + dRow)

#             # loop over regions (nested lists of the form
#             # [[Xstart,Ystart],[Xend,Yend]])
#             for reg in regions:
#                 ## number regions starting at "1"
#                 regnum = str(regions.index(reg) + 1)
#                 # start and endpoints for region, so length, line change can be
#                 # computed later
#                 regXstart = str(reg[0][0])
#                 regYstart = str(reg[0][1])
#                 regXend = str(reg[1][0])
#                 regYend = str(reg[1][1])
#                 for measure in measures:
#                     outLine = [
#                         subjNum, cond, item, value, regnum, regXstart, regXend,
#                         regYstart, regYend, measure, order, questionRT, questionAcc]
#                     subjOutput.append(outLine)

#         ## Attach subjOutput to main dataOutput record of data
#         dataOutput.extend(subjOutput)
