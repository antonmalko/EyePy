##edited by: Shevaun Lewis
##last updated: 3/5/2013
# Fixed appalling problem in regionCheck

# A function is added for computing first-pass skip -- Wing-Yee Chow (3/6/2013)


# Idea from Sol: instead of NAs use 0s initially, then replace them with NAs

#### Region check ####
######################
# regionCheck takes a region [[Xstart, Ystart],[Xend, Yend]] and a pair of coordinates for a fixation.
# It returns 'within' if the fixation is in the region, 'before' if it's in a preceding region, and
# 'after' if it's in a later region.

def regionCheck(reg, fix):

    xStart = reg[0][0]                                   ## unpack region delimiters from reg
    yStart = reg[0][1]
    xEnd = reg[1][0]
    yEnd = reg[1][1]

    if fix[0]==-1:                              ## if the x=coordinate of fix is -1, then the fixation was
        return 'ignore'                         ## not properly edited/rejected. ignore for calculations, print feedback.
        print "fixation out of bounds: "+fix
    elif yStart==yEnd:                          ## if the region starts and ends on the same line
        if fix[1] == yStart:                     ## UPDATED: you have to check which line the FIXATION is on!!!
            if fix[0]>=xStart and fix[0]<xEnd:
                return 'within'
            elif fix[0]<xStart:
                return 'before'
            elif fix[0]>=xEnd:
                return 'after'
        elif fix[1] < yStart:
            return 'before'
        elif fix[1] > yStart:
            return 'after'
    else:                                       ## if the region starts and ends on different lines
        if fix[1]==yStart:                      ## if the fixation is on the first line
            if fix[0]>=xStart:
                return 'within'
            else:
                return 'before'
        elif fix[1]==yEnd:                      ## if the fixation is on the second line
            if fix[0]<xEnd:
                return 'within'
            else:
                return 'after'

#### First-pass Skip calculation####
###################################
# FIXME: define

def firstSkip(region, fixations, lowCutoff, highCutoff):
    fixTime = 'NA'                                  ## initialize fixTime as 'NA' (no fixation)
    skip = 1

    for f in fixations:                             ## loop through each fixation
        duration = f[3]-f[2]                        ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  #only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='within':     ## if fix is within region
                fixTime = duration                  ## store duration as first fixation time
                skip = 0
                break                               ## break the search as soon as you find the first fixation
            elif regionCheck(region,f)=='after':    ## if fix is after the region
                break                               ## break the search since the region has been skipped
    return skip                                     ## return the skip boolean

#### First fixation calculation####
###################################
# returns the duration of the first fixation in the region

def firstFix(region, fixations, lowCutoff, highCutoff):
    fixTime = 'NA'                                  ## initialize fixTime as 'NA' (no fixation)

    for f in fixations:                             ## loop through each fixation
        duration = f[3]-f[2]                        ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  #only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='within':     ## if fix is within region
                fixTime = duration                  ## store duration as first fixation time
                break                               ## break the search as soon as you find the first fixation
            elif regionCheck(region,f)=='after':    ## if fix is after the region
                break                               ## break the search since the region has been skipped
    return fixTime                                  ## return the first fixation time (which is 'NA' if none other is found)

#### First pass calculation####
###############################
# returns the sum of the fixations in the region before the region is exited in either direction

def firstPass(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0                                      ## initialize sum to 0

    for f in fixations:                                 ## loop through each fixation
        duration = f[3]-f[2]                            ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  ## only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='within':         ## if fix is within region
                fixTimeSum = fixTimeSum + duration      ## add duration to sum of fixations
            elif regionCheck(region,f)=='after':        ## if fix is after the region
                break                                   ## break, because the first pass is over.
            elif fixTimeSum>0 and regionCheck(region,f)=='before': ##if the region has already been entered at least once,
                break                                   ## and fix is before the region, then break, because the first pass is over

    return fixTimeSum


#### Regression path calculation####
####################################
## sums all the fixations in all the regions up to and including the
## region of interest, before that region is exited to the right

def regPath(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0

    for f in fixations:                                 ## loop through each fixation
        duration = f[3]-f[2]                            ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  ## only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='after':           ## if the fixation is after the ROI, break
                break
            elif regionCheck(region,f)=='within' or fixTimeSum>0:        ## if the fix is w/in the ROI or the ROI has already been visited
                fixTimeSum = fixTimeSum + duration                      ## add the duration to the sum

    if fixTimeSum==0:
        fixTimeSum='NA'

    return fixTimeSum


#### Right-bounded Reading Time calculation####
####################################
## sums all the fixations in a region before the region is exited to the right

def rightBound(region, fixations, lowCutoff, highCutoff):
    fixTimeSum = 0

    for f in fixations:                                 ## loop through each fixation
        duration = f[3]-f[2]                            ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  ## only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='after':           ## if the fixation is after the ROI, break
                break
            elif regionCheck(region,f)=='within':        ## if the fix is w/in the ROI
                fixTimeSum = fixTimeSum + duration      ## add the duration to the sum

    return fixTimeSum


#### Re-reading time calculation####
####################################

def rereadTime(region, fixations, lowCutoff, highCutoff):
    first = firstPass(region, fixations, lowCutoff, highCutoff)
    # change these two lines IK
    if first=='NA':
        reread = 'NA'
    else:
        reread = totalTime(region, fixations, lowCutoff, highCutoff) - first
    if reread==0:
        reread = 'NA'
    return reread

#### Total reading time calculation####
####################################

def totalTime(region, fixations, lowCutoff, highCutoff):

    fixTimeSum = 0

    for f in fixations:                                 ## loop through each fixation
        duration = f[3]-f[2]                            ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  ## only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='within':         ## if the fix is w/in the ROI
                fixTimeSum = fixTimeSum + duration      ## add the duration to the sum

    return fixTimeSum

#### % Regression calculation####
#################################
##FIXME:define
##Note that if you ever go past the region, you break from loop; so doesn't count any regressions after you leave region to right

def perReg(region, fixations, lowCutoff, highCutoff):
    visitreg = 0
    reg = 0

    for f in fixations:                                 ## loop through each fixation
        duration = f[3]-f[2]                            ## calculate duration (endtime - starttime)
        if duration>lowCutoff and duration<highCutoff:  ## only use fixation if duration is within cutoffs
            if regionCheck(region,f)=='after':          ## if the fixation is after the ROI, break
                break
            elif regionCheck(region,f)=='within':       ## if the fixation is in the ROI,
                visitreg = 1                            ## mark the ROI as having been visited at least once
            elif visitreg == 1 and regionCheck(region,f)=='before':     ## if the ROI has been visited at least once and the
                reg = 1                                                 ## fix is in a region before the ROI, count it
                break                                                   ## as a regression and break

    return reg


def single_fixation_duration(args):
    pass
    # duration of the first fixation into region if it was the only fixation in the region

def rereading_prob(ars):
    pass
    # boolean flag of whether the region was re-read (does this include both directions?)


