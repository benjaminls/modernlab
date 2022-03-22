# PARSER
#     \
# LOCAL VARIABLE  -->  EXPORT TO CSV
#       |
# POS TO DISPLACEMENT
#       |
# REORGANIZE FROM BY
# PARTICLE TO BY FRAME
#       |
#  COMPUTE MSD 
#  & GET STDEV
#    /     \
# PLOT     EXPORT CSV

import os
import sys
import numpy as np

# datafile must be in same directory as the script when run
filename = sys.argv[1]
if filename not in os.listdir():
    print('ERROR: Cannot find \"', filename, '\" in the current working directory.\n')
    print(
        'Make sure the datafile you are trying to analyze is in the same place as this script when you run it.\n'
        )
    print(
        'Make sure you are typing the full filename correctly, including the file extension.\n'
    )
    sys.exit()


def split_points(vdata):
    global FRAMECOUNT

    trajlens = []
    l = 0
    for i in range(len(vdata)):
        if vdata[i] != '%':
            l += 1
            if i == len(vdata) - 1:     # appends the last trajectory
                trajlens.append(l)
        elif l != 0:
            trajlens.append(l)
            l = 0
    FRAMECOUNT = max(trajlens)
    # print(trajlens)
    out = []
    for i in range(len(trajlens)):
        if i == 0:
            out.append(trajlens[0])
        else:
            out.append(out[i-1] + trajlens[i])

    return out


def split_list(dataset, vdata):
    slist = np.split(dataset, split_points(vdata))
    slist = slist[:-1]
    return slist


def filter_complete(dataset):
    """Filter out all trajectories that don't span all frames.

    Args:
        dataset (list): data grouped by trajectory number

    Returns:
        list: filtered dataset of only complete trajectories
    """
    global PARTICLECOUNT

    out = []
    for i in range(len(dataset)):
        if len(dataset[i]) == FRAMECOUNT:
            out.append(dataset[i])
    PARTICLECOUNT = len(out)        # number of particles per frame after
                                    #   filtering for complete trajectories
    return out


def square_displacement(dataset):
    disp2list = [[] for item in range(FRAMECOUNT)]
    # print(len(disp2list))
    for t in range(len(dataset)):   # loop over trajectories
        traj = dataset[t]
        n_points = len(traj)
        # print(traj)
        for i in range(n_points):
            ind = int(traj[i][0])
            (x0, y0) = traj[0][1:]
            (xi, yi) = traj[i][1:]
            disp2 = (x0 - xi)**2 + (y0 - yi)**2
            # print(ind)
            disp2list[ind] += [disp2]
    
    return disp2list


def get_msd(disp2list):
    msd_list = []
    msd_stdev_list = []
    for i in range(FRAMECOUNT):
        disp2avg = np.sum(disp2list[i]) / PARTICLECOUNT
        stdev = np.std(disp2list[i]) / PARTICLECOUNT
        msd_list.append(disp2avg)
        msd_stdev_list.append(stdev)
    return (msd_list, msd_stdev_list)


# def organize(dataset):
#     out = [[] for item in range(len(FRAMECOUNT))]


# def split_traj(dataset):
#     # list of column 0 from dataset (frame #)
#     framelist = [item[0] for item in dataset]
#     # list of indices of all 0s in framelist
#     ind0s = [i for i, x in enumerate(framelist) if x == 0]
#     trajlen = []
#     for i in range(len(ind0s)):
#         length = ind0s[i+1] - ind0s[i]

#     for i in range(len(ind0s)):
#         ind_lower = ind0s[i]
#         ind_upper = ind0s[i+1] - 1
        

# filename = 'trajectories_2_micron_250_ml_(2)_link5_disp10.txt'

# Columns:
# frame | x (pixel) | y (pixel) | z (pixel) | m0 | m1 | m2 | m3 | m4 | s 
data = np.loadtxt(filename, comments='%', usecols=(0,1,2))
vdata = np.loadtxt(filename, comments=(' ', '% '), dtype=str)

data = split_list(data, vdata)
data = filter_complete(data)

disp2list = square_displacement(data)
(msd_list, msd_stdev_list) = get_msd(disp2list)

plt.errorbar(
    list(range(501)), 
    msd_list, 
    yerr=msd_stdev_list, 
    elinewidth=0.3, 
    capsize=0.1, 
    capthick=0.1,
    )

info = np.array([
    ['File Name: ', filename],
    ['Number of frames: ', FRAMECOUNT],
    ['Number of particles: ', PARTICLECOUNT],
    ['Distance units: ', 'pixels^2'], 
])



# brownian_output
#   |_  output_0
#   |       |_  msd.csv             >> mean square displacement data
#   |       |_  msd_stdev.csv       >> msd standard deviation data
#   |       |_  info.txt            >> important parameters & info
#   |       |_  raw.csv             >> copy of raw data used to produce output
#   |_  output_1
#   |       |_  msd.csv
#   |       |_  msd_stdev.csv
#   |       |_  info.txt
#   |       |_  raw.csv
#   |_  output_2
#   |       |_  ...
#   |_  output_3
#   |       |_  ...
#   |_  ...
#   |
#   |_  output_n


# store all output files in an output directory
outputdir = 'brownian_output'       # name of output directory
CWD = os.getcwd()                   # current working directory
print('Current Working Directory: ', CWD)

msd_list = np.asarray(msd_list)
msd_stdev_list = np.asarray(msd_stdev_list)

if outputdir in os.listdir():
    print('Found existing ', outputdir, ' in current working directory. ')
    print('All files will be saved in ', outputdir, '.')
else:
    print('Preexisting output directory not found.')
    print('Creating one now...')
    os.mkdir(outputdir)

# create dir in outputdir
os.chdir(os.path.join(CWD, outputdir))
n = 0
dirname = 'output_' + str(n)
while dirname in os.listdir():
    n += 1
    dirname = 'output_' + str(n)
print('Created new directory ', dirname, ' in ', outputdir)

# move into new output_n directory inside outputdir
os.chdir(os.path.join(CWD, outputdir, dirname))
print('Writing data...')
np.savetxt("msd.csv", msd_list, delimiter=",")
np.savetxt("msd_stdev.csv", msd_stdev_list, delimiter=",")
np.savetxt("info.txt", info, delimiter=", ")