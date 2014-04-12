# edited by: Shevaun Lewis
# last updated: 3/5/2013
# fixationed appalling problem in regionCheck

# A function is added for computing first-pass skip -- Wing-Yee Chow (3/6/2013)


def region_check(region, fixation):
    '''Takes a region in the form [[Xstart, Ystart],[Xend, Yend]] and a pair of 
    coordinates for a fixation. It then checks where the coordinates are with
    respect to the region.
    Depending on where that is returns 'within', 'before' or 'after'.
    '''
    # unpack region delimiters from region
    xStart = region[0][0]
    yStart = region[0][1]
    xEnd = region[1][0]
    yEnd = region[1][1]

    # if the x=coordinate of fixation is -1, the fixation was
    # not properly edited/rejected. ignore for calculations, print feedback.
    if fixation[0] == -1:
        return 'ignore'
        print "fixation out of bounds: " + fixation
    # if the region starts and ends on the same line
    elif yStart == yEnd:
        # UPDATED: you have to check which line the fixation is on!!!
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
        # if the fixation is on the first line
        if fixation[1] == yStart:
            if fixation[0] >= xStart:
                return 'within'
            else:
                return 'before'
        # if the fixation is on the second line
        elif fixation[1] == yEnd:
            if fixation[0] < xEnd:
                return 'within'
            else:
                return 'after'


def first_skip(region, fixations, lowCutoff, highCutoff):
    '''Given a region, a list of fixations and cutoff values returns either 
    1 or 0 for whether the region was skipped or not.
    '''
    was_skipped = 1

    # loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
            # if fixation is within region
            if fixation_position == 'within':
                was_skipped = 0
                # break the search as soon as you find the first fixation
                break
            # if fixation is after the region
            elif fixation_position == 'after':
                # break the search since the region has been
                break
    return was_skipped  # return the was_skipped boolean


def first_fixation(region, fixations, lowCutoff, highCutoff):
    '''Given a region, a list of fixations and cutoff values, returns 
    the duration of the first fixation.
    '''
    first_fixation_time = 0

    # loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
            # if fixation is within region
            if region_check(region, f) == 'within':
                ## store duration as first fixation time
                first_fixation_time = duration
                # break the search as soon as you find the first fixation
                break
            # if fixation is after the region
            elif region_check(region, f) == 'after':
                # break the search once the region has been passed
                break
    return first_fixation_time


# First pass calculation####
# returns the sum of the fixations in the region before the region is
# exited in either direction
def first_pass(region, fixations, lowCutoff, highCutoff):
    first_fixation_timeSum = 0  # initialize sum to 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if fixation is within region
            if region_check(region, f) == 'within':
                ## add duration to sum of fixations
                first_fixation_timeSum = first_fixation_timeSum + duration
            ## if fixation is after the region
            elif region_check(region, f) == 'after':
                ## break, because the first pass is over.
                break
            ##if the region has already been entered at least once,
            elif first_fixation_timeSum > 0 and region_check(region, f) == 'before':
                # and fixation is before the region, then break, because the first
                # pass is over
                break

    return first_fixation_timeSum


# Regression path calculation####
#
# sums all the fixations in all the regions up to and including the
# region of interest, before that region is exited to the right

def regression_path(region, fixations, lowCutoff, highCutoff):
    first_fixation_timeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is after the ROI, break
            if region_check(region, f) == 'after':
                break
            ## if the fixation is w/in the ROI or the ROI has already been visited
            elif region_check(region, f) == 'within' or first_fixation_timeSum > 0:
                ## add the duration to the sum
                first_fixation_timeSum = first_fixation_timeSum + duration

    return first_fixation_timeSum


# Right-bounded Reading Time calculation####
#
# sums all the fixations in a region before the region is exited to the right
def right_bound(region, fixations, lowCutoff, highCutoff):
    first_fixation_timeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is after the ROI, break
            if region_check(region, f) == 'after':
                break
            ## if the fixation is w/in the ROI
            elif region_check(region, f) == 'within':
                ## add the duration to the sum
                first_fixation_timeSum = first_fixation_timeSum + duration

    return first_fixation_timeSum


# Re-reading time calculation####
def reread_time(region, fixations, lowCutoff, highCutoff):
    first = first_pass(region, fixations, lowCutoff, highCutoff)
    return total_time(region, fixations, lowCutoff, highCutoff) - first


# Total reading time calculation####
def total_time(region, fixations, lowCutoff, highCutoff):

    first_fixation_timeSum = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]
            ## calculate duration (endtime - starttime)
        ## only use fixation if duration is within cutoffs
        if duration > lowCutoff and duration < highCutoff:
            ## if the fixation is w/in the ROI
            if region_check(region, f) == 'within':
                ## add the duration to the sum
                first_fixation_timeSum = first_fixation_timeSum + duration

    return first_fixation_timeSum

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
            if region_check(region, f) == 'after':
                break
            ## if the fixation is in the ROI,
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


def single_fixation_duration(region, fixations, lowCutoff, highCutoff):
    '''Given a region, fixation list, and low/high cutoff values, returns
    the duration of the fixation on the region if it was the only one.
    Otherwise returns zero.
    '''
    first_fixation = first_fixationn(region, fixations, lowCutoff, highCutoff)
    total_fixation = total_time(region, fixations, lowCutoff, highCutoff)
    if first_fixation == total_fixation:
        return total_fixation
    else:
        return 0


def rereading_prob(region, fixations, lowCutoff, highCutoff):
    '''given a region and a fixations list calculates whether the region was
    reread or not.
    Returns either 1 or 0, having converted boolean test to an integer.
    '''
    return int(reread_time(region, fixations, lowCutoff, highCutoff) > 0)
