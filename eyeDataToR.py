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

# Import other required files; these should be in the same directory
from eyeMeasures import *


###########################################################
## Interacting with the user
###########################################################

CUTOFF_PROMPT = '''The current cutoff settings are as follows.
low: {0}
high: {1}
Would you like to change them?
N.B. Type yes (or any of its variations) to change or anything else to proceed with current settings.\n'''


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
    file_paths = tuple(gen_file_paths(directory, filter_func=is_DA1_file))
    subj_numbers = map(get_subj_num, file_paths)
    if table_type is 'fixations':
        tables = map(read_fixation_table, file_paths)
    elif table_type is 'questions':
        tables = map(read_question_table, file_paths)
    else:
        # if the table type is unrecognizable, inform user and stop the program
        error = 'Not sure what to do with this table type: {0}\nCheck your code!'
        raise Exception(error.format(table_type))
    return dict(zip(subj_numbers, tables))


def create_subj_tables(sentence_dir, question_dir):
    '''Given folder names for sentences and questions returns a list of
    (subject_number, fixation_table, question_table) tuples.
    This is achieved by first creating two dictionaries, one for fixation files
    and one for question files. Both are indexed by subject numbers.
    '''
    # dictionaries of subj_n: table pairings
    fixation_paths = load_subj_tables(sentence_dir, 'fixations')
    question_paths = load_subj_tables(question_dir, 'questions')
    # start out by listing all the subjects present in both dictionaries
    all_data = [(subj, f_table, question_paths[subj])
                    for subj, f_table in fixation_paths.items()
                    if subj in question_paths]
    # add to these subjects who only have fixation files for them
    all_data += [(subj, f_table, None)
                    for subj, f_table in fixation_paths.items()
                    if subj not in question_paths]
    # add also subjects who only have question files associated with them
    all_data += [(subj, None, q_table)
                    for subj, q_table in question_paths.items()
                    if subj not in fixation_paths]
    return all_data



###########################################################
## Making a .reg file
###########################################################

SLASH_RGX = re.compile('/')

def get_region_indices(sentences): 
    all_indeces = iter([])
    number_of_regions = 0
    for sent, index in zip(sentences, count()):
        sent_indeces = (match.start() for match in SLASH_RGX.finditer(sent))
        normalized = [indx - normalizer 
            for indx, normalizer in zip(sent_indeces, count())]
        number_of_regions += len(normalized)
        x_y_sequence = chain(*zip(normalized, repeat(index)))
        all_indeces = chain(all_indeces, x_y_sequence)

    string_indices = (str(index) for index in all_indeces)

    return (str(number_of_regions),) + tuple(string_indices)
                                                                                                                                                                                                                            

def make_regions(del_file_name):
    with open(del_file_name) as del_file:
        split_lines = [line.split(' ') for line in del_file]

    item_info = ((str(item[0]), str(item[1])) for item in split_lines)
    sentence_items = (' '.join(item[2:]).split('\\n') for item in split_lines)
    reg_indeces = map(get_region_indices, sentence_items)
    return (item + indices for item, indices in zip(item_info, reg_indeces))


def get_region_table(file_name):
    # IK: include some print statements in this function
    if '.reg' in file_name:
        print('This looks like a region file. I can load it directly')
        return RegionTable(file_name, 0, 1)
    elif '.del' in file_name:
        print('This looks like a .del file. I will turn it into a region file.')
        region_data = make_regions(file_name)
        print('Successfully generated region data from DEL file.')
        reg_file_name = file_name.split('.del')[0] + '.reg'
        write_to_table(reg_file_name, region_data, delimiter=' ')
        print('Saved region data to "{0}"'.format(reg_file_name))
        return RegionTable(reg_file_name, 0, 1)


###########################################################
## Per/Region operations
###########################################################

def count_exclusions(subj, excluded, all_fixations):
    excluded_count = sum(map(len, excluded))
    all_count = sum(map(len, all_fixations))
    return (subj, excluded_count, all_count)


def zero_to_NA(fixation_measure, binomial_measures):
    """Given a fixation measure as a tuple consisting of
    (name_of_measure, calculated_value) and a list of binomial measures,
    sets the value to "NA" if the measure in question is binomial AND the raw
    value is equal to zero. Otherwise returns the value unchanged.
    """
    measure_name, value = fixation_measure
    if measure_name not in binomial_measures and value == 0:
        return (measure_name, 'NA')
    return (measure_name, value)


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
        measure_to_NA = zero_to_NA(raw_measure, binomial_measures)
        yield (m_name, measure_to_NA)


