#from https://github.com/iDigBio/idigbio-search-api/wiki/Code-Samples

#sample from iDigBio: https://www.idigbio.org/portal/records/f217b2b6-f9fa-409c-a8bd-ab40bae240b7

"""
Example:
Folder name: ummz-mammals-164676
"institutioncode": "ummz","collectioncode": "mammals","catalognumber": "164676"
"""
import os
#import idigbio
import datetime
import glob
import fnmatch
import re
from pygbif import occurrences as occ
import shutil

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

def getgbif(ic, cc, cn):
    """
    Using the GBIF library, fetch UMMZ records
    """
    #https://www.gbif.org/occurrence/search?catalog_number=56027&collection_code=herps&institution_code=ummz
    #https://www.gbif.org/occurrence/1987105097

    record_list = occ.search(institutionCode=ic,collectionCode=cc,catalogNumber=cn)

    for item in record_list['results']:
            ummzdict['sciName'] = item["scientificName"]
            ummzdict['keyWords'] = (item["kingdom"], item["phylum"], item["class"], item["order"], item["family"], item["scientificName"])
            ummzdict['yuuid'] = item["key"]

    return ummzdict

def getmediagroup(fn):
    uf = ""
    #ummzfiles = os.listdir(fn) # really need to zip these folders
    mgName = [dI for dI in os.listdir(fn) if os.path.isdir(os.path.join(fn,dI))]
    mgpath =  '%s/%s/' % (ummzpath,fname)

    for folders in mgName:
        mgfolder = os.path.join(mgpath, folders)
        #print(mgfolder)
        zfolders = "%s" % folders
        zfiles = shutil.make_archive(mgfolder, 'zip', mgfolder)
        zfilesplit = zfiles.split('/')
        zsplit = zfilesplit[len(zfilesplit)-1]
        uf = uf + ("      - %s\n" % (zsplit))

    filepath = ""
    for files in mgName:
        filepath = filepath + ("      - /hydra-dev/umrdr-data/%s/%s\n" % (fname, zsplit))

    return mgName, uf, filepath

def xtekdata(mgName):
    mgdesc = list()
    for mgroup in mgName:
        xpath =  '%s/%s/%s/tiff_16bit/' % (ummzpath,fname, mgroup)
        xtekpath = os.listdir(xpath)
        for xtek in xtekpath:
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
    ummzdict['desc'] =  mgdesc
    return ummzdict['desc']

def createyml(fname, uf, filepath):

    ytop = "---\n:user:\n  :visibility: open\n  :email: sborda@umich.edu\n  :works:\n    :depositor: sborda@umich.edu\n    :owner: ummz@umich.edu\n    :authoremail: ummz@umich.edu\n"
    ytitle = ("    :title: \n      - 'Computed tomography voxel dataset for %s:%s:%s' \n" % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn']))
    ydate = ("    :date_uploaded:\n      - '%s'\n" % (now.year))
    yrefby = "    :isReferencedBy:\n      - ''\n"
    ymethod = "    :methodology: 'This dataset was created at the University of Michigan Museum of Zoology using a procedure involving computed tomography (CT) hardware. After retrieving the specimen from the museum’s archives, staff secured the specimen in the Nikon XT H 225 ST and initiated the scanning process, which included capturing projections by rotating the specimen. The device’s associated software Inspect-X and the projections were then used to reconstruct a set of TIFF images, with each corresponding to a slice of the three-dimensional object (one voxel in height). In addition, the software created a .xtek volume file (included here), which contains details about the scanning environment, projections, and reconstructions.'\n"
    ypartof = "    :part_of:\n      - 'part of'\n"
    ycreator = "    :creator:\n      - 'University of Michigan Museum of Zoology'\n"
    ykw = ("    :keyword:\n      - '%s, computed tomography, X-ray, 3D' \n" % (', '.join(ummzdict['keyWords'])))
    #ydesc = ("    :description:\n      - 'Scan of specimen %s %s %s (%s). Dataset includes %s TIF images (each %s x %s x 1 voxel at %s mm resolution, derived from %s scan projections), xtek and vgi files for volume reconstruction.'\n" % (ic, cc, cn, sciName, voxZ.rstrip('\r\n'), voxX.rstrip('\r\n'), voxY.rstrip('\r\n'), voxres.rstrip('\r\n'), proj.rstrip('\r\n'))) #from xtek
    yrights = ("    :rights: https://creativecommons.org/licenses/by-nc-sa/4.0/ \n")
    ydatecov = ("    :date_coverage:\n      - '%s'\n" % (ummzdict['filedate'])) #from xtek
    ysubject = ("    :subject:\n      - 'Science'\n")
    ybib = ("    :bibliographic_citation:\n      - 'For more information on the original UMMZ specimen, see: https://www.idigbio.org/portal/records/%s'\n" % (ummzdict['yuuid'])) #build URL from iDigBio uuid
    ylang = ("    :language:\n      - 'English'\n")
    yfilename = ("    :filenames:\n %s" % (uf)) #pull from directory
    yfiles = ("    :files:\n %s" % (filepath)) #pull from directory



    file_name = '%s.yml' % fname
    f = open(file_name, 'w')  # open file in write mode

    f.write(ytop)
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
    f.write(yfilename)
    f.write(yfiles)
    f.close()
    return

### Start here!!
ummzpath = input("UMMZ folder path: ")
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
        ummzdict['ic'] = gbiflist[0]
        ummzdict['cc'] = gbiflist[1]
        ummzdict['cn'] = gbiflist[2]
        getgbif(ummzdict['ic'], ummzdict['cc'], ummzdict['cn'])
        mgName, uf, filepath = getmediagroup(fname) # Get media groups zip media group folders
        xtekdata(mgName) # Get values from xtekVolume
        createyml(fname, uf, filepath)
