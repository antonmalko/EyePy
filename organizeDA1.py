##by: Shevaun Lewis
##date updated: 3/11/11
##updated by: Shayne Sloggett
## revised 5/2014 by Ilia Kurenkov

# IK: for now importing repeat fxn from itertools, may want to revise this
from itertools import repeat
# import functionality from utility module
from util import *


###############################################################################
## processing unsorted DA1 files
###############################################################################

def classify_line(line):
    '''Given a line (as a list of strings), determines what type of trial 
    this line is: whether it is a question, a sentence or a rejected trial.
    '''
    trial_types = {
    '2' : 's',
    '6' : 'q',
    '7' : 'q',
    }
    item_type = line[4]
    if item_type in trial_types:
        return trial_types[item_type]
    return 'reject'


def parse_da1_file(file_name):
    '''Given a file name extracts the subject number from it as well as all the 
    sentence, question and rejected items for this subject.
    Returns a tuple of the form:
    (subject_number, sentence_list, question_list, rejected_list)
    '''
    # using function imported from util module
    subj_number = get_subj_num(file_name)
    with open(file_name) as da1file:
        # we start by filtering out all empty lines
        non_empty = [line.strip().split() for line in da1file if line]
        # we then collect the sentence, question and rejected lists
        sentences = [line for line in non_empty if classify_line(line) is 's']
        questions = [line for line in non_empty if classify_line(line) is 'q']
        rejects = [line for line in non_empty if classify_line(line) is 'reject']
    return (subj_number, sentences, questions, rejects)


def sort_da1_data(data_dir):
    '''Sorts a folder with DA1 files.
    Given a folder name, loops over all DA1 files in it and for each file
    creates a tuple with the subject number tied to the corresponding sentence, 
    question and rejected trials.
    '''
    print('Sorting DA1 files from {0}'.format(data_dir))
    # generate the paths to files using function from util module
    file_list = gen_file_paths(data_dir, filter_func=is_DA1_file)
    # we then run parse_da1_file function on every member of file_list
    return list(map(parse_da1_file, file_list))


###############################################################################
## loading sorted DA1s
###############################################################################

def get_study_name(dir_name):
    '''Given a folder name extracts the study name from it, assuming the following 
    folder name format:
    STUDY_NAME-sorted
    '''
    normed_dir = os.path.normpath(dir_name)
    return os.path.basename(normed_dir).split('-')[0]


def load_da1_file(file_path, index):
    '''This function loads only sentence or question or rejection items
    for a subject from a da1 file and returns them in the same format as if we 
    read in an unsorted da1 file:
    (subject#, sentences, questions, rejects)
    However, in this case two of the lists will be empty, as we are loading a
    sorted file.
    The "index" argument deterimines which one of the three lists gets populated
    with the items extracted from the file.
    '''
    subj_number = get_subj_num(file_path)
    subj_frame = [subj_number, [], [], []]
    with open(file_path) as da1file:
        subj_frame[index] = [line.strip().split() for line in da1file]
    return tuple(subj_frame)


def load_sorted_da1(sorted_dir_path):
    '''Given path to a folder with the sorted DA1 files, reads in said files
    and returns the same data structure as sort_da1_data, namely a list of
    tuples where subject numbers are bound to lists of sentence, question, rejected
    items.
    '''
    print('Loading sorted DA1s from {0}'.format(sorted_dir_path))
    suffixes = [
    ('-s', 1),
    ('-q', 2),
    ('-reject', 3)
    ]
    study_name = get_study_name(sorted_dir_path)
    sorted_da1 = []
    for suffix, index in suffixes:
        type_root = os.path.join(sorted_dir_path, study_name + suffix)
        subj_files = gen_file_paths(type_root)
        sorted_da1 += [load_da1_file(f, index) for f in subj_files]
    print('Loaded successfully.')
    return sorted_da1


###############################################################################
## Selecting items for only one experiment
###############################################################################

def condition_filter(start, total):
    '''Given a start and an end value returns the integer range spanned by these
    numbers.
    The integers are converted to strings so as to make comparing them with
    strings obtained from files easier.
    Assumes that user will give inputs > 0 for the total argument.
    '''
    start_int, total_int = int(start), int(total)
    return list(map(str, range(start_int, start_int + total_int)))


