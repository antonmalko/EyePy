# edited by: Shevaun Lewis
# last updated: 3/5/2013
# Fixed appalling problem in regionCheck

# A function is added for computing first-pass skip -- Wing-Yee Chow (3/6/2013)


# Idea from Sol: instead of NAs use 0s initially, then replace them with NAs

# Region check ####
#
# regionCheck takes a region [[Xstart, Ystart],[Xend, Yend]] and a pair of coordinates for a fixation.
# It returns 'within' if the fixation is in the region, 'before' if it's in a preceding region, and
# 'after' if it's in a later region.
def regionCheck(reg, fix):

    ## unpack region delimiters from reg
    xStart = reg[0][0]
    yStart = reg[0][1]
    xEnd = reg[1][0]
    yEnd = reg[1][1]

    ## if the x=coordinate of fix is -1, then the fixation was
    if fix[0] == -1:
        # not properly edited/rejected. ignore for calculations, print
        # feedback.
        return 'ignore'
        print "fixation out of bounds: " + fix
    ## if the region starts and ends on the same line
    elif yStart == yEnd:
        ## UPDATED: you have to check which line the FIXATION is on!!!
        if fix[1] == yStart:
            if fix[0] >= xStart and fix[0] < xEnd:
                return 'within'
            elif fix[0] < xStart:
                return 'before'
            elif fix[0] >= xEnd:
                return 'after'
        elif fix[1] < yStart:
            return 'before'
        elif fix[1] > yStart:
            return 'after'
    ## if the region starts and ends on different lines
    else:
        ## if the fixation is on the first line
        if fix[1] == yStart:
            if fix[0] >= xStart:
                return 'within'
            else:
                return 'before'
        ## if the fixation is on the second line
        elif fix[1] == yEnd:
            if fix[0] < xEnd:
                return 'within'
            else:
                return 'after'


# First-pass Skip calculation####
def first_skip(region, fixations, lowCutoff, highCutoff):
    skip = 1

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        #only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fix is within region
            if regionCheck(region, f) == 'within':
                skip = 0
                ## break the search as soon as you find the first fixation
                break
            ## if fix is after the region
            elif regionCheck(region, f) == 'after':
                ## break the search since the region has been skipped
                break
    return skip  # return the skip boolean


# First fixation calculation####
#
# returns the duration of the first fixation in the region
def first_fixation(region, fixations, lowCutoff, highCutoff):
    ## initialize fixTime as 'NA' (no fixation)
    fixTime = 'NA'

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        #only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fix is within region
            if regionCheck(region, f) == 'within':
                ## store duration as first fixation time
                fixTime = duration
                ## break the search as soon as you find the first fixation
                break
            ## if fix is after the region
            elif regionCheck(region, f) == 'after':
                ## break the search since the region has been skipped
                break
    ## return the first fixation time (which is 'NA' if none other is found)
    return fixTime


# First pass calculation####
# returns the sum of the fixations in the region before the region is
# exited in either direction
def first_pass(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0  # initialize sum to 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fix is within region
            if regionCheck(region, f) == 'within':
                ## add duration to sum of fixations
                fixTimeSum = fixTimeSum + duration
            ## if fix is after the region
            elif regionCheck(region, f) == 'after':
                ## break, because the first pass is over.
                break
            ##if the region has already been entered at least once,
            elif fixTimeSum > 0 and regionCheck(region, f) == 'before':
                # and fix is before the region, then break, because the first
                # pass is over
                break

    return fixTimeSum


# Regression path calculation####
#
# sums all the fixations in all the regions up to and including the
# region of interest, before that region is exited to the right

def regression_path(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is after the ROI, break
            if regionCheck(region, f) == 'after':
                break
            ## if the fix is w/in the ROI or the ROI has already been visited
            elif regionCheck(region, f) == 'within' or fixTimeSum > 0:
                ## add the duration to the sum
                fixTimeSum = fixTimeSum + duration

    return fixTimeSum


# Right-bounded Reading Time calculation####
#
# sums all the fixations in a region before the region is exited to the right
def right_bound(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is after the ROI, break
            if regionCheck(region, f) == 'after':
                break
            ## if the fix is w/in the ROI
            elif regionCheck(region, f) == 'within':
                ## add the duration to the sum
                fixTimeSum = fixTimeSum + duration

    return fixTimeSum


# Re-reading time calculation####
def reread_time(region, fixations, lowCutoff, highCutoff):
    first = first_pass(region, fixations, lowCutoff, highCutoff)
    return total_time(region, fixations, lowCutoff, highCutoff) - first


# Total reading time calculation####
def total_time(region, fixations, lowCutoff, highCutoff):

    fixTimeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fix is w/in the ROI
            if regionCheck(region, f) == 'within':
                ## add the duration to the sum
                fixTimeSum = fixTimeSum + duration

    return fixTimeSum

# % Regression calculation####
def percent_regression(region, fixations, lowCutoff, highCutoff):
    visitreg = 0
    reg = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is after the ROI, break
            if regionCheck(region, f) == 'after':
                break
            ## if the fixation is in the ROI,
            elif regionCheck(region, f) == 'within':
                ## mark the ROI as having been visited at least once
                visitreg = 1
            ## if the ROI has been visited at least once and the
            elif visitreg == 1 and regionCheck(region, f) == 'before':
                ## fix is in a region before the ROI, count it
                reg = 1
                ## as a regression and break
                break

    return reg


def single_fixation_duration(region, fixations, lowCutoff, highCutoff):
    '''Given a region, fixation list, and low/high cutoff values, returns
    the duration of the fixation on the region if it was the only one.
    Otherwise returns zero.
    '''
    first_fix = first_fixation(region, fixations, lowCutoff, highCutoff)
    total_fixation = total_time(region, fixations, lowCutoff, highCutoff)
    if first_fix == total_fixation:
        return total_fixation
    else:
        return 0


def rereading_prob(region, fixations, lowCutoff, highCutoff):
    '''given a region and a fixations list calculates whether the region was
    reread or not.
    Returns either 1 or 0, having converted boolean test to an integer.
    '''
    return int(reread_time(region, fixations, lowCutoff, highCutoff) > 0)
