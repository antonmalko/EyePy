##by: Shevaun Lewis
##date updated: 3/11/11
##updated by: Shayne Sloggett
## revised 5/2014 by Ilia Kurenkov

from util import *
from collections import defaultdict

import os
import splitDA1

## Get info from user.

# we need the following info:
# whether they want to split da1s (y/n)
# if yes, then we split the data simply into -s, -q, -reject piles
# fodler address with DA1 files (tab completion!)
# name of study

# ask if they want to split into multiple experiments
# for every experiment that they list, ask then for first condition and number of conditions
# run the da1splitEXpfolder

# check for similarities between da1splitExpFolder and da1splitTypeFolder

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

# print("Do you need to split the DA1s into -s, -q, and -reject files?")

# try:
#     DOSPLIT = str(input("y or n:"))
# except NameError:
#     print('Error: must input y or n')
#     exit()
# except ValueError:
#     print('Error: must input y or n')
#     exit()

# if DOSPLIT=="y":
#     print("DA1 files for both sentences and questions should be stored in a single folder.")
#     print("Filenames should be in the format ###-study.da1, where:")
#     print("	a. ### is a *3-digit* code for the subject number")
#     print("	b. 'study' is the name of the study")
#     print("These files should be stored inside a single folder. Enter that folder below.")

# else:
#     print("DA1 files should be stored in three folders, one each for -s, -q, and -reject files.")
#     print("Filenames should be in the format ###-study-s.da1, ###-study-q.da1, and ###-study-r.da1, where:")
#     print("	a. ### is a *3-digit* code for the subject number")
#     print("	b. 'study' is the name of the study")
#     print("	c. -s, -q and -r represent whether the file is for sentence, question or reject trials")
#     print("These three folders should be stored inside a single folder. Enter that directory address for that folder below.")

# try:
#     DATAFOLDER = str(input("Complete directory address with DA1 files:"))
# except NameError:
#     print('Error: must be a string')
#     exit()
# except ValueError:
#     print('Error: must be a string')
#     exit()

# if DOSPLIT=="y":
#     try:
#         STUDYNAME = str(input("Name of study:"))
#     except NameError:
#         print('Error: must be a string')
#         exit()
#     except ValueError:
#         print('Error: must be a string')
#         exit()

#     newfolders = splitDA1.DA1splitTypeFolder(DATAFOLDER, STUDYNAME)
#     print("Done. The processed DA1 files are now located in the new folder "+STUDYNAME+"-sorted, located inside your original data folder.")
# else:
#     foldernames = os.listdir(DATAFOLDER)
#     newfolders = [DATAFOLDER+"/"+foldernames[2], DATAFOLDER+"/"+foldernames[0], DATAFOLDER+"/"+foldernames[1]]

# print("Do you need to split the DA1 files into separate experiments?")

# if DOSPLIT=="y":
# 	DATAFOLDER = DATAFOLDER+"/"+STUDYNAME+"-sorted"

# try:
#     CONTINUE = str(input("y or n:"))
# except NameError:
#     print('Error: must input y or n')
#     exit()
# except ValueError:
#     print('Error: must input y or n')
#     exit()

# while CONTINUE=="y":
#     try:
#         EXPNAME = str(input("Enter the experiment name:"))
#     except NameError:
#         print('Error: must be a string')
#         exit()
#     except ValueError:
#         print('Error: must be a string')
#         exit()

#     try:
#         FIRSTCOND = int(input("Enter the number of the first condition for this experiment (from EyeTrack):"))
#     except NameError:
#         print('Error: must be an integer')
#         exit()
#     except ValueError:
#         print('Error: must be an integer')
#         exit()

#     try:
#         NUMCONDS = int(input("Enter the number of conditions for this experiment:"))
#     except NameError:
#         print('Error: must be an integer')
#         exit()
#     except ValueError:
#         print('Error: must be an integer')
#         exit()

#     expFolder = DATAFOLDER+"/"+EXPNAME+"-sorted"
#     os.mkdir(expFolder)
#     expFolderS = expFolder+"/"+EXPNAME+"-s"
#     os.mkdir(expFolderS)
#     expFolderQ = expFolder+"/"+EXPNAME+"-q"
#     os.mkdir(expFolderQ)
#     expFolderR = expFolder+"/"+EXPNAME+"-reject"
#     os.mkdir(expFolderR)

#     splitDA1.DA1splitExpFolder(newfolders[0], expFolderS, FIRSTCOND, NUMCONDS, EXPNAME)
#     splitDA1.DA1splitExpFolder(newfolders[1], expFolderQ, FIRSTCOND, NUMCONDS, EXPNAME)
#     splitDA1.DA1splitExpFolder(newfolders[2], expFolderR, FIRSTCOND, NUMCONDS, EXPNAME)
    
#     print("Done. The processed DA1 files have been stored in "+expFolder+", located within your original data folder.")
#     print("Do you want to get another experiment?")
#     try:
#         CONTINUE = str(input("y or n:"))
#     except NameError:
#         print('Error: must input y or n')
#         exit()
#     except ValueError:
#         print('Error: must input y or n')
#         exit()
# else:
#     print("Ok, bye!")
