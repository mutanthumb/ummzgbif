
#> python3 ./scripts/reorder_roi.py ./UMMZ-ms/

# read list of folders
# create new parent folder(s) based on folders that exist in specified folder
# -- use regex for first part of folders new folder name == everything up "_"
# move folders matching above regex into newly created folder(s)
# open sub folder with same name as parent w/o [date]
# look for *.xtekVolume file parse as per usual
# zip folders by skull or whole body
# create *.yml in parent folder created in line #2

from sys import argv
import os.path
import pathlib
import shutil
from os import listdir
from os.path import isfile, join
import re
from re import search
import datetime
from os import walk

#print(os.getcwd())

topDir = [d for d in os.listdir(argv[1]) if os.path.isdir(os.path.join(argv[1], d))]
#print(type(topDir))
os.chdir('./' + argv[1] + '/')
#print(os.getcwd())

for nestDir in topDir:
    print(nestDir)

    ummzpath = './' + nestDir +'/'
    #print(ummzpath)
    dirs = [d for d in os.listdir(ummzpath) if os.path.isdir(os.path.join(ummzpath, d))]
    #dirs = list
    #print(dirs)

    newdir = list()
    for specDir in dirs:
        #print(specDir)
        umztripledir = re.split(' +', specDir)[0]
        #print(re.split(' +', specDir))
        #print(umztripledir)
        scandate = re.split(' +', specDir)[1]
        match = re.search(r'\b\d{4}-\d\d?-\d\d?\b', scandate)
        newdate = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
        #print(newdate)
        newSpecDir = umztripledir + "-" + str(newdate)

        #print(umztripledir)
        if "skull" in specDir:
            if "_skull " in specDir:
                clipSkull = umztripledir.split('_skull')[0]
                os.mkdir(ummzpath + specDir + '/' + "Raw-Skull-" + clipSkull)
                rawTarDir = ummzpath + specDir + '/' + "Raw-Skull-" + clipSkull
            if "skulldice" in specDir:
                clipSkull = umztripledir.replace("skull", "")
                os.mkdir(ummzpath + specDir + '/' + "Raw-Skull-" + clipSkull)
                rawTarDir = ummzpath + specDir + '/' + "Raw-Skull-" + clipSkull
        else:
            os.mkdir(ummzpath + specDir + '/' + "Raw-WholeBody-" + umztripledir)
            rawTarDir = ummzpath + specDir + '/' + "Raw-WholeBody-" + umztripledir
        roiDir = ummzpath + specDir
        #roiAll = os.listdir(roiDir)
        #print(rawTarDir)
        roiSubDirs = [d for d in os.listdir(roiDir) if os.path.isdir(os.path.join(roiDir, d))]
        roiFiles = [f for f in listdir(roiDir) if isfile(join(roiDir, f))]

        for files in roiFiles:
            #print(files)
            shutil.move(roiDir + '/' + files, rawTarDir)
        for dirs in roiSubDirs:
            if "Raw" not in dirs:
                #print(dirs)
                if search(umztripledir, dirs):
                    #print(os.getcwd())
                    #print(dirs)
                    if "skull" in specDir:
                        if "_skull " in specDir:
                            reconTargetDir = ummzpath + specDir + '/' + "Recon-Skull-" + clipSkull
                        if "skulldice" in specDir:
                            reconTargetDir = ummzpath + specDir + '/' + "Recon-Skull-" + clipSkull                        
                    else:
                        reconTargetDir = ummzpath + specDir + '/' + "Recon-WholeBody-" + umztripledir
                    os.rename(ummzpath + specDir + '/' + dirs, reconTargetDir)
                else:
                    shutil.move(roiDir + '/' + dirs, rawTarDir)
        os.rename(ummzpath + specDir, ummzpath + newSpecDir)
