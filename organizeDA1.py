##by: Shevaun Lewis
##date updated: 3/11/11
##updated by: Shayne Sloggett
## revised 5/2014 by Ilia Kurenkov

# import functionality from utility module
from util import *

def classify_line(line):
    trial_types = {
    '2' : 's',
    '6' : 'q',
    '7' : 'q',
    }
    thing = line.split()[4]
    if thing in trial_types:
        return trial_types[thing]
    return 'reject'


def parse_da1_file(file_name):
    subj_number = get_subj_num(file_name)
    with open(file_name) as da1file:
        non_empty = [line for line in da1file if line]
        sentences = [line for line in non_empty if classify_line(line) is 's']
        questions = [line for line in non_empty if classify_line(line) is 'q']
        rejects = [line for line in non_empty if classify_line(line) is 'reject']
    return (subj_number, sentences, questions, rejects)


def sort_da1_data(data_dir):
    file_list = gen_file_paths(data_dir, filter_func=is_DA1_file)
    return [parse_da1_file(f_name) for f_name in file_list]


def create_folder(root_path, study_exp_name, suffix, data):
    out_root = os.path.join(root_path, study_exp_name + suffix)
    os.makedirs(out_root, exist_ok=True)
    existing_data = (item for item in data if len(item[1]) > 0)
    for subj_n, sents in existing_data:
        subj_file_name = subj_n + '-' + study_exp_name + suffix + '.da1'
        file_path = os.path.join(out_root, subj_file_name)
        # write_to_txt(file_path, sents, AddNewLines=True)
        write_to_txt(file_path, sents)


def write_da1(study_exp_name, data, nest_under=None):
    suffixes = [
    ('-s', 1),
    ('-q', 2),
    ('-reject', 3)
    ]
    if nest_under:
        root_path = os.path.join(nest_under, study_exp_name + '-sorted')
    else:
        root_path = study_exp_name + '-sorted'
    for suff, index in suffixes:
        relevant = ((item[0], item[index]) for item in data)
        create_folder(root_path, study_exp_name, suff, relevant)


def get_study_name(dir_name):
    normed_dir = os.path.normpath(dir_name)
    return os.path.basename(normed_dir).split('-')[0]


def load_da1_file(file_path, index):
    subj_number = get_subj_num(file_path)
    starter = (subj_number, [], [], [])
    with open(file_path) as da1file:
        subj_items = [line for line in da1file]
    return starter[:index] + (subj_items,) + starter[index + 1:]


def load_sorted_da1(sorted_dir):
    # consider passing this around as an argument to change program's overall behavior
    suffixes = [
    ('-s', 1),
    ('-q', 2),
    ('-reject', 3)
    ]
    # think about making following line a bit simpler or clearer as to its purpose
    study_name = get_study_name(sorted_dir)
    sorted_da1 = []
    for suffix, index in suffixes:
        suff_root = os.path.join(sorted_dir, study_name + suffix)
        subj_files = gen_file_paths(suff_root)
        sorted_da1 += [load_da1_file(f, index) for f in subj_files]
    return sorted_da1


def condition_filter(ranges):
    start, total = int(ranges[0]), int(ranges[1])
    return [str(n) for n in range(start, start + total)]


def by_condition(item, cond_range):
    s_number, sents, questions, rejects = item
    exp_sents = [s for s in sents if s.split()[1] in cond_range]
    exp_qs =  [q for q in questions if q.split()[1] in cond_range]
    exp_rej =  [r for r in rejects if r.split()[1] in cond_range]
    return (s_number, exp_sents, exp_qs, exp_rej)

gen_q = '''
Do you need to split the DA1s into -s, -q, and -reject files?
(Answer "no" if you already have the data split)
'''
by_exp_question = '''
Do you want to split the data by experiment?
'''
by_exp_question2 = '''
Do you want to split the data by more experiments?
'''

def main():
    split_study = ask_unique_question(gen_q)
    # data_dir = ask the user for it
    # same for study name
    if is_yes(split_study):
        questions = [
        'folder with unsorted DA1 files',
        'name of your study',
        ]
        [da1_folder, study_name] = ask_user_questions(questions, return_list=True)
        sorted_da1s = sort_da1_data(da1_folder)
        write_da1(study_name, sorted_da1s)
    else:
        da1_folder = ask_unique_question('Enter sorted files folder:\n')
        sorted_da1s = load_sorted_da1(da1_folder)
        study_name = da1_folder

    experiment_meta_qs = [
    'Experiment name',
    'First condition number',
    'Total number of conditions'
    ]

    experiment_decision = ask_unique_question(by_exp_question)
    splitting_by_experiment = is_yes(experiment_decision)

    while splitting_by_experiment:
        exp_meta_data = ask_user_questions(experiment_meta_qs, return_list=True)
        exp_filter = condition_filter(exp_meta_data[1:])
        exp_data = (by_condition(item, exp_filter) for item in sorted_da1s)
        # exp_path = os.path.join(study_name, exp_meta_data[0])
        exp_path = exp_meta_data[0]
        write_da1(exp_path, exp_data, nest_under=da1_folder)
        continue_decision = ask_unique_question(by_exp_question2)
        splitting_by_experiment = is_yes(continue_decision)


if __name__ == '__main__':
    main()