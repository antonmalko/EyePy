# IK: This file is intended to house some common functions and modules
# used by all of the eye-tracking data processing scripts
# this way we ensure that recurring tasks (like writing to files) aren't
# duplicated in several files but instead stored and defined in just one.

# This module uses some generator functions. In case you are not familiar with
# these, please feel free to read up on them here:
# https://docs.python.org/3.1/reference/simple_stmts.html#yield

# import module for OS interaction
import os, re, csv
# import regular expressions
import re
# import table file writing module
import csv
# import readline and set tab-completion based on what OS we are in
import readline
# MACOS uses "libedit" for readline functionality and has a different command
# for enabling tab completion
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
# whereas Unix (and maybe Windows) have the same command
else:
    readline.parse_and_bind("tab: complete")

###############################################################################
## Functions for interacting with users
###############################################################################

def ask_user_questions(question_sequence, use_template=True, return_list=False):
    '''Given a sequence of items (can be a list or a dictionary, anything
    that supports iteration), prints prompts for every item in the shell
    so that the user can input a value for every item.
    Returns a dictionary of (item_name : user_input) pairings.
    '''
    # define question prompt template and return variable
    q_template = 'Please enter the {} below:\n'

    if use_template:
        question_strings = [q_template.format(q) for q in question_sequence]
        answers = [input(question) for question in question_strings]
    else:
        answers = [input(question) for question in question_sequence]
    if return_list:
        return answers
    return dict(zip(question_sequence, answers))


def ask_single_question(question):
    return ask_user_questions([question], 
        use_template=False, 
        return_list=True)[0]


# define regular expression that checks for "yes" answers
_YES_RGX = re.compile('y(:?e[sa]|up)?', re.IGNORECASE)

def is_yes(user_input):
    return bool(_YES_RGX.match(user_input))

###############################################################################
## Functions for dealing with file names/paths
###############################################################################

def is_DA1_file(filename):
    '''Checks if a file name has DA1 extension.
    Currently accepts both ".da1" and ".DA1" files.
    Retunrs a boolean (True or False).
    '''
    return filename.endswith('.da1') or filename.endswith('.DA1')


_SUBJ_N_RGX = re.compile('\d+')


def get_subj_num(file_path):
    '''Given a filename string returns any substring that consists of digits.
    If multiple such substrings are found, returns the first one.
    If no such substrings are found, returns empty string and warns the user.
    '''
    # first we make sure we're dealing with file's name, not full path to it
    file_name = os.path.basename(file_path)
    # we don't want to risk finding digits from file extensions
    extensionless = file_name.split('.')[0]
    matches = _SUBJ_N_RGX.findall(extensionless)

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


###############################################################################
## Functions for writing to files
###############################################################################

def create_row_dicts(fields, data, fill_val='NA'):
    '''Helper generator function for the write_to_table(). Collecting data
    is often much more efficient and clear when this data is stored in tuples
    or lists, not dictionaries.
    Python's csv DictWriter class requires that it be passed a sequence of 
    dictionaries, however.
    This function takes a header list of column names as well as some data in
    the form of a sequence of rows (which can be tuples or lists) and converts
    every row in the data to a dictionary usable by DictWriter.
    '''
    for row in data:
        length_difference = len(fields) - len(row)
        error_message = 'There are more rows than labels for them: {0}'
        if length_difference < 0:
            print('Here are the column labels', fields)
            print('Here are the rows', row)
            raise Exception(error_message.format(length_difference))
        elif length_difference > 0:
            row = row + (fill_val,) * length_difference
        yield dict(zip(fields, row))


def write_to_table(file_name, data, header=None, **kwargs):
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
        if header:
            output = csv.DictWriter(f, header, **kwargs)
            output.writeheader()
            if 'fill_val' in kwargs:
                data = create_row_dicts(header, data, kwargs['fill_val'])
            else:                
                data = create_row_dicts(header, data)
        else:
            output = csv.writer(f, **kwargs)
        output.writerows(data)


###############################################################################
## Functions for reading in (table) files
###############################################################################

def read_table(filename):
    '''Takes a file name as a string, opens it. Once that's done, takes each
    non-empty row of the file and converts it into a tuple of strings.
    Returns a list of rows (as tuples of strings).
    '''
    with open(filename) as input_file:
        nonewlines = (line.strip() for line in input_file)
        return tuple(tuple(line.split()) for line in nonewlines if line)


