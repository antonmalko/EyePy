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

# import csv writing functionality
from csv import DictWriter

# IK: this section is where I create my commands
# to-do:
# docstrings
# get_subj_n exceptions or prints
# testing

# procedure
# we parse an ASC file
# we exclude the conditions not for this experiment
# we compute correctness for all relevant items
# we create a by-item file for the subject
# compute stats for subject, return those


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
    trial_filter = 'TRIALID ([EF]\d+)I(\d+)D1\s.*?' 
    target_key = 'QUESTION_ANSWER (\d+)\s.*?'
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
## Writing ouput to file (better in a separate file)
#################################################

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
    # print('the item', item)
    # print('the fields', fields)
    length_difference = len(fields) - len(item)
    # print(length_difference)
    if length_difference < 0:
        raise Exception('There are more items than labels for them: ' + str(length_difference))
    elif length_difference > 0:
        item = item + ('NA',) * length_difference
    return dict(zip(fields, item))


#################################################
## Writing subject per-item data to files
#################################################


def not_filler(item):
    """Checks whether the first element of an item contains 'F', for 'filler'.
    """
    return not item[0].startswith('F')


def reformat_condition(item):
    '''Given an item tuple, changes the condition string by setting it to
    "99" if the condition is a filler (condition string starts with F) OR
    by dropping the first character of the condition.
    '''
    condition = item[0]
    # print('reformatting',item)
    if condition.startswith('F'):
        return ('99',) + item[1:]
    else:
        return (condition[1:],) + item[1:]


def generate_item_table(subj_n, subj_output_name, item_list):
    subject_fields = [
    'subject',
    'condition',
    'item',
    'target key',
    'response key',
    'correct'
    ]
    no_fillers = list(filter(not_filler, item_list))
    # print('No fillers:\n', no_fillers)
    clean_conditions = [reformat_condition(item) for item in no_fillers]
    include_subject_ns = [(subj_n,) + item for item in clean_conditions]
    row_dicts = [create_row_dict(subject_fields, row) 
        for row in include_subject_ns]
    write_to_csv(subj_output_name, row_dicts, subject_fields)
    # return include_subjects


#################################################
## Processing each subject
#################################################

def filter_by_condition(cond_list, item_list):
    return [item for item in item_list if item[0][1:] in cond_list]


def item_correct(item):
    # print('Correction estimation for:', item)
    return item + (int(item[2] == item[3]),)


def subj_accuracy_stats(subj_number, item_list):
    # print(item_list)
    n_correct = sum(item[4] for item in item_list)
    n_total =  len(item_list)
    accuracy = float(n_correct) / n_total
    notes = '*Below 80%' if accuracy < 0.8 else 'NA'
    # IK: this function should return accuracy, #correct, total#, maybe more?
    return (subj_number, n_correct, n_total, accuracy, notes)


def process_subj(subj_n_file_path, out_dir, conditions):
    subj_number, f_path = subj_n_file_path
    try:
        parsed_asc = parse_asc_file(f_path)
        # print(parsed_asc)
        # this is where one can insert filtering by condition list, smthng like:
        if conditions:
            # print('got this far')
            parsed_asc = filter_by_condition(conditions, parsed_asc)
        per_item_correct = [item_correct(item) for item in parsed_asc]
        # print(per_item_correct)
        subj_output_name = os.path.join(out_dir, subj_number) + '.csv'
        generate_item_table(subj_number, subj_output_name, per_item_correct)
        # formatted = prep_for_writing(subj_number, per_item_correct)
        return subj_accuracy_stats(subj_number, per_item_correct)
    except Exception as e:
        raise e
        # print('Error parsing file: ', f_path)
        # print(e)
        return (subj_number,)

#################################################
## Collecting accuracies
#################################################

def get_subj_num(file_name):
    subj_n_rgx = re.compile('\d+')
    matches = subj_n_rgx.findall(file_name)
    if not matches:
        # IK: revise this line
        print("Unable to find subject number, please check this file name: " + file_name)
    elif len(matches) > 1:
        # IK: maybe print the list of matches?
        print("Can't seem to decide which to choose" + file_name)
    return matches[0]
    

def path_and_number(folder_name, file_name):
    file_path = os.path.join(folder_name, file_name)
    subj_number = get_subj_num(file_name)
    return (subj_number, file_path)


def compute_accuracy(asc_dir, out_dir, accuracy_file, conditions):
    # IK: rename ^^ this
    accuracy_fields = [
    'subject',
    'number correct',
    'number total',
    'accuracy',
    'notes']
    asc_file_list = (f_name for f_name in os.listdir(asc_dir) 
        if f_name.endswith('.asc'))
    subj_list = (path_and_number(asc_dir, f_name) for f_name in asc_file_list)
    # print('got this far')
    accuracy_data = [process_subj(subj, out_dir, conditions)
                                    for subj in subj_list]
    accuracy_data_dicts = [create_row_dict(accuracy_fields, subj_line) 
                                    for subj_line in accuracy_data]
    # IK: write this data to a file
    output_file = os.path.join(out_dir, accuracy_file)
    write_to_csv(output_file, accuracy_data_dicts, accuracy_fields)


#################################################
## User input and main()
#################################################


def ask_for_conditions():
    cond_string = input('Please enter the conditions you are interested in, separated by spaces.\n')
    cond_list = cond_string.strip().split()
    if len(cond_list) == 0:
        print("Unable to detect any conditions, will look at all trials.\n")
    # print(cond_list)
    return cond_list


def ik_main():
    # IK: maybe ask user for directory input?
    ASC = 'asc'
    OUTPUT = 'Accuracy'
    relevant_conditions = ask_for_conditions()
    accuracy_file = input('Please specify name of accuracy table file.\n')
    compute_accuracy(ASC, OUTPUT, accuracy_file, relevant_conditions)

if __name__ == '__main__':
    # wyc()
    ik_main()