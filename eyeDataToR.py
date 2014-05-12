# UMD Eye-tracking script

# CHANGELOG
# Edited by: Shevaun Lewis, Ewan Dunbar & Sol Lago
# 1. Added code for computing first pass-skips, 'fs' [01/11/13]
# Last updated: 04/01/14
# Major revisions by Ilia Kurenkov in 4/2014
# For a record of activity, see this url:
# https://github.com/UMDLinguistics/EyeTrackAnalysis.git

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

# Revised by Ilia
# This file is structured in the following way:
# First we import all the necessary python modules
# Then we define functions for printing messages to the user/getting information
# from them.
# Then we have one random function that finds questions based on subject number.
# Finally, we have a bunch of functions that are used to create the output rows
# From this it becomes apparent that if you want to understand what the program
# does overall, you are best served by looking at the very end of this file
# at the main() function. 
# That's where things come together.

# import python libraries: os for managing files
import os
# import readline and set tab-completion based on what OS we are in
import readline
# MACOS uses "libedit" for readline functionality and has a different command
# for enabling tab completion
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
# whereas Unix (and maybe Windows) have the same command
else:
    readline.parse_and_bind("tab: complete")
# import regular expressions
import re
# import csv writing functionality
from csv import DictWriter
# Import required files; these should be in the same directory
from eyeMeasures import *
from readInput import *


#######################################
## Interacting with the user

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
        answers[question] = input(q_template.format(question))
    return answers


CUTOFF_PROMPT = '''The current cutoff settings are as follows.
low: {0}
high: {1}
Would you like to change them?
N.B. Type "YES"  to change or anything else to proceed with current settings.\n'''


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
    decision = input(prompt.format(low_cutoff, high_cutoff))
    # define regular expression that checks for "yes" answers
    yes_rgx = re.compile('y(:?e[sa]|up)?', re.IGNORECASE)
    if bool(yes_rgx.match(decision)):
        # if user says something matching yes_rgx, ask them to input their own cutoffs
        user_cutoffs = ask_user_questions(['low cutoff', 'high cutoff'])
        # return their responses converted to integers
        return (int(user_cutoffs['low cutoff']), int(user_cutoffs['high cutoff']))
    # if user doesn't want to change stuff, return passed args unchanged
    return (low_cutoff, high_cutoff)


#######################################
## Dealing with files 

