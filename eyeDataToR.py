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


def create_file_paths(directory):
    '''Given a folder name returns a dict of with subject numbers as keys and 
    file lists as values.
    '''
    numbers_and_paths = ((get_subj_num(f_name), os.path.join(directory, f_name))
                                        for f_name in os.listdir(directory))
    return dict(numbers_and_paths)


def files_to_tables(subj_paths):
    # this assumes there will at least be one file for the subject
    # is this a reasonable assumption to make?
    subj, fix_filename, q_filename = subj_paths
    fixation_table = FixationTable(fix_filename, 1, 2) if is_DA1_file(fix_filename) else None
    question_table = QuestionTable(q_filename, 1, 2) if is_DA1_file(q_filename) else None
    return (subj, fixation_table, question_table)


def create_subj_tables(sentence_dir, question_dir):
    '''Given folder names for sentences and questions returns .
    IK: talk about what happens if there are non-overlapping entries.
    '''
    sentence_paths = create_file_paths(sentence_dir)
    question_paths = create_file_paths(question_dir)
    all_paths = [(subj, path, question_paths[subj])
                    for subj, path in sentence_paths.items()
                    if subj in question_paths]
    all_paths += [(subj, path, '')
                    for subj, path in question_paths.items()
                    if subj not in question_paths]
    all_paths += [(subj, '', path)
                    for subj, path in question_paths.items()
                    if subj not in sentence_paths]
    # print(list(map(files_to_tables, all_paths)))
    return list(map(files_to_tables, all_paths))
    # all_fixations [(subj, FixationTable(sent_path), QuestionTable(q_path))]
    # subj_nums = (get_subj_num(f_name) for f_name in file_list)
    # question_tables = (QuestionTable(os.path.join(question_dir, f_name), 1, 2)
    #     for f_name in file_list)
    # return dict(zip(subj_nums, question_tables))


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


def trial_fields(trial):
    '''
    '''
    # new_row = reset_fields(row, ['order', 'cond', 'item'])
    # new_row.append(('order', trial[0]))
    # new_row.append(('cond', trial[1]))
    # new_row.append(('item', trial[2]))
    return tuple(trial[:3])
    # return (trial[0], trial[1], trial[2])


def unpack_region_data(region_index, region):
    '''.
    '''
    return (str(region_index + 1),  # region number
        str(region[0][0]),  # Xstart
        str(region[1][0]),  # Xend
        str(region[0][1]),  # Ystart
        str(region[1][1])   # Yend
        )


def q_RT_acc(cond_item, item, q_table, answer_key):
    '''
    '''
    # new_row = reset_fields(row, ['questionRT', 'questionAcc'])
    # try to look up/compute the values for the fields
    # cond_item, order, cond, item = trial
    try:
        RT = q_table[cond_item][3]
        # print(q_table[cond_item])
        # print(answer_key[item][0])
        accuracy = int(q_table[cond_item][4] == answer_key[item][0])
        return (RT, accuracy)
        # new_row.append(('questionRT', subj_qs[cond_item][3]))
        # new_row.append(('questionAcc', int(subj_qs[cond_item][4] == answer[0])))
    # if this fails, set all fields to NA
    except:
        return ('NA', 'NA')
        # new_row.append(('questionRT', 'NA'))
        # new_row.append(('questionAcc', 'NA'))
    # return new_row


def zero_to_NA(item, binomial_measures):
    """
    """
    measure, value = item
    if measure in binomial_measures and value == 0:
        return (measure, 'NA')
    return (measure, value)


def region_measures(region, fixations, cutoffs):
    '''.
    '''
    # list below should be modified as needed (consider passing an argument)
    # list below consists of "measure name": measure_function pairs
    # measure functions are normally imported from eyeMeasures
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
    # region_data = unpack_region_data(region_index, region)
    # calculations = [func
    # for measure_name, func in measures]
    # calculations = [func for m, func in measures]
    # print(calculations)
    measure_data = ((measure_name, calc(region, fixations, low_cutoff, high_cutoff))
                        for measure_name, calc in measures)
    # print(measure_data)
    measures_to_NAs = (zero_to_NA(item, binomial_measures) 
                        for item in measure_data)
    # print(measures_to_NAs)
    # return list(measures_to_NAs)
    return measures_to_NAs
    # consider turning this into an iterator
    # return [region_data + measure for measure in measures_to_NAs]

    # for measure in measures:
    #     new_row = reset_fields(row, ['fixationtype', 'value'])
    #     measure_calc = measures[measure]
    #     calculated = measure_calc(region, fixations, lowCutoff, highCutoff)
    #     new_row.append(('fixationtype', measure))
    #     if measure in binomial_measures:
    #         new_row.append(('value', calculated))
    #     else:
    #         new_row.append(('value', zero_to_NA(calculated)))
    #     row_list.append(dict(new_row))
    # return row_list


