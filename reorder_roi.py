# read list of folders
# create new parent folder(s) based on folders that exist in specified folder
# -- use regex for first part of folders new folder name == everything up "_"
# move folders matching above regex into newly created folder(s)
# open sub folder with same name as parent w/o [date]
# look for *.xtekVolume file parse as per usual
# zip folders by skull or whole body
# create *.yml in parent folder created in line #2


import os.path
import pathlib
import shutil
from os import listdir
from os.path import isfile, join
import re
from re import search
import datetime
from os import walk

dirs = [d for d in os.listdir('UMMZ-ms') if os.path.isdir(os.path.join('UMMZ-ms', d))]
#dirs = list
#print(dirs)

newdir = list()
for specDir in dirs:
    #print(dir)
    umztripledir = specDir.split(' ')[0]
    scandate = specDir.split(' ')[1]
    match = re.search(r'\b\d{4}-\d\d?-\d\d?\b', scandate)
    newdate = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
    print(newdate)
    newSpecDir = umztripledir + "-" + str(newdate)

    #print(umztripledir)
    if "skull" in specDir:
        clipSkull = umztripledir.split('_skull')[0]
        os.mkdir('UMMZ-ms/' + specDir + '/' + "Raw-Skull-" + clipSkull)
        rawTarDir = 'UMMZ-ms/' + specDir + '/' + "Raw-Skull-" + clipSkull
    else:
        os.mkdir('UMMZ-ms/' + specDir + '/' + "Raw-WholeBody-" + umztripledir)
        rawTarDir = 'UMMZ-ms/' + specDir + '/' + "Raw-WholeBody-" + umztripledir
    roiDir = 'UMMZ-ms/' + specDir
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
                    reconTargetDir = 'UMMZ-ms/' + specDir + '/' + "Recon-Skull-" + clipSkull
                else:
                    reconTargetDir = 'UMMZ-ms/' + specDir + '/' + "Recon-WholeBody-" + umztripledir
                os.rename('UMMZ-ms/' + specDir + '/' + dirs, reconTargetDir)
            else:
                shutil.move(roiDir + '/' + dirs, rawTarDir)
    os.rename('UMMZ-ms/' + specDir, 'UMMZ-ms/' + newSpecDir)