def get_exp_items(item, cond_range):
    '''Given a (subject#, sents, questions, rejects) tuple as well as a range of
    conditions selects only those sentence/question/reject items whose second element
    (the condition code) is found in the range of permissible conditions.
    '''
    # unpack the item tuple
    s_number, sents, questions, rejects = item
    # subset sentences, questions, rejections
    exp_sents = [s for s in sents if s[1] in cond_range]
    exp_qs =  [q for q in questions if q[1] in cond_range]
    exp_rej =  [r for r in rejects if r[1] in cond_range]
    # put things back together and return
    return (s_number, exp_sents, exp_qs, exp_rej)


###############################################################################
## writing sorted DA1s to folders
###############################################################################

def create_folder(root_path, study_exp_name, suffix, data):
    '''Given a root path as well as a study or experiment name, a suffix 
    (e.g. -s or -q) and data to write, creates an output folder under the root_path
    directory with the passed suffix.
    Then creates files for all the subjects that have non-empty data for 
    this folder.
    '''
    # we start by setting up the output folder
    output_root = os.path.join(root_path, study_exp_name + suffix)
    os.makedirs(output_root, exist_ok=True)
    # we then make sure we're not writing empty lists to files
    existing_data = (item for item in data if len(item[1]) > 0)
    # for all subjects that have data associated with them...
    for subj_n, trials in existing_data:
        # create the name for the subject's file and turn it into a path
        subj_file_name = subj_n + '-' + study_exp_name + suffix + '.da1'
        subj_file_path = os.path.join(output_root, subj_file_name)
        write_to_table(subj_file_path, trials, delimiter=' ')


def write_da1(study_exp_name, data, nest_under=''):
    '''Given a study or experiment name as well as the data for writing,
    creates a folder corresponding to the experiment/study name and writes
    data to subfolders inside it, one for every suffix in the "suffixes" list.
    The suffixes stand for be basic trial types: sentences, questions, rejections.
    The optional nest_under argument can specify that the whole output folder
    should be created inside the folder passed as "nest_under".
    '''
    suffixes = [
    ('-s', 1),
    ('-q', 2),
    ('-reject', 3)
    ]
    # set the root path to different things based on whether nest_under is provided
    if nest_under:
        root_path = os.path.join(nest_under, study_exp_name + '-sorted')
    else:
        root_path = study_exp_name + '-sorted'
    print('Writing sorted DA1s to {0}'.format(root_path))
    for suff, index in suffixes:
        # use the index variable to select only data relevant for this suffix
        relevant = [(item[0], item[index]) for item in data]
        create_folder(root_path, study_exp_name, suff, relevant)


###############################################################################
## Running the code
###############################################################################

SPLIT_WHOLE_STUDY = '''
Do you need to split the DA1s into -s, -q, and -reject files?
(Answer *no* if you already have the data split.)
'''
START_EXP_SPLIT = '''
Do you want to split the data by experiment?
'''
MORE_EXP_SPLIT = '''
Do you want to split the data by more experiments?
'''

def main():
    split_study = ask_single_question(SPLIT_WHOLE_STUDY)
    if is_yes(split_study):
        questions = [
        'folder with unsorted DA1 files',
        'name of your study',
        ]
        [da1_folder, study_name] = ask_user_questions(questions, return_list=True)
        sorted_da1s = sort_da1_data(da1_folder)
        write_da1(study_name, sorted_da1s)
        study_root = study_name + '-sorted'
    else:
        sorted_folder = ask_single_question('Enter the sorted files folder:\n')
        sorted_da1s = load_sorted_da1(sorted_folder)
        study_root = sorted_folder

    experiment_meta_qs = [
    'name of your experiment',
    'first condition for this experiment',
    'total number of conditions for this experiment'
    ]

    experiment_split_decision = ask_single_question(START_EXP_SPLIT)
    splitting_by_experiment = is_yes(experiment_split_decision)

    while splitting_by_experiment:
        # ask some questions about the experiment
        exp_meta = ask_user_questions(experiment_meta_qs, return_list=True)
        # unpack users answers into variables
        [exp_name, first_cond, cond_total] = exp_meta
        exp_filter = condition_filter(first_cond, cond_total)
        print('Subsetting DA1 data.')
        exp_data = [get_exp_items(item, exp_filter) for item in sorted_da1s]
        write_da1(exp_name, exp_data, nest_under=study_root)
        print('Done writing data for this experiment!')
        continue_decision = ask_single_question(MORE_EXP_SPLIT)
        splitting_by_experiment = is_yes(continue_decision)

    print('Ok, bye!')

if __name__ == '__main__':
    main()