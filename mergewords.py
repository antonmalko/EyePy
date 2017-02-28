"""This script defines functions to add word information into the R table. It relies on functions from util.py from EyePy script collection and is supposed to be run automatically from generate_R_table.py. 
If you have an older version of generate_R_table.py without the call to this script, you can run it manually as well.
"""

# Created by Anton Malko in January 2016


###########################################################
## Imports
###########################################################
# import regex lib
import re
# import some aux functions 
from util import read_table, write_to_table, ask_user_questions, is_yes
# import function to get non-adjacent elements from a list
from operator import itemgetter


###########################################################
## Function for getting word info
###########################################################

def make_word_dict(del_file):
    '''A function to create dictionary of the following kind:
    key = tuple (condition, item, region)
    value = words in a given condition, item, region.
    
    The values are taken form .del file with region mark-up
    '''
    word_dict = {}
    with open(del_file) as del_file:
    	# split into condition number, item number, words in the sentence
        split_lines = [line.strip().split(' ') for line in del_file]
    for line in split_lines:
    	# extract condition and item number
        item_info = [str(line[0]), str(line[1])]
        # remove newlines symbols in the beginning of the line
        # or after a region boundary
        line = [re.sub('(^|/)\\\\n', '\\1', s) for s in line]
        # if the newlines symbols are in the middle of the line,
        # replace them with whitespaces
        line = [re.sub('\\\\n', ' ', s) for s in line]
        # split by /, which denote region boundaries
        item_sents = ' '.join(line[2:]).split('/')
        #item_sents = [s.replace('\n','') for s in item_sents]
        res = dict((tuple(item_info + [str(count)]), word) for count, word in enumerate(item_sents))
        word_dict.update(res)

    return word_dict

    
###########################################################
## The main function
###########################################################

def add_words(del_file, table_file, output_file):
    '''
    The function takes three arguments
    - Name of the .del file containing region mark-up
    - Name of the R table, generateed by generate_R_table.py
    - name for the modified table, containing word info
    
    It adds two new columns:
    - Words from each region
    - Length of every region
    '''
    print("Adding word information...")
    word_dict = make_word_dict(del_file)
    tabl = read_table(table_file)
    tabl = [list(x) for x in tabl]
    tabl[0] = [
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
        'words',
        'wordsLen'
    ]

    for i in range(1, len(tabl)):
	    word_key = itemgetter(2, 3, 6)(tabl[i])
	    # write both word and its length
	    tabl[i].extend([word_dict[word_key], len(word_dict[word_key])])
		
    write_to_table(output_file, tabl, delimiter='\t')
	
	
###########################################################
## EXECUTE
###########################################################
    
if __name__ == "__main__":

    our_questions = ["DEL filename", "R table filename"]
    
    # get file names, using function from util.py
    file_names = ask_user_questions(our_questions)
    
    # ask whether the user wants to over-write the existing table. If no, 
    # ask for the new name
    output_file = input ("Do you wih to save changes into existing table?" + 
        "If no, type the name of the new file; otherwise, type 'yes': ")
    if is_yes(output_file):
        output_file = file_names["R table filename"]
        
    add_words(file_names["DEL filename"], file_names["R table filename"], output_file)
