# UMD Eye-tracking script

# CHANGELOG
# Edited by: Shevaun Lewis, Ewan Dunbar & Sol Lago
# 1. Added code for computing first pass-skips, 'fs' [01/11/13]
# Last updated: 04/01/14
# Major revisions by Ilia Kurenkov in 4/2014
# For a record of activity, see this link:
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
from itertools import chain
# Import required files; these should be in the same directory
from eyeMeasures import *
from readInput import *


###########################################################
## Interacting with the user
###########################################################

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


###########################################################
## Dealing with files (fxns for separate lib)
###########################################################

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


def create_row_dict(fields, item):
    # IK: this should go into a separate file, I think
    length_difference = len(fields) - len(item)
    error_message = 'There are more items than labels for them: {0}'
    if length_difference < 0:
        print('Here are the column labels', fields)
        print('Here are the items', item)
        raise Exception(error_message.format(length_difference))
    elif length_difference > 0:
        item = item + ('NA',) * length_difference
    return dict(zip(fields, item))


def is_DA1_file(filename):
    '''Checks if a file name has DA1 extension.
    Currently accepts both ".da1" and ".DA1" files.
    Retunrs a boolean (True or False).
    '''
    return filename.endswith('.da1') or filename.endswith('.DA1')


def get_subj_num(file_name):
    '''Given a filename string returns any substring that consists of digits.
    If multiple such substrings are found, returns the first one.
    If no such substrings are found, returns empty string.
    '''
    subj_n_rgx = re.compile('\d+')
    # we don't want to risk finding digits from file extensions
    extensionless = file_name.split('.')[0]
    matches = subj_n_rgx.findall(extensionless)

    if not matches:
        warning = "Unable to find subject number in this file name: \n{0}"
        print(warning.format(file_name))
        return ''

    elif len(matches) > 1:
        warning = "Found several numbers in '{0}', using the first one out of: \n{1}"
        print(warning.format(file_name, matches))

    return matches[0]


def subjects_filepaths(directory):
    '''Given a folder name returns a dict of with subject numbers as keys and 
    file lists as values.
    '''
    numbers_and_paths = ((get_subj_num(f_name), os.path.join(directory, f_name))
                                        for f_name in os.listdir(directory))
    return dict(numbers_and_paths)


def files_to_tables(subj_paths):
    '''Given 3-member tuple of the form:
    (subj_n, fixation_file_path, question_file_path)
    turns the file paths into tables.
    If a file path is an empty string, it is converted to None.
    This returns a 3-tuple of the form:
    (subj_n, fixation_table, question_table)
    '''
    # this assumes there will at least be one file for the subject
    # is this a reasonable assumption to make?
    subj, fix_filename, q_filename = subj_paths
    fixation_table = FixationTable(fix_filename, 1, 2) if is_DA1_file(fix_filename) else None
    question_table = QuestionTable(q_filename, 1, 2) if is_DA1_file(q_filename) else None
    return (subj, fixation_table, question_table)


def create_subj_tables(sentence_dir, question_dir):
    '''Given folder names for sentences and questions returns a list of
    (subject_number, fixation_table, question_table) tuples.
    This is achieved by first creating two dictionaries, one for fixation files
    and one for question files. Both are indexed by subject numbers.
    The entries from these dictionaries are then combined into tuples
    that contain the subject number and a string for both the corresponding
    fixation and question file.
    If it so happens that a subject is missing one of the files, an empty string
    is entered in place of the file name inside the tuple.
    Finally, the filenames in the tuples are turned into tables.
    '''
    # dictionaries of subj_n:file_path pairings
    fixation_paths = subjects_filepaths(sentence_dir)
    question_paths = subjects_filepaths(question_dir)
    # start out by listing all the subjects present in both dictionaries
    all_paths = [(subj, path, question_paths[subj])
                    for subj, path in fixation_paths.items()
                    if subj in question_paths]
    # add to these subjects who only have fixation files for them
    all_paths += [(subj, path, '')
                    for subj, path in fixation_paths.items()
                    if subj not in question_paths]
    # add also subjects who only have question files associated with them
    all_paths += [(subj, '', path)
                    for subj, path in question_paths.items()
                    if subj not in fixation_paths]
    return list(map(files_to_tables, all_paths))


def expand(field1, more_fields, debug=False):
    if debug:
        print('field1 ' + str(field1))
        print(list(more_fields))
    try:
        return [field1 + field for field in more_fields]        
    except Exception as e:
        print('field1 ' + str(field1))
        # print(list(more_fields))
        raise e


def trial_info(trial):
    '''This function is really just a "fancy" wrapper for a very simple 
    subsetting operation. We take the first 3 members of the trial list.
    '''
    return tuple(trial[:3])


def q_RT_acc(cond_item, item, q_table, answer_key):
    '''Arguments: cond/item code, item number, question table, answer key.
    This function attempts to look up the answer provided by the subject for 
    the given cond/item code. The answer's RT is recorded as well as an integer
    [1 or 0] value for whether it matched the correct answer for that item, which
    is looked up in the answer_key dictionary.
    '''
    # IK: This is kind of redundant, should be revised at some point
    try:
        RT = q_table[cond_item][3]
        accuracy = int(q_table[cond_item][4] == answer_key[item][0])
        return (RT, accuracy)
    # if this fails, set both fields to NA
    except:
        return ('NA', 'NA')


def zero_to_NA(fixation_measure, binomial_measures):
    """Given a fixation measure as a tuple consisting of
    (name_of_measure, calculated_value) and a list of binomial measures,
    sets the value to "NA" if the measure in question is binomial AND the raw
    value is equal to zero. Otherwise returns the value unchanged.
    """
    measure_name, value = fixation_measure
    if measure_name in binomial_measures and value == 0:
        return (measure_name, 'NA')
    return (measure_name, value)


