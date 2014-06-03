"""
################################################################################	
# authors: Alan Mishler
#          Ewan Dunbar
# last edited: Feb 06 2011
# Feb 06 2011: fixed bug that was occurring when first experiment had only one
#              item --emd

# This script converts a list of stimulus sentences into the format required for use with EyeTrack, part of the UMass software package written by Adrian Staub. (see http://www.psych.umass.edu/eyelab/software/). This is meant for use with the Eyelink 1000. 

# input: python eyetrack_reading.py 'input file'
# output: text file 'output.script' in same directory
	# to use output.script, open file from inside EyeTrack

# format for input file:

	(#) Experiment 1
	1a. 	Item 1, condition 1.
			(Y/N question? (Correct answer))
	1b. 	Item 1, condition 2. 
			(Y/N question? (Correct answer))
	.
	.
	2a.		Item 2, condition 1.
			(Y/N question? (Correct answer))
	2b.		Item 2, condition 2.
			(Y/N question? (Correct answer))
	.
	.
	((#) Experiment 2)
	""
	((#) Fillers)
	""
	((#) Practice)
	""

# Every section must start with a heading consisting of letters and spaces and optionally starting with a '#'. Your item set may have any number of experiments, as long as every experiment has the same number of conditions (required for EyeTrack to do Latin squaring). Section headings may be repeated within item sets (as in the Psyscope format) as long as they are identical. Besides experiment sections, you may have sections for 'Fillers' and 'Practice' items. Practice items will be run first in the order they're given. 

# Every reading item must start with an item number and a letter specifying the condition. Each item may optionally be followed by a Y/N comprehension question. Each question may optionally start with a '?' and may optionally be followed by the correct answer to the question: Y(es) or (N)o. If no answer is given it will default to 'Y'. (To reverse this, edit line 150.) Having questions after some items and not others is fine.

# Spacing across and within lines doesn't matter. Sections may be arranged in any order. The actual order of item numbers doesn't matter as long as all items within a block have the same number and you don't reuse item numbers within a given experiment section. This means you can add, delete, and rearrange item sets within having to renumber them. Periods after item number and condition letter (e.g. '1a.') aren't required but look nice. Case (upper vs. lower) doesn't matter anywhere. 

# Minimally stated, the formatting requirements are as follows:

		# Every section must have a header. 
		# The first word in filler and practice section headings must be 'filler'/'practice'
		# Every experiment section must have the same number of conditions. 
		# Each entry may only be one line.
		# Only reading items should start with the (number)(letter) identifier.
		# Questions must end with a '?'
		# Section headings may start with a '#' but otherwise should consist only of letters and spaces. 
		# Within a given experiment, there can't be two items with the same item number and condition. 

# The script will output names of experiments, number of conditions/experiment, number of fillers and practice items, and number of questions. If it finds a section without a heading or detects a different number of conditions in different experimental blocks, it will output an error.

# Experiment formatting and various other parameters have to be edited manually if you don't like the defaults.  

# NOTE: for reasons that are unclear, EyeTrack sometimes displays an experimental trial or two before the practice items. This is not a bug in the script.
#        
################################################################################
"""

import re
import sys

file_in = open(sys.argv[1], 'rU')											# input file
output = open('output.script', 'wt')									# output file

	### regular expressions to search for headers and items of different types ###
item_re = re.compile(r'''
	(?P<itemline>^[ ]*(?P<itemnum>\b[\d]+)[ \t]*[a-z][ \t\.]*(?P<item>.*))	#item
	|(?P<questionline>(^[ \t.?]*(?P<question>[a-z].+\?)([ \t]*)(?P<answer>Y?N?)))	# question
	|(?P<filler>(^([ #\t]*)([ ]*)filler([ a-z]*)\n))						# fillers
	|(?P<practice>(^([ #\t]*)[ ]*practice[ a-z]*\n))					# practice
	|(?P<expline>(^([ #\t]*)[ ]*(?P<exp>([a-zA-Z]+))))			# experiment names
						''', re.I | re.X)