def tagged_table(table_lines, one, two):
    '''Given a table iterable for every line of said iterable creates a "tag"
    by combining the elements of the line indexed by "one" and "two" into 
    a tuple and pairing that up with the rest of the line.
    '''
    tags = ((line[one], line[two]) for line in table_lines)
    return zip(tags, table_lines)


def dict_from_table(table, paired=True):
    '''Takes a table and turns it into a dictionary. By default expects the table
    to be already tagged and consist of (tag, item) pairs. This is why the "paired"
    argument is set to True by default.
    If the table being passed isn't tagged, but just a sequence of lines, it is
    necessary to set "paired" to False when calling this function and then
    it will use the first element of each line as the key and the rest of the line
    as the value.
    '''
    if paired:
        return dict(table)
    return dict((item[0], item[1:]) for item in table)


def region_coordinates(tagged_table):
    '''Expects as input a table where every line is a pairing of a 
    (condition, item) tuple with a line of the form:
    condition, item, #_of_regions, X1, Y1, X2, Y2, ...
    where X and Y are coordinates for one region.
    Assuming such a table was passed, this function converts all the coordinates
    from strings to integers so that they can be used during processing to 
    establish whether a fixation is inside a region or not.
    Once converted, the Xs and Ys are paired up as coordinates using the zip()
    function. After that every coordinate pair is combined with the following
    pair so as to indicate not just the start but also the end of a region.
    The result is sequence of the following form:
    ((X1start, Y1start), (X1end, Y1end)), ((X2start, Y2start), (X2end, Y2end)), ...
    This sequence is turned into a tuple and paired up with the (condition, item)
    tag.
    Please note that this is a generator function, which means it does not
    directly return a sequence of items described above, but instead defines
    how to loop through the input table and what to do with every item therein.
    '''
    for tag, line in tagged_table:
        # take every second member of the line starting with the 4th, convert to int
        Xes = map(int, line[3::2])
        # take every second member of the line starting with the 5th, convert to int
        Ys = map(int, line[4::2])
        coordinates = zip(Xes, Ys)
        # as starts take all coordinate pairs till the last one
        starts = coordinates[:-1]
        # as ends take all coordinate pairs except the first one
        ends = coordinates[1:]
        pairs = tuple(zip(starts, ends))
        yield (tag, pairs)


def read_region_table(regFile, one, two):
    '''Given a region file turns it into a region table where the keys are
    (condition, item) tuples and values are sequences of regions as described
    in region_coordinates().
    '''
    read_in = read_table(regFile)
    tagged = tagged_table(read_in, one, two)
    regioned = region_coordinates(tagged)
    return dict_from_table(regioned)


def fixation_data(tagged_table):
    ''' A generator of fixation data for a tagged table, every line of which
    consists of a (condition, item#) tag paired up with a sequence of 
    the following fields:
    (order, cond, item, totaltime, buttonpress, 
        [unknown], [unknown], totalfixations, 
        series of [X Y fixation_start fixation_end] groups)
    Of these fields, only the fixations are of interest to us, so the function
    condenses the sequence of fields to a sequence of (X, Y, fixation_duration)
    items.
    '''
    for tag, line in tagged_table:
        # extract X, Y coordinates, convert them to integers
        Xes = map(int, line[8::4])
        Ys = map(int, line[9::4])
        # get starts and ends of fixations, convert them to integers
        fixation_starts = map(int, line[10::4])
        fixation_ends = map(int, line[11::4])
        # compute durations by subtracting start times from end times
        fixation_durations = (end - start 
            for end, start in zip(fixation_ends, fixation_starts))
        # combine into a sequence of (X, Y, duration) tuples
        fixations = zip(Xes, Ys, fixation_durations)
        yield (tag, tuple(fixations))


def read_fixation_table(da1File):
    '''As input takes a DA1 sentence file and returns a dictionary of
    (condition, item) : ((X1, Y1, duration1), (X2, Y2, duration2), ...)
    '''
    tagged = tagged_table(read_table(da1File), 1, 2)
    fixations = fixation_data(tagged)
    return dict_from_table(fixations)


def read_question_table(da1QFile):
    ''' Returns dict of ((cond, item) : (RT, buttonpress)) entries. 
    As input assumes a DA1 question file where every line is a list of fields:
    order, cond, item, rt, buttonpress
    '''
    tagged = tagged_table(read_table(da1QFile), 1, 2)
    RT_button_press = ((tag, line[3:5]) for tag, line in tagged)
    return dict_from_table(RT_button_press)