def region_measures(region, fixations, cutoffs):
    '''Given a region, a list of fixations, and cutoff values
    returns a list of (measure name, measure value) tuples for all the measures
    currently computed at UMD.
    Please note that all continuous measures that equal zero are set to "NA" for
    ease of later processing with R.
    '''
    # list below consists of "measure name": measure_function pairs
    # measure functions are imported from eyeMeasures
    measures = [
    ('ff', first_fixation),
    ('fp', first_pass),
    ('fs', first_skip),
    ('sf', single_fixation),
    ('pr', prob_regression),
    ('rp', regression_path),
    ('rb', right_bound),
    ('tt', total_time),
    ('rr', rereading_time),
    ('prr', prob_rereading),
    ]
    binomial_measures = ['fs', 'pr', 'prr']
    low_cutoff, high_cutoff = cutoffs
    measure_data = ((measure_name, calc(region, fixations, low_cutoff, high_cutoff))
                        for measure_name, calc in measures)
    measures_to_NAs = (zero_to_NA(item, binomial_measures) 
                        for item in measure_data)
    return measures_to_NAs


def region_info(region_index, region):
    '''Given a region and its index in the region list, returns the region number
    (simply its index + 1) in a tuple with its X and Y coordinates.
    '''
    # IK: Consider getting rid of the "str" to improve readability
    return (str(region_index + 1),  # region number
        str(region[0][0]),  # Xstart
        str(region[1][0]),  # Xend
        str(region[0][1]),  # Ystart
        str(region[1][1])   # Yend
        )


def process_regions(cond_item, fixations, table_of_regions, cutoffs):
    '''Given a cond/item code, a list of fixations, a table of regions, and
    cutoff values returns a list of tuples containing information about each
    region and eye-tracking measures in it for the relevant item.
    '''
    try:
        # IK: why do we need items 0-2 in that list anyway?
        regions = table_of_regions[cond_item][3:]
    except KeyError:
        print('Missing region information for this cond/item: ' + cond_item)
        raise
    # if we were able to retrieve regions for cond/item, we create a sequence of
    # tuples containing info for each region
    region_fields = (region_info(i, regions[i]) for i in range(len(regions)))
    # we then create a sequence of lists containing measure labels and values
    measures = (region_measures(region, fixations, cutoffs) for region in regions)
    # finally, we combine the two sequences
    region_rows = [expand(r, m_list) for r, m_list in zip(region_fields, measures)]
    # we return a "flattened" version of this list so as to combine it with
    # item information
    return chain(*region_rows)


def process_subj(subj_info, table_of_regions, answer_key, cutoffs):
    '''This function takes a subject number with corresponding fixation and 
    question table and constructs a list of tuples to be transformed into
    rows of the output file.
    '''
    subj_number, f_table, q_table = subj_info
    print('Processing subject #' + subj_number)

    if f_table:
        print('Found fixation data for this subject, will compute measures.')
        region_data = (process_regions(f, f_table[f][8:], table_of_regions, cutoffs)
                                                            for f in f_table)
        trials = [trial_info(f_table[cond_item]) for cond_item in f_table]
    else:
        print('No fixation data found for this subject.')
        region_data, trials = [], []
    
    if q_table:
        print('Found question data for subject, will compute accuracy.')
        q_infos = (q_RT_acc(cond_item, trial[2], q_table, answer_key) 
                        for cond_item, trial in zip(f_table.keys(), trials))
    else:
        print('No question data found for this subject.')
        q_infos = []
    add_q_info = (trial + q_info for trial, q_info in zip(trials, q_infos))
    item_rows = [expand(item, regions) 
                for item, regions in zip(add_q_info, region_data)]
    return expand((subj_number,), chain(*item_rows))


###########################################################
## This is the main function that actually puts all of the above together and 
## does stuff...
###########################################################

def main(enable_user_input=True):
    # IK: think about generalizing using experiment names?
    # IK: the default files dictionary is there mostly for development
    default_files = {
        'REG filename': 'output.reg.txt',
        'Question key filename': 'expquestions.txt',
        'Sentence data folder': 'Gardenias-s',
        'Question data folder': 'Gardenias-q',
        'Output filename': 'testing-loopless.csv',
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
        'order',
        'cond',
        'item',
        'questionRT',
        'questionAcc',
        'region',
        'Xstart',
        'Xend',
        'Ystart',
        'Yend',
        'fixationtype',
        'value',
    ]

    if enable_user_input:
        file_names = ask_user_questions(our_questions)
    else:
        file_names = default_files

    cutoffs = verify_cutoff_values(40, 1000)

    # Read in region key, create dictionary.
    # Key = unique cond/item tag; value = [cond, item, nregions, [[xStart,
    # yStart],[xEnd, yEnd]], ...]
    table_of_regions = RegionTable(file_names['REG filename'], 0, 1)
    # Read in question answer key, create dictionary.
    # Key = item number; value = [correctButton, LorR]
    answer_key = dictTable(read_table(file_names['Question key filename']))
    # Generate table files for all subjects
    tables_by_subj = create_subj_tables(file_names['Sentence data folder'],
                                        file_names['Question data folder'])
    # process all the subject data
    subj_rows = (process_subj(subj_data, table_of_regions, answer_key, cutoffs)
                                        for subj_data in tables_by_subj)
    # make data compatible with csv.DictWriter.writerows()
    output = (create_row_dict(output_header, row) 
                for row in chain(*list(subj_rows)))

    write_to_csv(file_names['Output filename'],
        output,
        output_header,
        delimiter='\t')


if __name__ == '__main__':
    main(enable_user_input=False)
    # main()