file_in.seek(0)			# return to first line of file

Experimental_items = [ ]
Practice_items = [ ]
Fillers = [ ]
exp_names = { }
fillers = { }
practice = { }
linenum = 0			# current line number in the input file					
itemlist = [ ]
numfillers = 0		# number of filler items, to display in stdout. Just a way for you to check that the script counted correctly.
numpractice = 0		# number of practice items, ""
numquestions = 0	# number of questions, "" 
fillers = { }	
condtotal = 0		# actual condition number for purposes of EyeTrack (e.g., for condition 2 in experiment 3, where all experiments have 5 conditions, condtotal will be 12)
cond = 0			# current condition number within an experiment
exp = 0				# current experiment number

stimtype = ['Null']	# Experimental, Filler, or Practice, for each item. Each "stim" is appended to this list. 
stim = 'NULL'	# current stimulus header type (experimental, filler, or practice)
item = 0
D = 0
E = [ ]	# experiment item strings
F = [ ]	# filler item string
P = [ ]	# practice item strings
correct_answer = {'y': 'leftTrigger', 'n': 'rightTrigger'}		

	### Add intro screen, since script can't currently handle multiline items: 

linenum = 0
for line in file_in:			
	linenum += 1
	i = item_re.match(line)
	if bool(i) == True:
		if bool(i.group('itemline')) == True:	# i.e. if it finds a sentence
			extend = True
			button = ''
			questions = ''
			sentence = i.group('item')
			trial_type = 'Reading'
			itemnum = i.group('itemnum')
			try:
				if stimtype[prevstim] == 'E':	# if sentence is an experimental item
					D = 0	# dependency index for Eyetrack. Non-zero values allow items to be put into fixed sequences.
					if itemnum in itemlist[exp - 1]:
						cond += 1
						prevstim = -1
					else:
						item += 1
						if len(itemlist[0]) == 1 and condtotal == 0: ## just finished first time through conditions - set condtotal
                                                        condtotal = cond
                                                if len(itemlist[exp-1]) == 0: ## haven't seen any conditions yet for this experiment - just augment condition
                                                                              ## this will either be 1 (experiment 1) or one more than the last condition of
                                                                              ## the previous experiment (elsewhere)
                                                        cond += 1
                                                else:                         ## we've been through all the conditions for this experiment at least once
                                                                              ## verify that the last time through, we saw the right number of conditions,
                                                                              ## and set the condition number appropriately
							if cond == exp*condtotal:
								cond = 1 + (exp - 1) * condtotal	## start numbering conditions for a new experiment (e.g. for condition one in experiment 2, 
							else:
								print('!!Error: EyeTrack requires the same number of conditions in each experiment. Number of conditions in previous blocks: %d. Number of conditions in current block: %d (line %d)' % (condtotal, cond - (exp - 1) * condtotal, linenum))
								exit()
						itemlist[exp - 1].append(itemnum)	## add item number to list of item numbers
			
				if (stim == 'F' or stim == 'P') and (stimtype[-1] == 'E'):	## check for last item in an experiment before fillers and practice, since Error above is only triggered when the previous item had the wrong number of conditions.
					if not cond == exp*condtotal:
						print('!!Error: EyeTrack requires the same number of conditions in each experiment. Number of conditions in previous blocks: %d. Number of conditions in current block: %d (line %d)' % (condtotal, cond - (exp - 1) * condtotal, linenum))
						exit()
				if stim == 'F':	# if sentence is a filler
					D = 0
					item += 1
					if numfillers == 0:	
						numfillers += 1
						cond += 1
					else:
						numfillers += 1
				if stim == 'P':	# if sentence is a practice item
					item = 1
					D += 1
					numpractice += 1
				
			except NameError:
				print('Error line %d: missing experiment heading' % linenum)
				exit()
		elif bool(i.group('questionline')) == True: 		# if it finds a question
			numquestions += 1
			extend = True
			sentence = i.group('question')
			trial_type = 'Question'
			if bool(i.group('answer')) == True:
				button = 'button = \t\t\t %s\n  '%correct_answer[i.group('answer').lower()]
			else:
				button = 'button = \t\t\t leftTrigger\n  '
			questions = '\\nYes                                                                    No'
			D += 1
			if stim == 'P':
				numpractice += 1

		elif bool(i.group('expline')) == True:	# if it finds an experiment heading
			stim = 'E'
			extend = False
			if not i.group('exp') in exp_names:
				exp_names[i.group('exp')] = linenum
				itemlist.append([ ])
				exp += 1
		elif bool(i.group('filler')) == True:
			stim = 'F'
			extend = False
			if not 'Fillers' in fillers:
				fillers['Fillers'] = linenum
		elif bool(i.group('practice')) == True:
			stim = 'P'
			extend = False
			if not 'Practice' in practice:
				practice['Practice'] = linenum
		stimtype.append(stim)
		if (stimtype[-2] == 'E') & (stimtype[-1] != 'E'):
			prevstim = -2 			# index to make sure number of conditions gets checked at last block of an experiment
		else:
			prevstim = -1
 		
 		if stim == 'P':
 			cond = 1
		trialID = '%s%dI%dD%d' %(stim, cond, item, D)	
		if stim == 'P':
			cond = 0
		if extend == True:
			if stimtype[-1] == 'E':
				E.extend(['\n','trial ',trialID,'\n  ', button, 'gc_rect =          (0 0 0 0)\n', '  inline =           |',sentence, questions,'\n', '  max_display_time = 60000\n', '  trial_type =       %s\n' % trial_type, 'end ', trialID, '\n'])
				Experimental_items.append(trialID)
			elif stimtype[-1] == 'F':
				F.extend(['\n', 'trial ',trialID,'\n  ', button, 'gc_rect =          (0 0 0 0)\n', '  inline =           |',sentence, questions, '\n', '  max_display_time = 60000\n', '  trial_type =       %s\n' % trial_type, 'end ', trialID, '\n'])
				Fillers.append(trialID)
			elif stimtype[-1] == 'P':
				P.extend(['\n','trial ',trialID,'\n  ', button, 'gc_rect =          (0 0 0 0)\n', '  inline =           |',sentence, questions, '\n', '  max_display_time = 60000\n', '  trial_type =       %s\n' % trial_type, 'end ', trialID, '\n'])
				Practice_items.append(trialID)
			if D == 1:
				seqID = '%s%dI%d' %(stim, cond, item)
				if stimtype[-1] == 'E':
					E.extend(['\nsequence S', seqID, '\n  ', seqID, 'D0', '\n  ', seqID, 'D1', '\n', 'end S', seqID, '\n'])
					Experimental_items[-2] = Experimental_items[-2],Experimental_items[-1]
					Experimental_items.pop(-1)
				elif stimtype[-1] =='F':		
					F.extend(['\nsequence S', seqID, '\n  ', seqID, 'D0', '\n  ', seqID, 'D1', '\n', 'end S', seqID, '\n'])
					Fillers[-2] = Fillers[-2],Fillers[-1]
					Fillers.pop(-1)

