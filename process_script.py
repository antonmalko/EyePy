# this script
# import everything from the utilities library
from util import *


def check_cond_item(entry, cond_range, item_range):
	'''Checks if the condition and item members of the "entry" tuple are within
	their respective permissible ranges.
	'''
	cond, item = entry[:2]
	return int(cond) in cond_range and int(item) in item_range


def tuples_to_str(seq, sep='\t'):
	'''Turns every member tuple of seq into a string where subparts of the tuple
	are separated from each other by "sep" and each row ends in a newline.
	'''
	return (sep.join(member) + '\n' for member in seq)


def write_out(exp_name, input_type, item_nums, cond_nums, data):
	'''Writes all the data collected to two files:
	One with all the data and one with only a subset thereof that fits in the 
	condition and item ranges specified by the user.
	'''
	all_file = '_'.join(['all', input_type, '.txt'])
	with open(all_file, 'w') as f:
		f.writelines(tuples_to_str(data))
	filtered_data = (d for d in data if check_cond_item(d, cond_nums, item_nums))
	exp_file = '_'.join([exp_name, input_type, '.txt'])
	with open(exp_file, 'w') as f:
		f.writelines(tuples_to_str(filtered_data))


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


def read_script_file(file_name):
	'''This function checks if the given file name has the .script extension
	and if it does, opens the file and reads it in as one string.
	If the file has a different extension, an exception is raised which alerts 
	the user and the program exits.
	'''
	error_message = '''Seems like you did not specify a valid .script file name.
Please either rename your file or provide a file with a .script extension.
'''
	if file_name.endswith('.script'):
		with open(file_name) as f:
			return f.read()
	else:
		raise Exception(error_message)


def generate_range(start, total):
	'''Provided with two numbers (as strings, because they are input by user),
	returns a range of numbers from "start" to "end".
	'''
	start_int = int(start)
	end_int = start_int + int(total)
	return list(range(start_int, end_int))


def main():
	'''Bringing it all together:
	- ask user to provide the variables listed below
	- create permissible item and condition number ranges
	- read in the .script file as one big string
	- extract the sentences from this string and write them to files
	- extract questions from this string and write them to files
	'''
	things_to_ask = [
	'name of your script file',
	'number of the first item',
	'total number of items',
	'number of the first condition',
	'total number of conditions',
	'name of your experiment',
	]
	user_answers = ask_user_questions(things_to_ask)

	item_range = generate_range(user_answers['number of the first item'], 
		user_answers['total number of items'])
	cond_range = generate_range(user_answers['number of the first condition'],
		user_answers['total number of conditions'])

	script_string = read_script_file(user_answers['name of your script file'])

	sent_rgx = re.compile('trial E(\d+)I(\d+)D0.*?inline =\s.*?\|(.*?)\n', re.DOTALL)
	sentences = sent_rgx.findall(script_string)
	write_out(user_answers['name of your experiment'], 'sentences', 
		item_range, cond_range, sentences)

	question_rgx = re.compile('trial E(\d+)I(\d+)D1.*?button =\s.*?(\w*?)\n', re.DOTALL)
	questions = question_rgx.findall(script_string)
	questions_with_codes = [trigger_to_code(q) for q in questions]
	write_out(user_answers['name of your experiment'], 'questions', 
		item_range, cond_range, questions_with_codes)

if __name__ == '__main__':
	main()