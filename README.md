EyePy
================

Collection of scripts for processing Eye-tracking data.

Changelog
================
Anton Malko:
- *mergewords.py* adds words into R table. It is run automatically from *generate_R_table.py*. However, it can be also run on its own; then it will ask for three things: .del filename, R table filename, output table name.

- *analysis_script.sh* automates the analysis process. It runs *sort_da1.py* and *generate_R_table.py* and asks for only two things: the name of the experiment and a postfix. The name of the experiment will be used as the name for the folder with split DA1 files. These files can be used later with different variants of preprocessing (different regions mark-up, different cut-off values etc.); postfix is used to identify such variants. For each variant, the script will create a folder with a name like "experiment_postfix", and put all the related files there (.del file, .reg file, "excluded-fixations.csv" file, R table).

The script will look for the .del file named like "experiment-postfix". It will do so in the script directory, if the script is run in the first time and "experiment-postfix" folder doesn't exist; otherwise, it will look in that folder.

The script relies on 'expect' program. In order to run on Unix:
	1. Open the script in any text editor, and write path to the folder with EyePy scripts.
	2. By default, the script expects that the folder with DA1 is in the same directory with the script itself. You can:
		- Copy the DA1 folder to the script folder
		- Create a symlink to the DA1 folder. Run the following command in the terminal, replacing the paths: *ln -s /path/to/original/DA1folder /path/to/script/folder*
		- Change line 29 in the script, replacing "DA1" with the path to DA1 folder
	
If you want to run this script on Windows, install *cygwin* package (https://www.cygwin.com/), which adds unix command line instruments to Windows.

The default answers the scripts gives to EyePy scripts are (underscores are replaced with  dashes):

sort-da1.py
	1. Do you need to split the DA1s into -s, -q, and -reject files? - Yes
	2. Please enter the folder with unsorted DA1 files below - DA1
	3.  Please enter the name of your study below - exp_name 
	4.  Do you want to split the data by experiment? - No

generate-R-table
	1.  Please enter the REG (or DEL) filename below: expname-postfix.del OR expname-postfix/expname_postfix.del (if the folder already exists)
	2.  Please enter the Question key filename below: expname-questions.txt
	3.  Please enter the Sentence data folder below: expname-sorted/expname-s
	4.  Please enter the Question data folder below: expname-sorted/expname-q
	5.  Please enter the Output filename below: expname-postfix.txt
	6.  The current cutoff settings are as follows.
		low: 40 ms
		high: 1000 ms
		Would you like to change them? - No


