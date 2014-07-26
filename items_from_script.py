'''This script analyzes the .script file used by EyeLink and from it extracts
the question items as well as the sentence items.
The question items are used to create an answer key to check if subjects respond
correctly to a given question.
The sentence items are used to (manually) create a .del (delimited) file, which 
in turn is read in by generate_R_table.py and turned into a .reg (region) file.
'''
# import everything from the utilities library
from util import *

###########################################################
## Main
###########################################################

def main():
	'''Bringing it all together:
	- ask user to provide the variables listed below
	- create permissible item and condition number ranges
	- read in the .script file as one big string
	- extract the sentences from this string and write them to files
	- extract questions from this string and write them to files
	'''
	things_to_ask = [
	'name of your experiment',
	'name of your script file',
	'number of the first item',
	'total number of items',
	'number of the first condition',
	'total number of conditions',
	]
	# use function from util module
	user_answers = ask_user_questions(things_to_ask)

	item_range = generate_range(user_answers['number of the first item'], 
								user_answers['total number of items'])
	cond_range = generate_range(user_answers['number of the first condition'],
								user_answers['total number of conditions'])

	script_string = read_script_file(user_answers['name of your script file'])

	rgx_template = 'trial E(\d+)I(\d+)D{0}.*?{1} =\s*{2}'
	# rgx_template = 'trial E(\d+)I(\d+)D{0}.*?{1} =\s*{2}'

	sent_rgx = re.compile(rgx_template.format(0, 'inline', '\|(.*?)\n'), re.DOTALL)
	sentences = sent_rgx.findall(script_string)
	write_out(user_answers['name of your experiment'], 
		'sentences', 
		item_range, 
		cond_range, 
		sentences)

	question_rgx = re.compile(rgx_template.format(1, 'button', '(\w*)'), re.DOTALL)
	questions = question_rgx.findall(script_string)
	questions_with_codes = list(map(trigger_to_code, questions))
	write_out(user_answers['name of your experiment'], 
		'questions', 
		item_range, 
		cond_range, 
		questions_with_codes)


def generate_range(start, total):
	'''Provided with two numbers (as strings, because they are input by user),
	returns a range of numbers from "start" to "end".
	'''
	start_int = int(start)
	end_int = start_int + int(total)
	return list(range(start_int, end_int))


_READ_ERROR = ('Seems like you did not specify a valid .script file name.\n'
	'Please either rename your file or provide a file with a .script extension.')


def read_script_file(file_name):
	'''This function checks if the given file name has the .script extension
	and if it does, opens the file and reads it in as one string.
	If the file has a different extension, an exception is raised which alerts 
	the user and the program exits.
	'''
	if file_name.endswith('.script'):
		with open(file_name) as f:
			return f.read()
	else:
		raise Exception(_READ_ERROR)


def write_out(exp_name, input_type, item_nums, cond_nums, data):
	'''Writes all the data collected to two files:
	One with all the data and one with only a subset thereof that fits in the 
	condition and item ranges specified by the user.
	'''
	all_file = 'all_' + input_type + '.txt'
	write_to_table(all_file, data, delimiter='\t')
	print('Wrote {0} {1} to *{2}*'.format('all', input_type, all_file))

	filtered_data = (d for d in data if check_cond_item(d, cond_nums, item_nums))
	exp_file = exp_name + '_' + input_type + '.txt'
	write_to_table(exp_file, filtered_data, delimiter='\t')
	print('Wrote {0} {1} to *{2}*'.format(exp_name, input_type, exp_file))
	

def check_cond_item(entry, cond_range, item_range):
	'''Checks if the condition and item members of the "entry" tuple are within
	their respective permissible ranges.
	'''
	cond, item = entry[:2]
	return int(cond) in cond_range and int(item) in item_range


def trigger_to_code(question_item):
	'''Given a question item, looks up the the number code for the left and right
	triggers.
	Then tacks on this code to the question item and returns it.
	'''
	codes = {
	'leftTrigger' : '6',
	'rightTrigger' : '7',
	}
	trigger = question_item[2].strip()
	return question_item + (codes[trigger],)


if __name__ == '__main__':
	main()