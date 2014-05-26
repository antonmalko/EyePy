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
# library for shared functions
import re
from csv import DictWriter


def ask_user_questions(question_sequence, use_template=True, return_list=False):
    '''Given a sequence of items (can be a list or a dictionary, anything
    that supports iteration), prints prompts for every item in the shell
    so that the user can input a value for every item.
    Returns a dictionary of (item_name : user_input) pairings.
    '''
    # define question prompt template and return variable
    q_template = 'Please enter the {} below:\n'

    if use_template:
        question_sequence = (q_template.format(q) for q in question_sequence)

    answers = (input(question) for question in question_sequence)
    if return_list:
        return list(answers)
    return dict(zip(question_sequence, answers))


def ask_single_question(question):
    return ask_user_questions([question], 
        use_template=False, 
        return_list=True)[0]


# define regular expression that checks for "yes" answers
YES_RGX = re.compile('y(:?e[sa]|up)?', re.IGNORECASE)

def is_yes(user_input):
    return bool(YES_RGX.match(user_input))


def is_DA1_file(filename):
    '''Checks if a file name has DA1 extension.
    Currently accepts both ".da1" and ".DA1" files.
    Retunrs a boolean (True or False).
    '''
    return filename.endswith('.da1') or filename.endswith('.DA1')


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


def write_to_txt(file_name, data, mode='w', **kwargs):
    '''Writes data to a text file.

    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of strings or lists of strings (not a string)
    :type addNewLines: bool
    :param addNewLines: determines if it's necessary to add newline chars to
    members of list
    :type kwargs: dict
    :param kwargs: key word args to be passed to list_to_plain_text, if needed
    '''
    with open(file_name, mode=mode) as f:
        f.writelines(data)


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


def get_subj_num(file_path):
    '''Given a filename string returns any substring that consists of digits.
    If multiple such substrings are found, returns the first one.
    If no such substrings are found, returns empty string and warns the user.
    '''
    subj_n_rgx = re.compile('\d+')
    # first we make sure we're dealing with file's name, not full path to it
    file_name = os.path.basename(file_path)
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


def gen_file_paths(dir_name, filter_func=None):
    if filter_func:
        return (os.path.join(dir_name, file_name) 
            for file_name in os.listdir(dir_name)
            if filter_func(file_name))
    return (os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name))