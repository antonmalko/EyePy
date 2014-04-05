def readTable(filename):

    myFile = open(filename, "r")
    temp = 1 # unused variable, IK
    dataTable = []

    for line in myFile:
        if line != "":
            nonewline = line.split('\n')[0] # somewhat weird way of trimming a line
            dataTable.append(nonewline.split())

    myFile.close()
    return dataTable

# tableTag creates a unique identifier for each line by concatenating the
# values in column "one" and "two" in the "input" table.
def tableTag(table,one,two):
    for line in table:
        tag = line[one]+line[two]
        line.insert(0,tag)
    return table

# dictTable creates a dictionary from a tagged table, where the key is the tag
# and the value is a list with the rest of the columns.
def dictTable(table):
    dtable = {}
    for line in table:
        dtable[line[0]] = line[1:]
    return dtable

# regStarts restructures a table ("taggedTable") assuming that it contains 4
# identifying columns (tag, cond, item, nregions), followed by a series of
# X Y pairs marking the beginning of each region.
def regStarts(taggedTable):
    regTable = []
    for line in taggedTable:
        idcols = line[0:4]
        p = 'x'         #p keeps track of whether the current value is an X or a Y
        regstarts = []
        for pos in line[4:]:
            if p=='x':
                regstarts.append(int(pos))
                p = 'y'
            else:
                x = regstarts[len(regstarts)-1]
                regstarts[len(regstarts)-1] = [x,int(pos)]
                p = 'x'
        idcols.extend(regstarts)
        regTable.append(idcols)
    return regTable

# regPairs appends the end delimiters to each pair of start delimiters for a region,
# resulting in the a series of nested lists: [[Xstart, Ystart], [Xend, Yend]].
def regPairs(regStartsTable):
    regTable = []
    for line in regStartsTable:
        idcols = line[0:4]
        starts = line[4:len(line)-1]
        ends = line[5:]
        regPairs = []
        for i in range(0,len(starts)):
            regPairs.append([starts[i], ends[i]])
        idcols.extend(regPairs)
        regTable.append(idcols)
    return regTable

# RegionTable converts a REG file into a dictionary where the key is the tag, and
# the value is the list of start/end coordinate pairs for each region.
def RegionTable(regFile, one, two):
    return dictTable(regPairs(regStarts(tableTag(readTable(regFile),one,two))))

# fixGroups restructures a table from a DA1 file, assuming that it contains 9 id
# columns (tag, order, cond, item, totaltime, buttonpress, [unknown], [unknown],
# totalfixations), followed by a series of [X Y start end] groups. It outputs a
# dictionary, where the key is the tag and the value is the list with the rest of
# the columns
def fixGroups(taggedTable):
    fixTable = []
    for line in taggedTable:
        idcols=line[0:9]
        p = 'x'
        fixgroups = []
        for pos in line[9:]:
            if p=='x':
                x = int(pos)
                p = 'y'
            elif p=='y':
                y = int(pos)
                p = 'start'
            elif p=='start':
                start = int(pos)
                p = 'end'
            elif p=='end':
                fixgroups.append([x,y,start,int(pos)])
                p = 'x'
        idcols.extend(fixgroups)
        fixTable.append(idcols)
    return fixTable

# FixationTable converts a DA1 file into a dictionary where the key is the tag and
# the value is a list of lists of [X Y starttime endtime] for each fixation.
def FixationTable(da1File, one, two):
    return dictTable(fixGroups(tableTag(readTable(da1File),one,two)))

# QuestionTable converts a DA1 file into a dictionary, where the key is the tag and the value
# is a list with the following fields: order, cond, item, rt, buttonpress
def QuestionTable(da1QFile, one, two):
    qtable = tableTag(readTable(da1QFile), one, two)
    qDict = {}
    for row in qtable:
        qDict[row[0]] = row[1:6]
    return qDict
