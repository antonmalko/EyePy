import sys
import random

# IK: start by opening the file passed as cmd-line arg, then ask for subj number
try:
	file_in = open(sys.argv[1], 'rU')					# Script file, output from eyetrack_reading.py
except NameError:
	print('Error: Specify input file (open script for usage info)')

try:
	subject = int(raw_input('Subject number:'))
except NameError:
    print('Error: must be an integer')
    exit()
except ValueError:
    print('Error: must be an integer')
    exit()

# IK: use subj number to open output file
output = open('order_subj%d.script' %subject, 'wt')		# output ordering file

# IK: this reads all lines, ignoring the header
# IK:  uses some obscure assignments and evals after manipulating the line
file_in.readline()	# get past beginning of header
for i in range(2,10):	# get variables from header
	line = file_in.readline()
	vars()[line.split(':')[0]] = eval(line.split(':')[1].rstrip('\n'))

# IK: this is mysterious. If # of conditions is a factor of subj # we don't increment the counter???
counter = int(subject%Number_conditions)
if counter == 0:
	counter += Number_conditions
	
check = raw_input('Counterbalancing condition: %d. Is this right? (y/n)' %counter)
if not check.lower() == 'y':
	counter = int(input('Enter counterbalancing condition:'))

output.writelines(['%','BeginHeader\nSubject %d, counterbalancing condition %d\n' %(subject, counter), '%EndHeader\n'])	# write header
output.writelines('P1I1D0\n')

item = 1
cond = counter

itemlist = [ ]
itemnum = counter
while itemnum <= Number_experimental_items:
	itemlist.append(Experimental_items[itemnum -1])
	item += 1
	if cond < Number_conditions:
		cond += 1
	else:
		cond = 1
	itemnum = ((item - 1)*Number_conditions + cond)
itemlist.extend(Fillers)	# add filler number to list for randomization

randlist = random.sample(itemlist, len(itemlist))		# randomize order of fillers and experimental items

for member in Practice_items:							# write practice items to file first
	if type(member) == tuple:
		for part in member:
			output.writelines([part, '\n'])
	else:
		output.writelines([member, '\n'])

if len(Practice_items) > 0:
	output.writelines('P1I1D%d\n' %(len(Practice_items) + 1))

for member in randlist:
	if type(member) == tuple:
		for part in member:
			output.writelines([part, '\n'])
	else:
		output.writelines([member, '\n'])