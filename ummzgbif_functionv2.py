# Z:\UMMZ>python ummzgbif_functionv2.py UMMZ-TEST > log.txt

'''
Emails for ummz
All of UMMZ:
ummz-data@umich.edu

Divisions:
ummz-birds-data@umich.edu
ummz-fish-data@umich.edu
ummz-herp-data@umich.edu
ummz-insects-data@umich.edu
ummz-mammals-data@umich.edu
ummz-mollusks-data@umich.edu
'''

"""
Example:
Folder name: ummz-mammals-164676
"institutioncode": "ummz","collectioncode": "mammals","catalognumber": "164676"
"""
import os
from sys import argv
#import idigbio
import datetime
import glob
import fnmatch
import re
from pygbif import occurrences as occ
import shutil
from pandas import read_excel
import json

now = datetime.datetime.now()

def parsefolder(fn):
    if fn.startswith('ummz-'):
        fsplit = fn.split("-")
        if len(fsplit) <= 2:
            print("Missing catalog number, contact Scott Martin")
            return
        else:
            ic = fsplit[0] #institutioncode
            cc = fsplit[1] #collectioncode --> use this to get contact email
            cn = fsplit[2] #catalognumber
            return ic, cc, cn

def morphosourcemd(up, fn):
    my_sheet = 'Sheet1'
    file_name = '%s/MorphoSourceBatchImportWorksheet.xlsx' % (up)# name of your excel file
    df = read_excel(file_name, skiprows = 1, sheet_name = my_sheet)
    msfields = df.loc[df['MorphoSource Field'].str.contains(fn)]
    #print(df.head()) # shows headers with top 5 rows
    jstr = msfields.to_json()
    #pprint.pprint(jstr)
    msdf = '%s/%s/MorphoSourceFields.json' % (up, fn)
    msdatafile = open(msdf, "w") # Create in proper sub-folders
    msdatafile.write(json.dumps(json.loads(jstr), indent = 4, sort_keys=True))
    msdatafile.close()
    return

def getgbif(ic, cc, cn):
    """
    Using the GBIF library, fetch UMMZ records
    """
    #https://www.gbif.org/occurrence/search?catalog_number=56027&collection_code=herps&institution_code=ummz
    #https://www.gbif.org/occurrence/1987105097

    record_list = occ.search(institutionCode=ic,collectionCode=cc,catalogNumber=cn)
    if record_list['results'] == []:
        print("No GBIF record for %s contact Scott Martin" % fname)

    else:
        for item in record_list['results']:
                ummzdict['sciName'] = item["scientificName"]
                ummzdict['keyWords'] = (item["kingdom"], item["phylum"], item["class"], item["order"], item["family"], item["scientificName"])
                ummzdict['yuuid'] = item["key"]

    return ummzdict

def getmediagroup(up, fn):
    uf = ""
    filepath = ""
    #ummzfiles = os.listdir(fn) # really need to zip these folders
    mgpath =  '%s/%s/' % (up, fn)
    mgName = [dI for dI in os.listdir(mgpath) if os.path.isdir(os.path.join(mgpath, dI))]

    for folders in mgName:
        mgfolder = os.path.join(mgpath, folders)
        #print(mgfolder)
        zfolders = "%s" % folders
        zfiles = shutil.make_archive(mgfolder, 'zip', mgfolder)
        zfilesplit = zfiles.split('\\')
        zsplit = zfilesplit[len(zfilesplit)-1]
        uf = uf + ("      - %s\n" % (zsplit))
        filepath = filepath + ("      - /deepbluedata-prep/UMMZ/%s/%s/%s\n" % (up, fn, zsplit))

    return mgName, uf, filepath