def process_regions(cond_item, fixations, table_of_regions, cutoffs):
    # print(cond_item)
    try:
        # IK: why do we need items 0-2 in that list anyway?
        regions = table_of_regions[cond_item][3:]
    except KeyError:
        print('Missing region information for this cond/item: ' + cond_item)
        raise

    region_data = (unpack_region_data(i, regions[i]) for i in range(len(regions)))
    # print(list(region_data))
    measures = (region_measures(region, fixations, cutoffs) for region in regions)
    # print(len(list(region_data)) == len(list(measures)))
    # print(list(measures))
    # test = (expand(r, m) for r, m in zip(region_data, measures))
    # print(list(test))
    # return chain((expand(r, m) for r, m in zip(region_data, measures)))
    return chain(*[expand(r, m) for r, m in zip(region_data, measures)])


def process_subj(subj_data, table_of_regions, answer_key, cutoffs):
    subj_number, f_table, q_table = subj_data
    # print([(key, value[:3]) for key, value in f_table.items()])
    print('Processing subject #' + subj_number)

    if f_table:
        print('Found fixation data for this subject, will compute measures.')
        region_data = (process_regions(f, f_table[f][8:], table_of_regions, cutoffs)
                                                            for f in f_table)
        # flat_regions = (chain(*reg_list) for reg_list in region_data)
        # flat_regions = chain(region_data)
        trials = [trial_fields(f_table[cond_item]) for cond_item in f_table]
        # print(list(trials))
        # print(f_table.keys())
    else:
        print('No fixation data found for this subject.')
        region_data, trials = [], []
    
    if q_table:
        print('Found question data for subject, will compute accuracy.')
        accuracies = (q_RT_acc(cond_item, trial[2], q_table, answer_key) 
                        for cond_item, trial in zip(f_table.keys(), trials))
        # accuracies = list(zip(f_table.keys(), trials))
        # print(accuracies)
    else:
        print('No question data found for this subject.')
        accuracies = []
    # this step can be skipped if we don't want question accuracies computed
    # print(list(trials))
    # print(list(accuracies))
    add_q_info = (trial + q_info for trial, q_info in zip(trials, accuracies))
    # print(len(list(add_q_info)) == len(list(trials)))
    # drop_labels = (trial[1:] for trial in add_q_info)
    item_rows = [expand(item, regions) 
                for item, regions in zip(add_q_info, region_data)]
    return expand((subj_number,), chain(*item_rows))
    # return expand((subj_number,), add_q_info)

    # item_data = (proc_item(item, table_of_regions))

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
    # print 'regions:'
    # print table_of_regions

    # Read in question answer key, create dictionary.
    # Key = item number; value = [correctButton, LorR]
    answer_key = dictTable(read_table(file_names['Question key filename']))

    # Get file lists (contents of the data and question directories)
    tables_by_subj = create_subj_tables(file_names['Sentence data folder'],
                                        file_names['Question data folder'])
    # print(len(list(tables_by_subj)))
    subj_rows = [process_subj(subj_data, table_of_regions,
        answer_key, cutoffs)
    for subj_data in tables_by_subj]
    # print(list(subj_rows))
    output = [create_row_dict(output_header, row) for row in chain(*subj_rows)]

    # for subj_num, data_file_path in sentences_by_subj.items():
    #     row = []
    #     row.append(('subj', subj_num))
    #     if is_DA1_file(data_file_path):

    #         print('Processing ', os.path.basename(data_file_path))
    #         fixation_table = FixationTable(data_file_path, 1, 2)
    #         subj_questions = lookup_question(subj_num, questions_by_subj)

    #         for cond_item in fixation_table:
    #             try:
    #                 # IK: why do we need items 0-2 in that list anyway?
    #                 regions = table_of_regions[cond_item][3:]
    #             except:
    #                 raise Exception('Missing region information for this cond/item: ' + cond_item)

    #             # this may need to be revised, IK
    #             row, item = unpack_trial_data(row, fixation_table[cond_item])
    #             row = set_question_RT_Acc(row,
    #                 cond_item, subj_questions, answer_key[item])
    #             # fixations is a list of the fixations--[X Y starttime endtime]
    #             fixations = fixation_table[cond_item][8:]
    #             reg = [region_measures(indx, regions[indx], fixations, cutoffs)
    #             for indx in range(len(regions))]
    #             # loop over regions (nested lists of the form
    #             # [[Xstart,Ystart],[Xend,Yend]])
    #             # for region in regions:
    #             #     row = unpack_region_data(row, region,
    #             #         regions.index(region))
    #             #     dataOutput += collect_measures(row, region,
    #             #         fixations, lowCutoff, highCutoff)
    #     else:
    #         print("This is not a DA1 file: {}\nSkipping...".format(data_file_path))

    write_to_csv(file_names['Output filename'],
        output, #IK: run "create dict rows" on this
        output_header,
        delimiter='\t')


if __name__ == '__main__':
    main(enable_user_input=False)
    # main()