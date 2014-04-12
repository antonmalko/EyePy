##by: Shevaun Lewis
##date updated: 3/11/11
##updated by: Shayne Sloggett

import os
import splitDA1

## Get info from user.

print("Do you need to split the DA1s into -s, -q, and -reject files?")

try:
    DOSPLIT = str(input("y or n:"))
except NameError:
    print('Error: must input y or n')
    exit()
except ValueError:
    print('Error: must input y or n')
    exit()

if DOSPLIT=="y":
    print("DA1 files for both sentences and questions should be stored in a single folder.")
    print("Filenames should be in the format ###-study.da1, where:")
    print("	a. ### is a *3-digit* code for the subject number")
    print("	b. 'study' is the name of the study")
    print("These files should be stored inside a single folder. Enter that folder below.")

else:
    print("DA1 files should be stored in three folders, one each for -s, -q, and -reject files.")
    print("Filenames should be in the format ###-study-s.da1, ###-study-q.da1, and ###-study-r.da1, where:")
    print("	a. ### is a *3-digit* code for the subject number")
    print("	b. 'study' is the name of the study")
    print("	c. -s, -q and -r represent whether the file is for sentence, question or reject trials")
    print("These three folders should be stored inside a single folder. Enter that directory address for that folder below.")

try:
    DATAFOLDER = str(input("Complete directory address with DA1 files:"))
except NameError:
    print('Error: must be a string')
    exit()
except ValueError:
    print('Error: must be a string')
    exit()

if DOSPLIT=="y":
    try:
        STUDYNAME = str(input("Name of study:"))
    except NameError:
        print('Error: must be a string')
        exit()
    except ValueError:
        print('Error: must be a string')
        exit()

    newfolders = splitDA1.DA1splitTypeFolder(DATAFOLDER, STUDYNAME)
    print("Done. The processed DA1 files are now located in the new folder "+STUDYNAME+"-sorted, located inside your original data folder.")
else:
    foldernames = os.listdir(DATAFOLDER)
    newfolders = [DATAFOLDER+"/"+foldernames[2], DATAFOLDER+"/"+foldernames[0], DATAFOLDER+"/"+foldernames[1]]

print("Do you need to split the DA1 files into separate experiments?")

if DOSPLIT=="y":
	DATAFOLDER = DATAFOLDER+"/"+STUDYNAME+"-sorted"

try:
    CONTINUE = str(input("y or n:"))
except NameError:
    print('Error: must input y or n')
    exit()
except ValueError:
    print('Error: must input y or n')
    exit()

while CONTINUE=="y":
    try:
        EXPNAME = str(input("Enter the experiment name:"))
    except NameError:
        print('Error: must be a string')
        exit()
    except ValueError:
        print('Error: must be a string')
        exit()

    try:
        FIRSTCOND = int(input("Enter the number of the first condition for this experiment (from EyeTrack):"))
    except NameError:
        print('Error: must be an integer')
        exit()
    except ValueError:
        print('Error: must be an integer')
        exit()

    try:
        NUMCONDS = int(input("Enter the number of conditions for this experiment:"))
    except NameError:
        print('Error: must be an integer')
        exit()
    except ValueError:
        print('Error: must be an integer')
        exit()

    expFolder = DATAFOLDER+"/"+EXPNAME+"-sorted"
    os.mkdir(expFolder)
    expFolderS = expFolder+"/"+EXPNAME+"-s"
    os.mkdir(expFolderS)
    expFolderQ = expFolder+"/"+EXPNAME+"-q"
    os.mkdir(expFolderQ)
    expFolderR = expFolder+"/"+EXPNAME+"-reject"
    os.mkdir(expFolderR)

    splitDA1.DA1splitExpFolder(newfolders[0], expFolderS, FIRSTCOND, NUMCONDS, EXPNAME)
    splitDA1.DA1splitExpFolder(newfolders[1], expFolderQ, FIRSTCOND, NUMCONDS, EXPNAME)
    splitDA1.DA1splitExpFolder(newfolders[2], expFolderR, FIRSTCOND, NUMCONDS, EXPNAME)
    
    print("Done. The processed DA1 files have been stored in "+expFolder+", located within your original data folder.")
    print("Do you want to get another experiment?")
    try:
        CONTINUE = str(input("y or n:"))
    except NameError:
        print('Error: must input y or n')
        exit()
    except ValueError:
        print('Error: must input y or n')
        exit()
else:
    print("Ok, bye!")
