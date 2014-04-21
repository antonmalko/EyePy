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
        print("fixation out of bounds: " + fixation)
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
        if lowCutoff < duration < highCutoff:
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
        if lowCutoff < duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
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


def first_pass(region, fixations, lowCutoff, highCutoff):
    '''Given a region and a list of fixations as well as cutoff values,
    returns the sum of all the fixations in the region before it is exited in 
    either direction.
    '''
    first_pass_sum = 0  # initialize sum to 0

    # loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if lowCutoff < duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
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


def regression_path(region, fixations, lowCutoff, highCutoff):
    '''Sums up fixation durations for the current region N and all regions 
    to the left of N starting with when region N was entered and up to the point
    when it was exited to the right.
    '''
    regression_sum = 0.0

    # loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if lowCutoff < duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
            # if the region was exited to the right, break
            if fixation_position == 'after':
                break
            # if the fixation is w/in the ROI or the ROI has already been visited
            elif fixation_position == 'within' or regression_sum > 0:
                # add the duration to the sum
                regression_sum = regression_sum + duration

    return regression_sum


def right_bound(region, fixations, lowCutoff, highCutoff):
    '''Sum of all fixations in a region before it is exited to the right.
    '''
    right_bound_sum = 0.0

    # loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if lowCutoff < duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
            # break as soon as region is exited to the right
            if fixation_position == 'after':
                break
            # until that happens, keep adding up durations
            elif fixation_position == 'within':
                right_bound_sum = right_bound_sum + duration

    return right_bound_sum


def rereading_time(region, fixations, lowCutoff, highCutoff):
    '''Returns the difference between total reading time and the first pass 
    reading time for the current region.
    '''
    first_duration = first_pass(region, fixations, lowCutoff, highCutoff)
    return total_time(region, fixations, lowCutoff, highCutoff) - first_duration


def total_time(region, fixations, lowCutoff, highCutoff):
    '''Calculates overall total reading time for current ROI.
    '''
    total_time_sum = 0

    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if lowCutoff < duration < highCutoff:
            # only add fixations in the ROI
            if region_check(region, f) == 'within':
                total_time_sum = total_time_sum + duration

    return total_time_sum


def percent_regression(region, fixations, lowCutoff, highCutoff):
    '''Returns either 1 or 0 depending on whether a regression happens 
    from current region.
    '''
    was_visited = False
    regression_prob = 0

    ## loop through each fixation
    for f in fixations:
        duration = f[3] - f[2]  # calculate duration (endtime - starttime)
        # only use fixation if duration is within cutoffs
        if lowCutoff < duration < highCutoff:
            # check where fixation was relative to region
            fixation_position = region_check(region, f)
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


def single_fixation_duration(region, fixations, lowCutoff, highCutoff):
    '''Given a region, fixation list, and low/high cutoff values, returns
    the duration of the fixation on the region if it was the only fixation.
    Otherwise returns zero.
    '''
    first_fixation = first_fixation(region, fixations, lowCutoff, highCutoff)
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
