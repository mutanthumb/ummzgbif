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

dirs = [d for d in os.listdir('UMMZ-05-20-2019') if os.path.isdir(os.path.join('UMMZ-05-20-2019', d))]
#dirs = list
#print(dirs)

newdir = list()
for dir in dirs:
    shortdir = dir.split('_')[0]
    shorttargetdir = 'UMMZ-05-20-2019/' + shortdir
    sourcedir = 'UMMZ-05-20-2019/' + dir + '/'
    targetdir = shorttargetdir + '/'
    if shortdir not in newdir:
        pathlib.Path(shorttargetdir).mkdir(parents=True, exist_ok=True)
    shutil.move(sourcedir, targetdir)
    mgs = [d for d in os.listdir(shorttargetdir) if os.path.isdir(os.path.join(shorttargetdir, d))]
    #print(mgs)
    for mg in mgs:
        #newsource = shorttargetdir + mg
        if 'skull' in mg:
            shutil.move(shorttargetdir + '/' + mg, shorttargetdir + '/' + 'skull')
            xtekV = [d for d in os.listdir(shorttargetdir + '/' + 'skull') if os.path.isdir(os.path.join(shorttargetdir + '/' + 'skull', d))]
            print(xtekV)
            for xv in xtekV:
                if shortdir in xv:
                    shutil.move(shorttargetdir + '/' + 'skull/' + xv, shorttargetdir + '/' + 'skull/' + 'tiff_16bit')
        else:
            shutil.move(shorttargetdir + '/' + mg, shorttargetdir + '/' + 'whole-body')
            xtekV = [d for d in os.listdir(shorttargetdir + '/' + 'whole-body') if os.path.isdir(os.path.join(shorttargetdir + '/' + 'whole-body', d))]
            print(xtekV)
            for xv in xtekV:
                if shortdir in xv:
                    shutil.move(shorttargetdir + '/' + 'whole-body/' + xv, shorttargetdir + '/' + 'whole-body/' + 'tiff_16bit')