def write_to_csv(file_name, data, header, **kwargs):
    '''Writes data to file specified by filename.

    :type file_name: string
    :param file_name: name of the file to be created
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
    '''Given a filename returns the subject number.
    Currently uses convention that first 3 chars in filename are subj number.
    Can (and should) be changed in the future to something more robust.
    '''
    return filename[0:3]


def create_file_paths(directory):
    '''Given a folder name returns a list of (subject_number, file_path tuples).
    '''
    file_paths = (os.path.join(sentence_dir, f_name)
        for f_name in os.listdir(directory))
    subj_nums = (get_subj_num(f_name) for f_name in file_list)
    return dict(zip(subj_nums, file_paths))


def files_to_tables(subj, fix_filename, q_filename):
    # this assumes there will at least be one file for the subject
    # is this a reasonable assumption to make?
    fixation_table = FixationTable(fix_filename, 1, 0) if fix_filename else None
    question_table = QuestionTable(fix_filename, 1, 0) if fix_filename else None
    return (subj, fixation_table, question_table)


def create_subj_tables(sentence_dir, question_dir):
    '''Given folder names for sentences and questions returns .
    IK: talk about what happens if there are non-overlapping entries.
    '''
    sentence_paths = create_file_paths(sentence_dir)
    question_paths = create_file_paths(question_dir)
    all_paths = [(subj, path, question_paths[subj]) 
    for subj, path in sentence_paths.items() if subj in question_paths]
    all_paths += [(subj, path, '') 
    for subj, path in question_paths.items() if subj not in question_paths]
    all_paths += [(subj, '', path) 
    for subj, path in question_paths.items() if subj not in sentence_paths]
    return map(files_to_tables, all_paths)
    # all_fixations [(subj, FixationTable(sent_path), QuestionTable(q_path))]
    # subj_nums = (get_subj_num(f_name) for f_name in file_list)
    # question_tables = (QuestionTable(os.path.join(question_dir, f_name), 1, 2)
    #     for f_name in file_list)
    # return dict(zip(subj_nums, question_tables))


#######################################
## Misc (and Other)

def lookup_question(number, question_tables):
    '''Given a subject number and the table of qutestion files for subjects
    returns the table relevant for this subject number.
    If no such table is available, alerts the user and returns an empty dict.
    '''
    try:
        return question_tables[number]
    except:
        print("No question data for subject " + number)
        return {}


#######################################
## Functions for creting/updating what will be a row in the output file

def reset_fields(row, fields_to_reset):
    '''The way Python dictionaries are set up, if we use them directly, we will
    simply overwrite every row's entry with the data we collect from the next row.
    In order to avoid this, we instead accumulate lists of (key, value) tuples
    which can then be turned into dictionaries before we add them to our output
    file.
    This function takes a list Row consisting of (key, value) pairs and a list 
    of keys (or fields) to reset and returns the Row list without any pairs where
    the first member (the key) is present in the list of fields to reset.
    '''
    return [pair for pair in row if pair[0] not in fields_to_reset]


def unpack_trial_data(row, trial):
    '''Takes a row and a trial and sets the values for some of the fields in
    the row to stuff extracted from the trial list.
    '''
    new_row = reset_fields(row, ['order', 'cond', 'item'])
    new_row.append(('order', trial[0]))
    new_row.append(('cond', trial[1]))
    new_row.append(('item', trial[2]))
    return (new_row, trial[2])


def unpack_region_data(row, region, region_index):
    '''Takes a row and a region as arguments. Sets some of the row's fields
    to values gotten from the region.
    Returns the row.
    '''
    new_row = reset_fields(row, ['region', 'Xstart', 'Ystart', 'Xend', 'Yend'])
    new_row.append(('region', str(region_index + 1)))
    new_row.append(('Xstart', str(region[0][0])))
    new_row.append(('Ystart', str(region[0][1])))
    new_row.append(('Xend', str(region[1][0])))
    new_row.append(('Yend', str(region[1][1])))
    return new_row


def set_question_RT_Acc(row, cond_item, subj_qs, answer):
    '''Given a row, a condition/item tag, a list of subject responses to questions
    as well as the correct answer, sets the RT and accuracy fields in the row.
    Returns the row.
    '''
    new_row = reset_fields(row, ['questionRT', 'questionAcc'])
    # try to look up/compute the values for the fields
    try:
        new_row.append(('questionRT', subj_qs[cond_item][3]))
        new_row.append(('questionAcc', int(subj_qs[cond_item][4] == answer[0])))
    # if this fails, set all fields to NA
    except:
        new_row.append(('questionRT', 'NA'))
        new_row.append(('questionAcc', 'NA'))
    return new_row


def zero_to_NA(value):
    """Given any numeric value converts it to "NA" if it's zero. 
    Returns unchanged value otherwise.
    """
    if value == 0:
        return 'NA'
    return value


def collect_measures(row, region, fixations, lowCutoff, highCutoff):
    '''Given a row, a region and a list of fixations collects some eye-tracking
    measures.
    Uses the row fields to create output rows for every measure computed.
    Returns the resulting list of output rows.
    '''
    # list below should be modified as needed (consider passing an argument)
    # list below consists of "measure name": measure_function pairs
    # measure functions are normally imported from eyeMeasures
    measures = {
    'ff': first_fixation,
    'fp': first_pass,
    'fs': first_skip,
    'sf': single_fixation,
    'pr': prob_regression,
    'rp': regression_path,
    'rb': right_bound,
    'tt': total_time,
    'rr': rereading_time,
    'prr': prob_rereading,
    }
    binomial_measures = ['fs', 'pr', 'prr']
    row_list = []
    for measure in measures:
        new_row = reset_fields(row, ['fixationtype', 'value'])
        measure_calc = measures[measure]
        calculated = measure_calc(region, fixations, lowCutoff, highCutoff)
        new_row.append(('fixationtype', measure))
        if measure in binomial_measures:
            new_row.append(('value', calculated))
        else:
            new_row.append(('value', zero_to_NA(calculated)))
        row_list.append(dict(new_row))
    return row_list


#######################################
## This is the main function that actually puts all of the above together and 
## does stuff...

def main(enable_user_input=True):
    # IK: think about generalizing using experiment names?
    # IK: the default files dictionary is there mostly for development
    default_files = {
        'REG filename': 'output.reg.txt',
        'Question key filename': 'expquestions.txt',
        'Sentence data folder': 'Gardenias-s',
        'Question data folder': 'Gardenias-q',
        'Output filename': 'testing2.csv',
    }
    # define list of questions to be asked of user if defaults aren't used
    our_questions = [
        'REG filename',
        'Question key filename',
        'Sentence data folder',
        'Question data folder',
        'Output filename',
    ]

    # defining output header
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

    if enable_user_input:
        file_names = ask_user_questions(our_questions)
    else:
        file_names = default_files

    lowCutoff, highCutoff = verify_cutoff_values(40, 1000)

    # Read in region key, create dictionary.
    # Key = unique cond/item tag; value = [cond, item, nregions, [[xStart,
    # yStart],[xEnd, yEnd]], ...]
    table_of_regions = RegionTable(file_names['REG filename'], 0, 1)
    # print 'regions:'
    # print table_of_regions

    # Read in question answer key, create dictionary.
    # Key = item number; value = [correctButton, LorR]
    answer_key = dictTable(read_table(file_names['Question key filename']))

    # Get file lists (contents of the data and question directories)
    tables_by_subj = create_subj_tables(file_names['Sentence data folder'],
                                            file_names['Question data folder'])

    dataOutput = []

    for subj_num, data_file_path in sentences_by_subj.items():
        row = []
        row.append(('subj', subj_num))
        if is_DA1_file(data_file_path):

            print('Processing ', os.path.basename(data_file_path))
            fixation_table = FixationTable(data_file_path, 1, 2)
            subj_questions = lookup_question(subj_num, questions_by_subj)

            for cond_item in fixation_table:
                try:
                    # IK: why do we need items 0-2 in that list anyway?
                    regions = table_of_regions[cond_item][3:]
                except:
                    raise Exception('Missing region information for this cond/item: ' + cond_item)

                # this may need to be revised, IK
                row, item = unpack_trial_data(row, fixation_table[cond_item])
                row = set_question_RT_Acc(row,
                    cond_item, subj_questions, answer_key[item])
                # fixations is a list of the fixations--[X Y starttime endtime]
                fixations = fixation_table[cond_item][8:]
                # loop over regions (nested lists of the form
                # [[Xstart,Ystart],[Xend,Yend]])
                for region in regions:
                    row = unpack_region_data(row, region,
                        regions.index(region))
                    dataOutput += collect_measures(row, region,
                        fixations, lowCutoff, highCutoff)
        else:
            print("This is not a DA1 file: {}\nSkipping...".format(data_file_path))

    write_to_csv(file_names['Output filename'],
        dataOutput,
        output_header,
        delimiter='\t')


if __name__ == '__main__':
    main(enable_user_input=False)
    # main()