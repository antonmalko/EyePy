# UMD Eye-tracking script

# CHANGELOG
# Edited by: Shevaun Lewis, Ewan Dunbar & Sol Lago
# 1. Added code for computing first pass-skips, 'fs' [01/11/13]
# Last updated: 04/01/14
# Major revisions by Ilia Kurenkov in Spring of 2014
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
# Coming soon (*as* soon as we finalize this)...

# import iteration functions such as chain, repeat, cycle
# c.f. https://docs.python.org/2/library/itertools.html
from itertools import *
# import everything from the utilities module
from util import *

# Import all currently supported eye-tracking measures
from eye_measures import *


###########################################################
## Putting it all together...
###########################################################

def main():
    # define list of questions to be asked of user when they run the file
    our_questions = [
        'REG (or DEL) filename',
        'Question key filename',
        'Sentence data folder',
        'Question data folder',
        'Output filename',
    ]
    # ask user to provide values for these questions using function imported 
    # from util module
    file_names = ask_user_questions(our_questions)

    # check with user about cutoff boundaries
    cutoffs = verify_cutoff_values(40, 1000)

    # Get a region dictionary in the following format.
    # Key = unique cond/item tag; 
    # value = (((xStart, yStart), (xEnd, yEnd)), ...)
    table_of_regions = get_region_table(file_names['REG (or DEL) filename'])
    # Using functions from the util module, create a dictionary of correct
    # answers to all the questions
    # Key = item number; 
    # value = (correct_button_code, LeftorRight)
    answer_key = dict_from_table(read_table(file_names['Question key filename']),
                                                    paired=False)
    # take locations of sentence and question files (all defined by the user)
    # turn these into a sequence of tuples of the form:
    # (subject#, list_of_fixations, list_of_questions)
    tables_by_subj = create_subj_tables(file_names['Sentence data folder'],
                                        file_names['Question data folder'])
    
    # collect fixation  data for all subjects as well as exclusion stats
    all_subj_data = tuple(process_subj(tables_by_subj, table_of_regions, 
            answer_key, cutoffs))
    print('Done processing. Created data for {0} subjects.'.format(len(all_subj_data)))

    # split subject data into fixation information and exclusion statistics
    # If you unpack a list of tuples using "*" and then pass it to 
    # the zip() function, you end up with two sequences: one with all the 
    # first members of the tuples and one with all the second members of the tuples
    subj_rows, subj_exclusions = tuple(zip(*all_subj_data))
    # make fixation data compatible with csv.DictWriter (use itertools fxn for that)
    # Convert it from a list of lists (one for every subject in turn consisting
    # of data rows for that subject) to a flat list of rows
    flattened_subj_rows = chain(*subj_rows)

    # define output header and write to file
    fixation_table_header = [
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

    write_to_table(file_names['Output filename'],
        flattened_subj_rows,
        header=fixation_table_header,
        delimiter='\t',
        restval=' ')

    # now define exclusion header and exclusion file name, then write to it
    exclusion_table_header = [
    'Subject',
    'Excluded',
    'Total'
    ]
    excl_file_name = 'excluded_fixation_counts.csv'
    print('Writing statistics of exclusions to *{0}*'.format(excl_file_name))
    write_to_table(excl_file_name,
        subj_exclusions,
        header=exclusion_table_header)


###########################################################
## Interacting with the user
###########################################################

CUTOFF_PROMPT = '''The current cutoff settings are as follows.
low: {0}
high: {1}
Would you like to change them?
N.B. Type yes (or any of its variations) to change or anything else to proceed with current settings.\n'''


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
    if is_yes(decision):
        # if user says something matching yes_rgx, ask them to input their own cutoffs
        user_cutoffs = ask_user_questions(['low cutoff', 'high cutoff'])
        # return their responses converted to integers
        return (int(user_cutoffs['low cutoff']), int(user_cutoffs['high cutoff']))
    # if user doesn't want to change stuff, return passed args unchanged
    return (low_cutoff, high_cutoff)


###########################################################
## General functions and dealing with files
###########################################################

def create_subj_tables(sentence_dir, question_dir):
    '''Given folder names for sentences and questions returns a list of
    (subject_number, fixation_table, question_table) tuples.
    This is achieved by first creating two dictionaries, one for fixation files
    and one for question files. Both are indexed by subject numbers.
    '''
    # dictionaries of (subj_n: table) pairings
    fixation_paths = load_subj_tables(sentence_dir, 'fixations')
    question_paths = load_subj_tables(question_dir, 'questions')
    # start out by listing all the subjects present in both dictionaries
    all_data = [(subj, f_table, question_paths[subj])
                    for subj, f_table in fixation_paths.items()
                    if subj in question_paths]
    # add subjects who only have fixation files for them
    all_data += [(subj, f_table, None)
                    for subj, f_table in fixation_paths.items()
                    if subj not in question_paths]
    # add also subjects who only have question files associated with them
    all_data += [(subj, None, q_table)
                    for subj, q_table in question_paths.items()
                    if subj not in fixation_paths]
    return all_data


def load_subj_tables(directory, table_type):
    '''Takes a directory and a string description of which table type to
    load.
    Creates a sequence of file paths for all DA1 files in the directory.
    Extracts subject numbers from the paths, then converts the file paths
    to corresponding tables. Whether fixation or question tables are loaded
    is determined by the "table_type" argument.
    Pairs up the subject numbers with the file names, then turns these pairings
    into a dictionary which is returned.
    '''
    # use function from util module to generate file paths keeping only DA1 files
    file_paths = tuple(gen_file_paths(directory, filter_func=is_DA1_file))
    # from these file paths get subject numbers
    subj_numbers = map(get_subj_num, file_paths)
    if table_type is 'fixations':
        tables = map(read_fixation_table, file_paths)
    elif table_type is 'questions':
        tables = map(read_question_table, file_paths)
    else:
        # if the table type is unrecognizable, inform user and stop the program
        error = 'Not sure what to do with this table type: {0}\nCheck your code!'
        raise Exception(error.format(table_type))
    # if tables for subjects loaded, combine them with subject numbers using
    # zip() and turn the resulting list of tuples into a dictionary
    return dict(zip(subj_numbers, tables))


###########################################################
## Making/Loading a .reg file
###########################################################

def get_region_table(file_name):
    '''Given a file name returns a region table.
    If the file name ends with .reg, loads the region table from that directly.
    If the file name ends with .del, uses that to create a .reg file and loads
    the latter.
    '''
    if '.reg' in file_name:
        print('This looks like a region file. I can load it directly')
        return read_region_table(file_name, 0, 1)
    elif '.del' in file_name:
        print('This looks like a .del file. I will turn it into a region file.')
        region_data = make_regions(file_name)
        print('Successfully generated region data from DEL file.')
        reg_file_name = file_name.split('.del')[0] + '.reg'
        write_to_table(reg_file_name, region_data, delimiter=' ')
        print('Saved region data to "{0}"'.format(reg_file_name))
        return read_region_table(reg_file_name, 0, 1)
                                                                                                                                                                                                                            

def make_regions(del_file_name):
    '''A generator function that, given a .del file name opens the file and loops
    over its lines, yielding tuples of the following form:
    (condition, item#, region_indeces)
    '''
    with open(del_file_name) as del_file:
        split_lines = [line.strip().split(' ') for line in del_file]
    for line in split_lines:
        # convert item information to strings for later writing
        item_info = (str(line[0]), str(line[1]))
        # combine the rest of the line into one string and then split it
        # by the special '\\n' symbol
        # this is used for items that span multiple lines during presentation
        item_sents = ' '.join(line[2:]).split('\\n')
        # use the result to get a list of indeces
        reg_indeces = get_region_indices(item_sents)
        yield item_info + reg_indeces


_SLASH_RGX = re.compile('/')

def get_region_indices(sentences): 
    '''Given a sequence of sentences for an item returns a tuple with
    the number of regions followed by X and Y coordinates for each region
    (number of regions, X1, Y1, X2, Y2, ...)
    '''
    # initialize collection of indices to emtpy list ...
    all_indeces = []
    # ... and number of regions to 0
    number_of_regions = 0
    for sent, line_index in zip(sentences, count()):
        # get raw indeces of where '/' occurs in the string
        sent_indeces = (match.start() for match in _SLASH_RGX.finditer(sent))
        # now we need to normalize these indeces to account for the fact that
        # we do NOT want to be counting the '/' as part of the string
        # this means that for every raw index of '/' that we find in the string
        # we have to subtract the number of times '/' had already occured in
        # the same string.
        # So for the first instance of '/' we subtract 0, for the second instance
        # we subtract 1 and so on and so forth.
        # This can easily be done with the help Python's built-in enumerate() fxn
        # https://docs.python.org/3.3/library/functions.html#enumerate
        normalized = tuple(region_index - normalizer
                    for normalizer, region_index in enumerate(sent_indeces))
        number_of_regions += len(normalized)
        # to each region index we add the line index, using itertools.repeat
        add_line_indx = zip(normalized, repeat(line_index))
        # now we need to flatten this sequence of pairs to be just a sequence
        # of X1, Y1, X2, Y2, ... strings
        x_y_sequence = chain(*add_line_indx)
        # now we add this to our collection of 
        all_indeces += list(x_y_sequence)
    # once we're done collecting all the indices, turn them into strings
    string_indices = map(str, all_indeces)
    # return a tuple: (number of regions, X1, Y1, X2, Y2,...)
    return (str(number_of_regions),) + tuple(string_indices)


###########################################################
## Per/Region operations
###########################################################


def process_subj(subjects, table_of_regions, answer_key, cutoffs):
    '''This function takes a subject number with corresponding fixation and 
    question table and constructs a list of tuples to be transformed into
    rows of the output file.
    '''
    for subj_number, f_table, q_table in subjects:
        print('Processing subject #' + subj_number)
        if f_table:
            print('Found fixation data for this subject, will compute measures.')
            # split trial info from fixations
            trials, fixations = split_trials_from_fixations(f_table)
            # compute question accuracy and get question RT
            q_acc_RT = question_info(f_table, q_table, answer_key)
            # combine trial info with question accuracy and RT
            all_trial_fields = (t + q for t, q in zip(trials, q_acc_RT))

            # make sure only fixations inside cutoffs are kept
            filtered_fixations = tuple(filter_fixations(cutoffs, fixations))
            # count the number of fixations excluded through filtering
            exclusions = count_exclusions(subj_number, 
                filtered_fixations, 
                fixations)
            # use table of regions to load per/trial regions for this subject
            regions = load_subj_regions(table_of_regions, f_table)

            # use trial fields, regions and filtered fixations to get the measures
            subj_data = measures_per_trial(subj_number, all_trial_fields,
                regions, filtered_fixations)
            yield (subj_data, exclusions)
        else:
            print('Found no fixation data for subject. Skipping.')


def load_subj_regions(table_of_reg, f_table):
    try:
        return (table_of_reg[cond_item] for cond_item in f_table)
    except KeyError as error:
        problematic_key = error.message
        print_message = 'Missing region information for this cond/item: {0}'
        raise Exception(print_message.format(problematic_key))


def split_trials_from_fixations(fixation_table):
    trial_fields = (order_etc 
        for cond_item, (order_etc, fixations) in fixation_table.items())
    fixations = (fixations 
        for cond_item, (order_etc, fixations) in fixation_table.items())
    return (trial_fields, tuple(fixations))


def question_info(sentence_table, question_table, answer_key):
    ''' A generator for subject accuracy per item. '''
    if question_table:
        for cond_item in sentence_table:
            item = cond_item[1]
            try:
                RT, subj_response = question_table[cond_item]
                correct_button = answer_key[item][0]
                # check if subject responded correctly and convert that to int
                accuracy = int(subj_response == correct_button)
                yield (RT, accuracy)
            # if this fails, set both fields to NA
            except KeyError as e:
                yield ('NA', 'NA')
    else:
        # if there is no question table found for subject, keep returning NAs infinitely
        while True:
            yield ('NA', 'NA')


def filter_fixations(cutoffs, trials):
    low_cutoff, high_cutoff = cutoffs
    for trial_fixations in trials:
        filtered = tuple((X, Y, duration)
            for X, Y, duration in trial_fixations
            if low_cutoff < duration < high_cutoff)
        yield filtered


def measures_per_trial(subj, trial_fields, region_list, trial_fixations):
    '''This function is really just a "fancy" wrapper for a very simple 
    subsetting operation. We take the first 3 members of the trial list.
    '''
    subj_number = (subj,)
    for fields, regions, fixations in zip(trial_fields, region_list, trial_fixations):
        for index, reg in enumerate(regions):
            reg_fields = (index + 1, reg[0][0], reg[1][0], reg[0][1], reg[1][1])
            measures = region_measures(reg, fixations)
            for measure in measures:
                yield subj_number + fields + reg_fields + measure


def region_measures(region, fixations):
    '''Given a region, a list of fixations, and cutoff values
    returns a list of (measure name, measure value) tuples for all the measures
    currently computed at UMD.
    Please note that all continuous measures that equal zero are set to "NA" for
    ease of later processing with R.
    '''
    # list below consists of "measure name": measure_function pairs
    # measure functions are imported from eyeMeasures
    measures = (
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
    )
    binomial_measures = ('fs', 'pr', 'prr')
    for m_name, m_calculator in measures:
        raw_measure = m_calculator(region, fixations)
        measure_to_NA = zero_to_NA(m_name, raw_measure, binomial_measures)
        yield measure_to_NA


def zero_to_NA(measure_name, measure_value, binomial_measures):
    """Given a fixation measure as a tuple consisting of
    (name_of_measure, calculated_value) and a list of binomial measures,
    sets the value to "NA" if the measure in question is binomial AND the raw
    value is equal to zero. Otherwise returns the value unchanged.
    """
    if measure_name not in binomial_measures and measure_value == 0:
        return (measure_name, 'NA')
    return (measure_name, measure_value)


def count_exclusions(subj_number, filtered, all_fixations):
    # we count how many fixations were left after filtering
    filtered_count = sum(map(len, filtered))
    # we count how many there were in total
    all_count = sum(map(len, all_fixations))
    # subtract number of filtered fixations from total number of fixations
    excluded_count = all_count - filtered_count
    return (subj_number, excluded_count, all_count)


if __name__ == '__main__':
    # main(enable_user_input=False)
    main()