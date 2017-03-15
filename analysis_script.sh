#!bin/bash

# PUT THE PATH TO YOU PYTHON SCRIPTS DIRECTORY HERE 
python_scripts_folder=""

# if the directory doesn't exist, tell this and exit
if [ ! -d "$python_scripts_folder" ]; then
  echo "Python script directory is assumed to be $python_scripts_directory, but such directory doesn't exist. Change the directory in the script code. "
  exit 1
fi

#############################
## Ask user to provide parameters
#############################

# ask for experiment name
echo "This script combines the splitting of DA1 files and the generation of R table. Enter the name of your experiment. It will be used as name for the folder with processed DA1 files:"
read exp_name

# ask for postfix, to identify potential different variants of R tables
echo "Enter a postfix. It will be used to name the resulting R table (e.g. if your experiment is called \"exp\", and you enter \"main\", the R table will be called \"exp_main\")"
read postfix

echo "Enter the path to the folder with your DA1 files"
read da1_folder

#############################
## Find DEL file
#############################

# if the script is run on the first time and there is no folder like "exp_postfix",
# the .del file is expected to be in the same dir with the script
if [ ! -d "$exp_name"_"$postfix" ]; then
  echo "DEL file is expected to be in the same folder"
  # if DEL file is not found, exit
  [[ ! -e "$exp_name"_"$postfix.del" ]] && \
  	echo "DEL file not found; exiting script"&& \
 	exit 1
 	
  delfile="$exp_name"_"$postfix.del"
else
# otherwise the script expects to find del file inside "exp_postfix" folder
  echo "DEL file is expected to be in the $exp_name"_"$postfix folder"
  # if DEL file is not found, exit
  [[ ! -e "$exp_name"_"$postfix/$exp_name"_"$postfix.del" ]]&&\
  echo "DEL file not found; exiting script" &&\
  exit 1 
  
  delfile="$exp_name"_"$postfix/$exp_name"_"$postfix.del"
fi

#############################
## Clean up from previous runs
#############################

# If there are "split" folders from the previous runs, remove them. Otherwise their contents may interfere with the current analysis (e.g. if there are more subjects in there than you currently run, it normally wouldn't delete those extraneous files and they would make it to the R table)

if [ -d "$exp_name-sorted" ]; then
	echo "Found an existing split folder, will rename it to $exp_name-old. If you don't need it, remove it later"
	mv "$exp_name-sorted" "$exp_name-sorted-old"
fi

#############################
## Main: Run EyePy with expect
#############################

# expect will wait for EOF to exit
/usr/bin/expect << EOF

# run sort_da1.py
spawn python3 "$python_scripts_folder/sort_da1.py"
expect "you need to split"
send "y\r"
expect "the folder with unsorted" 
# change if your DA1 folder is not in the same dir with the script
send "$da1_folder\r"
expect "name of your study"
send "$exp_name\r"
expect "split the data by experiment"
# change if you have several experiments
send "n\r"
expect "bye"
close

# generate R table
spawn python3 "$python_scripts_folder/generate_R_table.py"
expect "REG (or DEL) filename"
send "$delfile\r"
expect "Question key filename"
send "$exp_name\_questions.txt\r"
expect "Sentence data folder"
send "$exp_name-sorted/$exp_name-s\r"
expect "Question data folder"
send "$exp_name-sorted/$exp_name-q\r"
expect "Output filename"
send "$exp_name\_$postfix.txt\r"
expect "change current settings"
send "n\r"
expect sleep 3
expect "Writing statistics"
expect sleep 3
close

EOF

#############################
## Arrange created files
#############################

# move the R table into Data folder
# assuming the current folder is, with . being root project folder:
# ./Analysis/scripts/Making R table
mkdir ../../../Data/csv
cp -f "$exp_name"_"$postfix.txt" ../../../Data/csv/"$exp_name"_"$postfix.txt"


# move all the files related to this analysis variant into separate folder in the 
# script directory
mkdir ./"$exp_name"_"$postfix"/
[[ -e "$exp_name"_"$postfix.reg" ]] && mv "$exp_name"_"$postfix.reg" ./"$exp_name"_"$postfix"/
mv "excluded_fixation_counts.csv" ./"$exp_name"_"$postfix"/
# if .del file is in the script directory, move it to the new folder
[[ -e "$exp_name"_"$postfix.del" ]] && \
	mv "$exp_name"_"$postfix.del" ./"$exp_name"_"$postfix"/
mv "$exp_name"_"$postfix.txt" ./"$exp_name"_"$postfix"/

echo "Done!"