if stimtype[-1] == 'E':								## last check in cases where the last item in the input is an experimental one. 
	if not cond == exp * condtotal:
		print('!!Error: EyeTrack requires the same number of conditions in each experiment. Number of conditions in previous blocks: %d. Number of conditions in current block: %d (line %d)' % (condtotal, cond - (exp - 1) * condtotal, linenum))
		exit()
		
	### fix order of practice items

######## Output counts to stdout so you can check that the script counted correctly #########
print('\n%d Experiments, %d conditions in each' %(len(exp_names), condtotal))	## Experiments	
for key in exp_names:
	print('%s: line %d' %(key, exp_names[key]))

if 'Practice' in practice:					## Practice items
	print('%d practice items: line %d' %(numpractice, practice['Practice']))
else:
	print('0 practice items')
	
if 'Fillers' in fillers:					## Filler items
	print('%d fillers: line %d' %(numfillers, fillers['Fillers']))
else:
	print('0 filler items')
	
print('%d questions' %numquestions)			## Questions

output.writelines(['%','BeginHeader\nNumber_experiments: %d\nNumber_conditions: %d\nNumber_experimental_items: %d\nNumber_practice_items: %d\nNumber_fillers: %d\nExperimental_items: %r\nPractice_items: %r\nFillers: %r' %(len(exp_names), condtotal, len(Experimental_items), numpractice, numfillers, Experimental_items, Practice_items, Fillers), '\n%EndHeader\n\n'])
output.writelines(['set conditions = %d' % condtotal, '\n', 'set experiments = %d' % len(exp_names), '\n'])		# add number of conditions and experiments
output.writelines(['set background = 16777215\n', 'set foreground =  0\n\n'])							# set background and text color
output.writelines(['trial_type Reading\n', '  text_format =    \'Courier\' 12 25 20 250 nonantialiased\n', '  button =         X\n', '  output =         stream\n', '  trigger =        gaze\n', '  cursor_size =    0\n','  dc_delay =       0\n','  stimulus_delay = 0\n','  revert =         0\n','end Reading\n\n'])
output.writelines(['trial_type Question\n', '  text_format =    \'Courier\' 16 50 50 250 nonantialiased\n', '  button =         leftTrigger\n','  button =         rightTrigger\n', '  output =         nostream\n', '  trigger =        nogaze\n', '  cursor_size =    0\n','  dc_delay =       0\n','  stimulus_delay = 0\n','  revert =         0\n','end Question\n\n'])
output.writelines(['trial_type Message\n', '  text_format =    \'Courier\' 16 25 20 20 nonantialiased\n', '  button =         X\n', '  output =         nostream\n', '  trigger =        nogaze\n', '  cursor_size =    0\n','  dc_delay =       0\n','  stimulus_delay = 0\n','  revert =         0\n','end Message\n\n'])