def measures_per_trial(subj, t_fields, q_fields, region_list, fixations):
    '''This function is really just a "fancy" wrapper for a very simple 
    subsetting operation. We take the first 3 members of the trial list.
    '''
    subj_number = tuple(subj)
    for t, q, regions, fix in zip(t_fields, q_fields, region_list, fixations):
        # fil = filter_fixations(cutoffs, fixations)
        # enumerated = load_subj_regions(table_of_regions, cond_item)
        fields = t + q
        for (index, reg), fix in zip(regions, fil):
            reg_fields = reg + tuple(index + 1)
            measures = region_measures(reg, fixations)
            for measure in measures:
                yield subj_number + fields + reg_fields + measure


def question_info(sentence_table, question_table, answer_key):
    ''' A generator for subject accuracy per item. '''
    if question_table:
        for cond_item in sentence_table:
            item = cond_item[1]
            try:
                RT, button = q_table[cond_item]
                correct_button = answer_key[item][0]
                accuracy = int(button == correct_button)
                yield (RT, accuracy)
            # if this fails, set both fields to NA
            except:
                yield ('NA', 'NA')
    else:
        while True:
            yield ('NA', 'NA')


def filter_fixations(cutoffs, fixations):
    low_cutoff, high_cutoff = cutoffs
    for fix in fixations:
        if low_cutoff < fix < high_cutoff:
            yield fix


def split_trials_from_fixations(fixation_table):
    trial_fields = (order_etc 
        for cond_item, (order_etc, fixations) in fixation_table)
    fixations = (fixations 
        for cond_item, (order_etc, fixations) in fixation_table)
    return (trial_fields, tuple(fixations))


def load_subj_regions(table_of_reg, f_table):
    try:
        region_list = (table_of_regions[cond_item] for cond_item in f_table)
    except KeyError as e:
        # IK: pass problematic key to print statement
        print('Missing region information for this cond/item: ' + cond_item)
        raise
    return (enumerate(regions) for regions in region_list)


def process_subj(subjects, table_of_regions, answer_key, cutoffs):
    '''This function takes a subject number with corresponding fixation and 
    question table and constructs a list of tuples to be transformed into
    rows of the output file.
    '''
    for subj_number, f_table, q_table in subjects:
        print('Processing subject #' + subj_number)
        if f_table:
            print('Found fixation data for this subject, will compute measures.')
            regions = load_subj_regions(table_of_regions, f_table)
            trials, fixations = split_trials_from_fixations(f_table)
            filtered_fixations = filter_fixations(cutoffs, fixations)
            q_infos = question_info(f_table, q_table, answer_key)
            subj_data = measures_per_trial(subj_number, trials, q_infos,
                regions, filtered_fixations)
            exclusions = count_exclusions(subj_number, 
                filtered_fixations, 
                fixations)
            yield (subj_data, exclusions)
        else:
            print('Found no fixation data for subject. Skipping.')


###########################################################
## Putting it all together...
###########################################################

def main(enable_user_input=True):
    # IK: think about generalizing using experiment names?
    # IK: the default files dictionary is there mostly for development
    default_files = {
        'REG (or DEL) filename': 'output.reg.txt',
        'Question key filename': 'expquestions.txt',
        'Sentence data folder': 'Gardenias-s',
        'Question data folder': 'Gardenias-q',
        'Output filename': 'testing-loopless.csv',
    }
    # define list of questions to be asked of user if defaults aren't used
    our_questions = [
        'REG (or DEL) filename',
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
    table_of_regions = get_region_table(file_names['REG (or DEL) filename'])
    # Read in question answer key, create dictionary.
    # Key = item number; value = [correctButton, LorR]
    answer_key = dictTable(read_table(file_names['Question key filename']))
    # Generate table files for all subjects
    tables_by_subj = create_subj_tables(file_names['Sentence data folder'],
                                        file_names['Question data folder'])
    # process all the subject data
    all_subj_data = tuple(process_subj(tables_by_subj, 
            table_of_regions, 
            answer_key, 
            cutoffs))
    subj_rows = (rows for rows, exclusions in all_subj_data)
    # make data compatible with csv.DictWriter.writerows()
    flattened_subj_rows = chain(*subj_rows)

    write_to_table(file_names['Output filename'],
        flattened_subj_rows,
        header=output_header,
        delimiter='\t')

    exclusion_header = [
    'Subject',
    'Excluded',
    'Total'
    ]
    subj_exclusions = (exclusions for rows, exclusions in all_subj_data)
    write_to_table('excluded_fixation_counts.csv',
        subj_exclusions,
        header=exclusion_header
        )


if __name__ == '__main__':
    # main(enable_user_input=False)
    main()