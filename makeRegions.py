#by: Shevaun Lewis
#created: 10/22/10

#This script converts a list of stimulus sentences with the regions delimited
# by forward slashes (a DEL file) into a REG file, which lists the (x,y) character 
# coordinates of the boundaries of each region.

#input: python del-make_reg_file.py 'input file' (no quotes around filename)
#output: text file 'regions.reg.txt' in same directory

#input file:
#input file contains one line per item per condition.
#Item and condition numbers must correspond to those used in the EyeTrack script file.

import sys
import string


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


def main(del_file_name, reg_file_name):
    with open(del_file_name) as del_file:
        reglines = []

        for line in del_file:
            item = line.split(" ")
            s = " ".join(item[2:])
            l = s.split('\\n')
            regstarts0 = []
            for sentence in l:
                cl = l.index(sentence)
                for char in sentence:
                    if char == '/':
                        i = sentence.index(char)
                        regstarts0.append(str(i)+' '+str(cl))
                        sentence = sentence[0:i]+sentence[i+1:]
                    nregions0 = len(regstarts0)

            reglines.append(str(item[0])+' '+str(item[1])+' '+str(nregions0)+' '+' '.join(regstarts0))
    with open(reg_file_name, 'w') as region_file:
        for row in reglines:
            reg_file.write(str(row)+'\n')


if __name__ == '__main__':
    file_questions = [
    'input (DEL) file name',
    'output (REG) file name'
    ]
    file_names = ask_user_questions(file_questions)
    main(file_names['input (DEL) file name'], 
        file_names['output (REG) file name'])