def xtekdata(mgName):
    mgdesc = list()
    for mgroup in mgName:
        if mgroup == 'surface_model':
            continue
        else:
            xpath =  '%s/%s/%s/tiff_16bit/' % (ummzpath,fname, mgroup)
            xtekpath = os.listdir(xpath)
            xteckVol = 1
            for xtek in xtekpath:
                xteckVol = 1
                if xtek.endswith(".xtekVolume"):
                    xtekfolder = os.path.join(xpath, xtek)
                    xtekfile = open(xtekfolder, "r")
                    for line in xtekfile:
                        if line.startswith("InputFolderName"):
                             match = re.search(r'\b\d{4}-\d\d?-\d\d?\b', line)
                             ummzdict['filedate'] = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
                             #print(filedate)
                        if re.match("VoxelSizeX=", line):
                             voxres = re.split('=', line)[-1]
                             #print(voxres)
                        if re.match("VoxelsX=", line):
                             voxX = re.split('=', line)[-1]
                             #print(voxX)
                        if re.match("VoxelsY=", line):
                             voxY = re.split('=', line)[-1]
                             #print(voxY)
                        if re.match("VoxelsZ=", line):
                             voxZ = re.split('=', line)[-1]
                             #print(voxZ)
                        if re.match("Projections=", line):
                             proj = re.split('=', line)[-1]
                             #print(proj)
                    ydesc = ("    :description:\n      - 'Scan of specimen %s %s %s (%s) - %s . Dataset includes %s TIF images (each %s x %s x 1 voxel at %s mm resolution, derived from %s scan projections), xtek and vgi files for volume reconstruction.'\n" % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn'], ummzdict['sciName'], mgroup, voxZ.rstrip('\r\n'), voxX.rstrip('\r\n'), voxY.rstrip('\r\n'), voxres.rstrip('\r\n'), proj.rstrip('\r\n'))) #from xtek
                    #print(ydesc)
                    mgdesc.append(ydesc)
                    break

                else:
                    xteckVol = 0
                    continue
            if xteckVol == 0:
                print("No *.xtekVolume file found in %s!" % xpath)
    ummzdict['desc'] =  mgdesc
    return ummzdict['desc']

def createyml(fname, uf, filepath, gbifl1):

    emailDict = {"birds" : "ummz-birds-data@umich.edu", "fish" : "ummz-fish-data@umich.edu" , "herps" : "ummz-herp-data@umich.edu", "insects": "ummz-insects-data@umich.edu" , "mammals" : "ummz-mammals-data@umich.edu", "mollusks" : "ummz-mollusks-data@umich.edu"}

    ownauth = emailDict.get(gbifl1, "")

    ytop = "---\n:user:\n  :visibility: open\n  :email: sborda@umich.edu\n  :works:\n    :depositor: sborda@umich.edu\n"
    yownauth = ("    :owner: '%s'\n    :authoremail: '%s'\n" % (ownauth, ownauth))
    ytitle = ("    :title: \n      - 'Computed tomography voxel dataset for %s:%s:%s' \n" % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn']))
    ydate = ("    :date_uploaded:\n      - '%s'\n" % (now.year))
    yrefby = "    :isReferencedBy:\n      - ''\n"
    ymethod = "    :methodology: 'This dataset was created at the University of Michigan Museum of Zoology using a procedure involving computed tomography (CT) hardware. After retrieving the specimen from the museum’s archives, staff secured the specimen in the Nikon XT H 225 ST and initiated the scanning process, which included capturing projections by rotating the specimen. The device’s associated software Inspect-X and the projections were then used to reconstruct a set of TIFF images, with each corresponding to a slice of the three-dimensional object (one voxel in height). In addition, the software created a .xtek volume file (included here), which contains details about the scanning environment, projections, and reconstructions.'\n"
    ypartof = "    :part_of:\n      - 'part of'\n"
    ycreator = "    :creator:\n      - 'University of Michigan Museum of Zoology'\n"
    ykw = ("    :keyword:\n      - '%s, computed tomography, X-ray, 3D' \n" % (', '.join(ummzdict['keyWords'])))
    yrights = ("    :rights: https://creativecommons.org/licenses/by-nc-sa/4.0/ \n")
    ydatecov = ("    :date_coverage:\n      - '%s'\n" % (ummzdict['filedate'])) #from xtek
    ysubject = ("    :subject:\n      - 'Science'\n")
    ybib = ("    :bibliographic_citation:\n      - 'For more information on the original UMMZ specimen, see: https://www.gbif.org/occurrence/%s'\n" % (ummzdict['yuuid'])) #build URL from iDigBio uuid
    ylang = ("    :language:\n      - 'English'\n")
    ycurnote = ("    :curation_notes_admin:\n      'UMMZ Batch Ingest'\n")
    ydoi = ("    :doi: 'mint now'\n")
    yfilename = ("    :filenames:\n %s" % (uf)) #pull from directory
    yfiles = ("    :files:\n %s" % (filepath)) #pull from directory

    file_name = '%s/%s.yml' % (ummzpath, fname)
    f = open(file_name, 'w')  # open file in write mode

    f.write(ytop)
    f.write(yownauth)
    f.write(ytitle)
    f.write(ydate)
    f.write(yrefby)
    f.write(ymethod)
    f.write(ykw)
    for desc in ummzdict['desc']:
        f.write(desc)
    f.write(yrights)
    f.write(ydatecov)
    f.write(ysubject)
    f.write(ybib)
    f.write(ylang)
    f.write(ycurnote)
    f.write(ydoi)
    f.write(yfilename)
    f.write(yfiles)
    f.close()
    return

### Start here!!
#ummzpath = input("UMMZ folder path: ")
ummzpath = argv[1] #For example UMMZ-02-22-219
print(ummzpath)
#get folder name from the system to parse into query fields
folderName = [dI for dI in os.listdir(ummzpath) if os.path.isdir(os.path.join(ummzpath,dI))]
#error handling for folder names (ex: not including catalognumber)
for fname in folderName:
    ummzdict = dict()
    gbiflist = parsefolder(fname)
    if gbiflist == None:
        continue
    else:
        # Get data from GBIF
        morphosourcemd(ummzpath, fname)
        ummzdict['ic'] = gbiflist[0]
        ummzdict['cc'] = gbiflist[1]
        ummzdict['cn'] = gbiflist[2]
        getgbif(ummzdict['ic'], ummzdict['cc'], ummzdict['cn'])
        mgName, uf, filepath = getmediagroup(ummzpath, fname) # Get media groups zip media group folders
        xtekdata(mgName) # Get values from xtekVolume
        createyml(fname, uf, filepath, gbiflist[1])
