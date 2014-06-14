'''Module to house functions that calculate eye-tracking measures.
'''
# CHANGELOG
# edited by: Shevaun Lewis
# last updated: 3/5/2013
# fixationed appalling problem in regionCheck
# A function is added for computing first-pass skip -- Wing-Yee Chow (3/6/2013)
# 5/2014 - 6/2014 by Ilia Kurenkov
# rewrote the measure functions and moved cutoff filtering to another script
# added two new measures: single fixation and probability of rereading


def region_check(region, fixationX, fixationY):
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
    if fixationX == -1:
        return 'ignore'
        print("fixation out of bounds: " + fixation)
    # if the region starts and ends on the same line
    elif yStart == yEnd:
        # UPDATED: you have to check which line the fixation is on!!!
        if fixationY == yStart:
            if fixationX >= xStart and fixationX < xEnd:
                return 'within'
            elif fixationX < xStart:
                return 'before'
            elif fixationX >= xEnd:
                return 'after'
        elif fixationY < yStart:
            return 'before'
        elif fixationY > yStart:
            return 'after'
    # if the region starts and ends on different lines
    else:
        # if the fixation is on the first line
        if fixationY == yStart:
            if fixationX >= xStart:
                return 'within'
            else:
                return 'before'
        # if the fixation is on the second line
        elif fixationY == yEnd:
            if fixationX < xEnd:
                return 'within'
            else:
                return 'after'


def first_skip(region, fixations):
    '''Given a region, a list of fixations and cutoff values returns either 
    1 or 0 for whether the region was skipped or not.
    '''
    was_skipped = 1

    # loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
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


def first_fixation(region, fixations):
    '''Given a region, a list of fixations and cutoff values, returns 
    the duration of the first fixation.
    '''
    first_fixation_time = 0

    # loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        # if fixation is within region
        if fixation_position == 'within':
            ## store duration as first fixation time
            first_fixation_time = duration
            # break the search as soon as you find the first fixation
            break
        # if fixation is after the region
        elif fixation_position == 'after':
            # break the search once the region has been passed
            break
    return first_fixation_time


def first_pass(region, fixations):
    '''Given a region and a list of fixations as well as cutoff values,
    returns the sum of all the fixations in the region before it is exited in 
    either direction.
    '''
    first_pass_sum = 0  # initialize sum to 0

    # loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        # if fixation is within region
        if fixation_position == 'within':
            ## add duration to sum of fixations
            first_pass_sum = first_pass_sum + duration
        # if fixation is after the region
        elif fixation_position == 'after':
            # break, because the first pass is over.
            break
        #if the region has already been entered at least once and fixation 
        # is before the region, break, because the first pass is over
        elif first_pass_sum > 0 and fixation_position == 'before':
            break

    return first_pass_sum


def regression_path(region, fixations):
    '''Sums up fixation durations for the current region N and all regions 
    to the left of N starting with when region N was entered and up to the point
    when it was exited to the right.
    '''
    regression_sum = 0.0

    # loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        # if the region was exited to the right, break
        if fixation_position == 'after':
            break
        # if the fixation is w/in the ROI or the ROI has already been visited
        elif fixation_position == 'within' or regression_sum > 0:
            # add the duration to the sum
            regression_sum = regression_sum + duration

    return regression_sum


def prob_regression(region, fixations):
    '''Returns either 1 or 0 depending on whether a regression happens 
    from current region.
    '''
    was_visited = False
    regression_prob = 0
    
    # set this value to "NA" if there was no first fixation on the region
    if first_skip(region, fixations):
        return 'NA'

    ## loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        # break if region exited to the right
        if fixation_position == 'after':
            break
        # if the fixation is in ROI, mark ROI as having been visited
        elif fixation_position == 'within':
            was_visited = True
        # if ROI was visited and regression to preceding region happened
        elif was_visited and fixation_position == 'before':
            regression_prob = 1
            break

    return regression_prob


def right_bound(region, fixations):
    '''Sum of all fixations in a region before it is exited to the right.
    '''
    right_bound_sum = 0.0

    # loop through each fixation
    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        # break as soon as region is exited to the right
        if fixation_position == 'after':
            break
        # until that happens, keep adding up durations
        elif fixation_position == 'within':
            right_bound_sum = right_bound_sum + duration

    return right_bound_sum


def rereading_time(region, fixations):
    '''Returns the difference between total reading time and the first pass 
    reading time for the current region.
    '''
    first_duration = first_pass(region, fixations)
    return total_time(region, fixations,) - first_duration


def total_time(region, fixations):
    '''Calculates overall total reading time for current ROI.
    '''
    total_time_sum = 0

    for X, Y, duration in fixations:
        # check where fixation was relative to region
        fixation_position = region_check(region, X, Y)
        if fixation_position == 'within':
            total_time_sum = total_time_sum + duration

    return total_time_sum


def single_fixation(region, fixations):
    '''Given a region, fixation list, and low/high cutoff values, returns
    the duration of the fixation on the region if it was the only fixation.
    Otherwise returns zero.
    '''
    first_fix = first_fixation(region, fixations)
    total_fixation = total_time(region, fixations)
    if first_fix == total_fixation:
        return total_fixation
    else:
        return 0


def prob_rereading(region, fixations):
    '''given a region and a fixations list calculates whether the region was
    reread or not.
    Returns either 1 or 0, having converted boolean test to an integer.
    '''
    return int(rereading_time(region, fixations) > 0)
