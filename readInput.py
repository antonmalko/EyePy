# from gum import *

def read_table(filename):
    '''Takes a file name as a string, opens it. Once that's done, takes each
    non-empty row of the file and converts it into a list of strings.
    Returns a list of rows (as lists of strings).
    '''
    with open(filename) as input_file:
        nonewlines = (line.strip() for line in input_file)
        return tuple(tuple(line.split()) for line in nonewlines if line)

# tableTag creates a unique identifier for each line by concatenating the
# values in column "one" and "two" in the "input" table.
def tagged_table(table_lines, one, two):
    '''Given a table iterable for every line of said iterable creates a "tag"
    for the line by combining the elements of the line indexed by "one" and "two"
    into a tuple and pairing that up with the rest of the line.
    '''
    tags = ((line[one], line[two]) for line in table_lines)
    return zip(tags, table_lines)

# dictTable creates a dictionary from a tagged table, where the key is the tag
# and the value is a list with the rest of the columns.
def dict_from_table(table, paired=True):
    if paired:
        return dict(table)
    return dict((item[0], item[1:]) for item in table)


def region_coordinates(tagged_table):
    for tagged_line in tagged_table:
        tag, line = tagged_line
        Xes = map(int, line[3::2])
        Ys = map(int, line[4::2])
        coordinates = zip(Xes, Ys)
        starts = coordinates[:-1]
        ends = coordinates[1:]
        pairs = tuple(zip(starts, ends))
        yield (tag, pairs)


# # regStarts restructures a table ("taggedTable") assuming that it contains 4
# # identifying columns (tag, cond, item, nregions), followed by a series of
# # X Y pairs marking the beginning of each region.
# def regStarts(taggedTable):
#     regTable = []
#     for line in taggedTable:
#         idcols = line[0:4]
#         p = 'x'         #p keeps track of whether the current value is an X or a Y
#         regstarts = [] 
#         for pos in line[4:]:
#             if p=='x':
#                 regstarts.append(int(pos))
#                 p = 'y'
#             else:
#                 x = regstarts[len(regstarts)-1]
#                 regstarts[len(regstarts)-1] = [x,int(pos)]
#                 p = 'x'
#         idcols.extend(regstarts)
#         regTable.append(idcols)
#     return regTable

# # regPairs appends the end delimiters to each pair of start delimiters for a region,
# # resulting in the a series of nested lists: [[Xstart, Ystart], [Xend, Yend]].
# def regPairs(regStartsTable):
#     regTable = []
#     for line in regStartsTable:
#         idcols = line[0:4]
#         starts = line[4:len(line)-1]
#         ends = line[5:]
#         regPairs = []
#         for i in range(0,len(starts)):
#             regPairs.append([starts[i], ends[i]])
#         idcols.extend(regPairs)
#         regTable.append(idcols)
#     return regTable

# RegionTable converts a REG file into a dictionary where the key is the tag, and
# the value is the list of start/end coordinate pairs for each region.
def region_table(regFile, one, two):
    read_in = read_table(regFile)
    tagged = tagged_table(read_in, one, two)
    regioned = region_coordinates(tagged)
    return dict_from_table(regioned)


def fixation_data(tagged_table):
# don't forget to turn these into ints
    for tagged_line in tagged_table:
        tag, line = tagged_line
        Xes = map(int, line[8::4])
        Ys = map(int, line[9::4])
        fixation_starts = map(int, line[10::4])
        fixation_ends = map(int, line[11::4])
        fixations = ((x, y, end - start) 
            for x, y, start, end 
            in zip(Xes, Ys, fixation_starts, fixation_ends))
        yield (tag, tuple(fixations))

# fixGroups restructures a table from a DA1 file, assuming that it contains 9 id
# columns (tag, order, cond, item, totaltime, buttonpress, [unknown], [unknown],
# totalfixations), followed by a series of [X Y start end] groups. It outputs a
# dictionary, where the key is the tag and the value is the list with the rest of
# the columns
# def fixGroups(taggedTable):
#     fixTable = []
#     for line in taggedTable:
#         idcols=line[0:9]
#         p = 'x'
#         fixgroups = []
#         for pos in line[9:]:
#             if p=='x':
#                 x = int(pos)
#                 p = 'y'
#             elif p=='y':
#                 y = int(pos)
#                 p = 'start'
#             elif p=='start':
#                 start = int(pos)
#                 p = 'end'
#             elif p=='end':
#                 fixgroups.append([x,y,start,int(pos)])
#                 p = 'x'
#         idcols.extend(fixgroups)
#         fixTable.append(idcols)
#     return fixTable

# FixationTable converts a DA1 file into a dictionary where the key is the tag and
# the value is a list of lists of [X Y starttime endtime] for each fixation.
def fixation_table(da1File, one, two):
    tagged = tagged_table(read_table(da1File),one,two)
    fixations = fixation_data(tagged)
    return dict_from_table(fixations)

# QuestionTable converts a DA1 file into a dictionary, where the key is the tag and the value
# is a list with the following fields: order, cond, item, rt, buttonpress
def question_table(da1QFile, one, two):
    ''' Returns dict of (tag : (RT, buttonpress)) entries. '''
    tagged = tagged_table(read_table(da1QFile), one, two)
    RT_button_press = ((tag, line[3:5]) for tag, line in tagged)
    return dict_from_table(RT_button_press)


def test_output(old_fn, new_fn, *args):
    # print 'Testing old stuff'
    # old_output = old_fn(*args)
    # writable_old = [' '.join(line) for line in old_output]
    # print 'Writing old stuff'
    # # print old_output
    # write_to_txt('readTable.out', writable_old, AddNewLines=True)
    # print 'Testing new stuff'
    # new_output = new_fn(*args)
    # writable_new = [' '.join(line) for line in new_output]
    # print 'Writing new stuff'
    # write_to_txt('read_table.out', writable_new, AddNewLines=True)
    # print old_output == new_output
    pass


if __name__ == '__main__':
    test_output(readTable, read_table, 'gardenias.reg.txt')