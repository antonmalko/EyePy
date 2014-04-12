# edited by: Shevaun Lewis
# last updated: 3/5/2013
# fixationed appalling problem in regionCheck

# A function is added for computing first-pass skip -- Wing-Yee Chow (3/6/2013)


def region_check(region, fixation):
    '''Takes a region in the form [[Xstart, Ystart],[Xend, Yend]] and a pair of 
    coordinates for a fixationation. It then checks where the coordinates are with
    respect to the region.
    Depending on where that is returns 'within', 'before' or 'after'.
    '''
    # unpack region delimiters from region
    xStart = region[0][0]
    yStart = region[0][1]
    xEnd = region[1][0]
    yEnd = region[1][1]

    # if the x=coordinate of fixation is -1, the fixationation was
    # not properly edited/rejected. ignore for calculations, print feedback.
    if fixation[0] == -1:
        return 'ignore'
        print "fixationation out of bounds: " + fixation
    # if the region starts and ends on the same line
    elif yStart == yEnd:
        # UPDATED: you have to check which line the fixationATION is on!!!
        if fixation[1] == yStart:
            if fixation[0] >= xStart and fixation[0] < xEnd:
                return 'within'
            elif fixation[0] < xStart:
                return 'before'
            elif fixation[0] >= xEnd:
                return 'after'
        elif fixation[1] < yStart:
            return 'before'
        elif fixation[1] > yStart:
            return 'after'
    # if the region starts and ends on different lines
    else:
        # if the fixationation is on the first line
        if fixation[1] == yStart:
            if fixation[0] >= xStart:
                return 'within'
            else:
                return 'before'
        # if the fixationation is on the second line
        elif fixation[1] == yEnd:
            if fixation[0] < xEnd:
                return 'within'
            else:
                return 'after'


# First-pass Skip calculation####
def first_skip(region, fixationations, lowCutoff, highCutoff):
    skip = 1

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        #only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fixation is within region
            if region_check(region, f) == 'within':
                skip = 0
                ## break the search as soon as you find the first fixationation
                break
            ## if fixation is after the region
            elif region_check(region, f) == 'after':
                ## break the search since the region has been skipped
                break
    return skip  # return the skip boolean


# First fixationation calculation####
#
# returns the duration of the first fixationation in the region
def first_fixationation(region, fixationations, lowCutoff, highCutoff):
    ## initialize fixationTime as 'NA' (no fixationation)
    fixationTime = 'NA'

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        #only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fixation is within region
            if region_check(region, f) == 'within':
                ## store duration as first fixationation time
                fixationTime = duration
                ## break the search as soon as you find the first fixationation
                break
            ## if fixation is after the region
            elif region_check(region, f) == 'after':
                ## break the search since the region has been skipped
                break
    ## return the first fixationation time (which is 'NA' if none other is found)
    return fixationTime


# First pass calculation####
# returns the sum of the fixationations in the region before the region is
# exited in either direction
def first_pass(region, fixationations, lowCutoff, highCutoff):
    fixationTimeSum = 0  # initialize sum to 0

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fixation is within region
            if region_check(region, f) == 'within':
                ## add duration to sum of fixationations
                fixationTimeSum = fixationTimeSum + duration
            ## if fixation is after the region
            elif region_check(region, f) == 'after':
                ## break, because the first pass is over.
                break
            ##if the region has already been entered at least once,
            elif fixationTimeSum > 0 and region_check(region, f) == 'before':
                # and fixation is before the region, then break, because the first
                # pass is over
                break

    return fixationTimeSum


# Regression path calculation####
#
# sums all the fixationations in all the regions up to and including the
# region of interest, before that region is exited to the right

def regression_path(region, fixationations, lowCutoff, highCutoff):
    fixationTimeSum = 0

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixationation is after the ROI, break
            if region_check(region, f) == 'after':
                break
            ## if the fixation is w/in the ROI or the ROI has already been visited
            elif region_check(region, f) == 'within' or fixationTimeSum > 0:
                ## add the duration to the sum
                fixationTimeSum = fixationTimeSum + duration

    return fixationTimeSum


# Right-bounded Reading Time calculation####
#
# sums all the fixationations in a region before the region is exited to the right
def right_bound(region, fixationations, lowCutoff, highCutoff):
    fixationTimeSum = 0

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixationation is after the ROI, break
            if region_check(region, f) == 'after':
                break
            ## if the fixation is w/in the ROI
            elif region_check(region, f) == 'within':
                ## add the duration to the sum
                fixationTimeSum = fixationTimeSum + duration

    return fixationTimeSum


# Re-reading time calculation####
def reread_time(region, fixationations, lowCutoff, highCutoff):
    first = first_pass(region, fixationations, lowCutoff, highCutoff)
    return total_time(region, fixationations, lowCutoff, highCutoff) - first


# Total reading time calculation####
def total_time(region, fixationations, lowCutoff, highCutoff):

    fixationTimeSum = 0

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is w/in the ROI
            if region_check(region, f) == 'within':
                ## add the duration to the sum
                fixationTimeSum = fixationTimeSum + duration

    return fixationTimeSum

# % Regression calculation####
def percent_regression(region, fixationations, lowCutoff, highCutoff):
    visitreg = 0
    reg = 0

    ## loop through each fixationation
    for f in fixationations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixationation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixationation is after the ROI, break
            if region_check(region, f) == 'after':
                break
            ## if the fixationation is in the ROI,
            elif region_check(region, f) == 'within':
                ## mark the ROI as having been visited at least once
                visitreg = 1
            ## if the ROI has been visited at least once and the
            elif visitreg == 1 and region_check(region, f) == 'before':
                ## fixation is in a region before the ROI, count it
                reg = 1
                ## as a regression and break
                break

    return reg


def single_fixationation_duration(region, fixationations, lowCutoff, highCutoff):
    '''Given a region, fixationation list, and low/high cutoff values, returns
    the duration of the fixationation on the region if it was the only one.
    Otherwise returns zero.
    '''
    first_fixation = first_fixationation(region, fixationations, lowCutoff, highCutoff)
    total_fixationation = total_time(region, fixationations, lowCutoff, highCutoff)
    if first_fixation == total_fixationation:
        return total_fixationation
    else:
        return 0


def rereading_prob(region, fixationations, lowCutoff, highCutoff):
    '''given a region and a fixationations list calculates whether the region was
    reread or not.
    Returns either 1 or 0, having converted boolean test to an integer.
    '''
    return int(reread_time(region, fixationations, lowCutoff, highCutoff) > 0)