# write opening screen:
output.writelines(['trial P1I1D0\n', '  gc_rect =          (0 0 0 0)\n', '  inline =           |In the following experiment, you will be asked to read a series of \\nsentences. Some of the sentences will be followed by a comprehension \\nquestion about the sentence. When you have finished reading each sentence, press the \'X\' key on the \\ncontrol pad to advance to the question. To answer a question, press the left \\ntrigger to indicate a \'yes\' response and the right trigger to indicate a \'no\' \\nresponse.  Before viewing each sentence, you will be asked to fixate on a box \\nthat will appear on the left side of the screen.  Upon fixation, the sentence \\nscreen will automatically advance.\\n\\n'])		# write first part of opening message

# if there are practice items, write start screen, practice items, break screen, and practice item sequence
if numpractice > 0:			
	output.writelines(['Please press \'X\' to begin a practice session.\n',  '  max_display_time = 3000000\n', '  trial_type =       Message\n', 'end P1I1D0\n']) 
	output.writelines(P)
	output.writelines(['\ntrial P1I1D%d\n' %(numpractice + 1), '  gc_rect =          (0 0 0 0)\n', '  inline =           |END PRACTICE SESSION\\n\\nIf you need a break during the experiment (if your\\neyes get tired, for example), let the\\nexperimenter know. Do you have any questions?\\nIf not, press \'X\' to start the experiment.\n',  'max_display_time = 3000000\n', '  trial_type =       Message\n', 'end P1I1D%d\n' %(numpractice + 1)])				
	output.writelines('\nsequence SP1I1\n')					
	for i in range(0,numpractice + 1):
		output.writelines('  P1I1D%d\n' %i)
	output.writelines('end SP1I1\n')

# else tell them to start the experiment
else:						
	output.writelines(['Please press \'X\' to begin the experiment.\n', '  max_display_time = 3000000\n', '  trial_type =       Message\n', 'end P1I1D0\n'])				

output.writelines(E+F)	# write experimental items and fillers
