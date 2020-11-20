# Z:\UMMZ>python ummzgbif_functionv3.py UMMZ-TEST > log.txt

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
#from pygbif import occurrences as occ
import shutil
from pandas import read_excel
import json
import requests
import csv


now = datetime.datetime.now()

def parsefolder(fn):
    if fn.startswith('ummz-'):
        initSplit = fn.split("_")
        tripleSplit = initSplit[0]
        fsplit = tripleSplit.split("-")
        if len(fsplit) <= 2:
            print("Missing catalog number, contact Scott Martin")
            return
        else:
            ic = fsplit[0] #institutioncode
            cc = fsplit[1] #collectioncode --> use this to get contact email
            cn = fsplit[2] #catalognumber
            return ic, cc, cn
    else:
        print("Incorrect folder name! %s" %fn)
        return

def getgbif(ic, cc, cn):
    """
    Using the GBIF library, fetch UMMZ records
    """
    #https://www.gbif.org/occurrence/search?catalog_number=246790&collection_code=herps&institution_code=ummz
    #https://www.gbif.org/occurrence/1987105097
    gbif_baseurl = 'https://api.gbif.org/v1/'
    #url = gbif_baseurl + 'occurrence/search?' + 'catalog_number=' + cn + '&collection_code=' + cc + '&institution_code=' + ic
    #print(url)
    results = requests.get(gbif_baseurl + 'occurrence/search?' + 'catalog_number=' + cn + '&collection_code=' + cc + '&institution_code=' + ic)
    #https://api.gbif.org/v1/occurrence/search?catalog_number=124092&collection_code=mammals&institution_code=ummz
    key_list = json.loads(results.content.decode())
    #print(data)
    #print("line 80: %s " % key_list['results'])
    #for item in key_list['results']:
            #key = print(item['key'])
    #htmltext = key_list.json
    #print(htmltext)
    #key_list = occ.search(institutionCode=ic,collectionCode=cc,catalogNumber=cn)
    if key_list['results'] == []:
        print("No GBIF record for %s contact Scott Martin" % fname)
        ummzdict['ic'] = "error"
        ummzdict['cc'] = "error"
        ummzdict['cn'] = "error"
        return ummzdict

    else:
        gbif_baseurl = 'https://api.gbif.org/v1/'
        for item in key_list['results']:
                #print(item['key'])
                #key = print(item['key'])
                url = gbif_baseurl + 'occurrence/' + str(item['key']) + '/fragment'
                #print(url)
                record_results = requests.get(gbif_baseurl + 'occurrence/' + str(item['key']) + '/fragment')
                record_list = json.loads(record_results.content.decode())
                #print(record_list)
                #print(record_list['scientificName'])
                ummzdict['yuuid'] = item["key"]
                ummzdict['sciName'] = record_list["scientificName"]
                ummzdict['keyWords'] = (record_list["kingdom"], record_list["phylum"], record_list["class"], record_list["order"], record_list["family"], record_list["scientificName"], ummzdict['yuuid'])
                #print(ummzdict)
        return ummzdict

def getmediagroup(up, fn, ic, cc, cn, uid):
    uf = ""
    filepath = ""
    #ummzfiles = os.listdir(fn) # really need to zip these folders
    mgpath =  '%s/%s/' % (up, fn)
    mgName = [dI for dI in os.listdir(mgpath) if os.path.isdir(os.path.join(mgpath, dI))]

    for folders in mgName:
        #print(type(folders))
        if folders.startswith(("Raw", "Recon")):

            mgfolder = os.path.join(mgpath, folders)
            #print("mgfolder= %s" % mgfolder)
            zfolders = "%s" % folders
            try:
                # Modify zip name to include Darwin core triple and GBIF occurrence ID
                # shutil.make_archive(name_of_zip, 'zip', folder_to_be_zipped) mgfolder + ic + "-" + cc + "-" + cn + "-" + uid
                # zfiles = shutil.make_archive(mgfolder + "-" + str(uid), 'zip', mgfolder)
                zfiles = shutil.make_archive(mgfolder + "-" + str(uid), 'tar', mgfolder)
            except OSError:
                pass
            #zfilesplit = zfiles.split('/') # for Mac/Linux
            zfilesplit = zfiles.split('\\') # for Windows
            zsplit = zfilesplit[len(zfilesplit)-1]
            uf = uf + ("      - %s\n" % (zsplit))
            filepath = filepath + ("      - /deepbluedata-prep/UMMZ/%s/%s/%s\n" % (up, fn, zsplit))

            #Get tifs and ply files for previews
            plyfile = [f for f in os.listdir(mgfolder) if f.endswith('.ply')]
            if len(plyfile) != 0:
                uf = uf + ("      - %s\n" % (plyfile[0]))
                filepath = filepath + ("      - /deepbluedata-prep/UMMZ/%s/%s\n" % (mgfolder, plyfile[0]))
            if "Skull" in folders:
                img_files = [f for f in os.listdir(mgfolder) if f.endswith('.tif')]
                uf = uf + ("      - %s\n" % (img_files[0]))
                filepath = filepath + ("      - /deepbluedata-prep/UMMZ/%s/%s\n" % (mgfolder, img_files[0]))
            if "WholeBody" in folders:
                img_files = [f for f in os.listdir(mgfolder) if f.endswith('.tif')]
                fbimg = int(len(img_files)/2)
                uf = uf + ("      - %s\n" % (img_files[fbimg]))
                filepath = filepath + ("      - /deepbluedata-prep/UMMZ/%s/%s\n" % (mgfolder, img_files[fbimg]))

    return mgName, uf, filepath


def xtekdata(mgName):
    mgdesc = list()
    msMetadata = list()
    for mgroup in mgName:
        #print(mgroup)
        mdDict = dict()
        #msMetadata['mdDict']['name'] = mgroup
        #mdDict['part'] = mgroup
        if mgroup == 'surface_model':
            continue
        else:
            xpath =  '%s/%s/%s/' % (ummzpath,fname, mgroup)
            xtekpath = os.listdir(xpath)
            #print('mgfolder= %s' % (mgroup))
            if "WholeBody" in mgroup:
                mdDict['part'] = "WholeBody"
            else:
                mdDict['part'] = "Skull"

            #mdDict['part'] = roiName
            #xteckVol = 1
            #if line.startswith("InputFolderName"):
            match = re.search(r'\b\d{4}-\d\d?-\d\d?\b', fname)
            ummzdict['scandate'] = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
                 #print(filedate)
            mdDict['scandate'] = ummzdict['scandate']
            #shortMGroup = re.sub(r'-\b\d{4}-\d\d?-\d\d?\b', '', mgroup)
            for xtek in xtekpath:
                #xteckVol = 1

                if xtek.endswith(("_01.xtekct", ".xtekVolume")):
                    xtekfolder = os.path.join(xpath, xtek)
                    xtekfile = open(xtekfolder, "r")
                    #print(xtekfile)
                    for line in xtekfile:

                        if re.match("VoxelSizeX=", line):
                             voxRes = re.split('=', line)[-1]
                             #print(voxres)
                        if re.match("VoxelsX=", line):
                             voxX = re.split('=', line)[-1]
                             mdDict['x_spacing'] = voxX.rstrip('\r\n')
                             #print(voxX)
                        if re.match("VoxelsY=", line):
                             voxY = re.split('=', line)[-1]
                             mdDict['y_spacing'] = voxY.rstrip('\r\n')
                             #print(voxY)
                        if re.match("VoxelsZ=", line):
                             voxZ = re.split('=', line)[-1]
                             mdDict['z_spacing'] = voxZ.rstrip('\r\n')
                             #print(voxZ)
                        if re.match("Projections=", line):
                             proj = re.split('=', line)[-1]
                             #print(proj)
                    '''
                    if "Recon" in mgroup:
                        numtif = voxZ.rstrip('\r\n')
                        dataType = "Reconstructed -"
                    if "Raw" in mgroup:
                        numtif = proj.rstrip('\r\n')
                        dataType = "Raw -"
                    '''
                    mdDict['occurrence_id'] = "urn:catalog:" + ummzdict['ic'] + ":" + ummzdict['cc'] + ":" + ummzdict['cn']
                    mdDict["institution_code"] = ummzdict['ic']
                    mdDict["collection_code"] = ummzdict['cc']
                    mdDict["catalog_number"] = ummzdict['cn']
                    mdDict["device_model"] = "XT H225ST"
                    mdDict["device_manufacturer"] = "Nikon"
                    mdDict["device_modality"] = "Micro/Nano X-Ray Computed Tomography"
                    mdDict["device_description"] = ""
                    mdDict["device_organization_name"] = "University of Michigan Museum of Zoology"
                    #mdDict["x_spacing"] = voxX
                    #mdDict["y_spacing"] = voxY
                    #mdDict["z_spacing"] = voxZ
                    mdDict["unit"] = "mm"

                    if "Recon" in mgroup:
                        numtif = mdDict['z_spacing'].rstrip('\r\n')
                        mdDict["media_ct_number_of_images_in_set"] = mdDict['z_spacing'].rstrip('\r\n')
                        mdDict["processing_activity_type"] = "Reconstructed"
                        mdDict["media_ct_series_type"] = "Reconstructed Image Stack"
                    if "Raw" in mgroup:
                        numtif = proj.rstrip('\r\n')
                        mdDict["number_of_images_in_set"] = proj.rstrip('\r\n')
                        mdDict["processing_activity_type"] = "Raw"
                        mdDict["media_ct_series_type"] = "Projections"


                    if "WholeBody" in mgroup:
                        roiName = "WholeBody"
                    else:
                        roiName = "Skull"

                    mdDict["license"] = "https://creativecommons.org/licenses/by-nc-sa/4.0/"

                    #ydesc = ("    :description:\n      - 'Scan of specimen %s:%s:%s (%s) - %s . Dataset includes %s TIF images (each %s x %s x 1 voxel at %s mm resolution, derived from %s scan projections), xtek and vgi files for volume reconstruction.'\n" % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn'], ummzdict['sciName'], shortMGroup, numtif, voxX.rstrip('\r\n'), voxY.rstrip('\r\n'), voxres.rstrip('\r\n'), proj.rstrip('\r\n'))) #from xtek
                    ydesc = ("Scan of specimen %s:%s:%s (%s) - %s. %s Dataset includes %s TIF images (each %s x %s x 1 voxel at %s mm resolution, derived from %s scan projections), xtek and vgi files for volume reconstruction." % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn'], ummzdict['sciName'], mdDict['part'], mdDict["processing_activity_type"], numtif, mdDict['x_spacing'], mdDict['y_spacing'], voxRes.rstrip('\r\n'), proj.rstrip('\r\n'))) #from xtek
                    #print(ydesc)
                    mgdesc.append(ydesc)
                    break

                #else:
                    #xteckVol = 0
                    #continue
            #if xteckVol == 0:
                #print("No *.xtekVolume file found in %s!" % xpath)
        #print(mdDict)
        msMetadata.append(mdDict)
    ummzdict['desc'] =  mgdesc
    return ummzdict['desc'], msMetadata, roiName


def createyml(fname, uf, filepath, gbifl1, roiName):

    emailDict = {"birds" : "ummz-birds-data@umich.edu", "fish" : "ummz-fish-data@umich.edu" , "herps" : "ummz-herp-data@umich.edu", "insects": "ummz-insects-data@umich.edu" , "mammals" : "ummz-mammals-data@umich.edu", "mollusks" : "ummz-mollusks-data@umich.edu"}
    ownauth = emailDict.get(gbifl1, "")

    collDict = {"birds" : "Division of Birds", "fish" : "sj139222d" , "herps" : "05741r77z", "insects": "Division of Insects" , "mammals" : "nv935298c", "mollusks" : "Division of Mollusks"}
    collID = collDict.get(gbifl1, "")

    ytop = ("---\n:user:\n  :visibility: restricted\n  :email: '%s'\n  :ingester: 'fritx@umich.edu'\n  :source: DBDv2\n  :mode: build\n  :works:\n    :depositor: sborda@umich.edu\n" % (ownauth))
    yownauth = ("    :owner: '%s'\n    :authoremail: '%s'\n" % (ownauth, ownauth))
    ytitle = ("    :title: \n      - 'Computed tomography voxel dataset for %s:%s:%s-%s-%s' \n" % (ummzdict['ic'], ummzdict['cc'], ummzdict['cn'],ummzdict['sciName'], roiName))
    ydate = ("    :date_uploaded:\n      - '%s'\n" % (now.year))
    yrefby = ("    :referenced_by:\n      - 'For more information on the original UMMZ specimen, see: https://www.gbif.org/occurrence/%s'\n" % (ummzdict['yuuid'])) #build URL from iDigBio uuid\n      - ''\n"
    ymethod = "    :methodology:\n      - 'This dataset was created at the University of Michigan Museum of Zoology using a procedure involving computed tomography (CT) hardware. After retrieving the specimen from the museum''s archives, staff secured the specimen in the Nikon XT H 225 ST and initiated the scanning process, which included capturing projections by rotating the specimen. The device''s associated software CT-Pro-3D and the projections were then used to reconstruct a set of TIFF images, with each corresponding to a slice of the three-dimensional object (one voxel in height). In addition, the software created a .xtek volume file (included here), which contains details about the scanning environment, projections, and reconstructions.'\n"
    ypartof = "    :part_of:\n      - 'part of'\n"
    ycreator = "    :creator:\n      - 'University of Michigan Museum of Zoology'\n"
    ykw = ("    :keyword:\n      - %s\n      - 'computed tomography'\n      - 'X-ray'\n      - '3D' \n" % ('\n      - '.join("'{0}'".format(w) for w in ummzdict['keyWords'])))
    yrights = ("    :rights_license:\n      - https://creativecommons.org/licenses/by-nc-sa/4.0/ \n")
    ydatecov = ("    :date_coverage:\n      - '%s'\n" % (ummzdict['scandate'])) #from xtek
    ysubject = ("    :subject_discipline:\n      - 'Science'\n")
    #ybib = ("    :bibliographic_citation:\n      - 'For more information on the original UMMZ specimen, see: https://www.gbif.org/occurrence/%s'\n" % (ummzdict['yuuid'])) #build URL from iDigBio uuid
    ydesclist = ("    :description:\n      - %s\n" % ('\n      - '.join("'{0}'".format(w) for w in ummzdict['desc'])))
    ylang = ("    :language:\n      - 'English'\n")
    ycurnote = ("    :curation_notes_admin:\n      - 'UMMZ Batch Ingest'\n")
    ydoi = ("    :doi: 'mint_now'\n")
    ycoll = ("    :in_collections:\n      - %s \n" % (collID))
    yfilename = ("    :filenames:\n%s" % (uf)) #pull from directory
    yfiles = ("    :files:\n%s" % (filepath)) #pull from directory

    file_name = '%s/%s.yml' % (ummzpath, fname)
    f = open(file_name, 'w')  # open file in write mode

    f.write(ytop)
    f.write(ycoll)
    f.write(yownauth)
    f.write(ycreator)
    f.write(ytitle)
    #f.write(ydate)
    f.write(yrefby)
    f.write(ymethod)
    f.write(ykw)
    #for desc in ummzdict['desc']:
    f.write(ydesclist)
    f.write(yrights)
    f.write(ydatecov)
    f.write(ysubject)
    #f.write(ybib)
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
#print(ummzpath)
#get folder name from the system to parse into query fields
folderName = [dI for dI in os.listdir(ummzpath) if os.path.isdir(os.path.join(ummzpath,dI))]
#error handling for folder names (ex: not including catalognumber)
msMetadata = dict()
msFilePath = ummzpath + '/' + "DBD_file_manifest.csv"
with open(msFilePath, mode='w', encoding='utf8', newline='') as csv_file:
    fieldnames = ["file_name", "ms_id", "media_type", "ingestable", "parent_file_name", "parent_ms_id", "parent_identifier", "occurrence_id", "institution_code", "collection_code", "catalog_number", "scandate", "device_model", "device_manufacturer", "device_modality", "device_description", "device_organization_name", "x_spacing", "y_spacing", "z_spacing",  "unit", "number_of_images_in_set", "processing_activity_type", "creator", "part", "license", "media_ct_series_type", "media_ct_number_of_images_in_set"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for fname in folderName:
        #print(fname)
        ummzdict = dict()

        gbiflist = parsefolder(fname)
        if gbiflist == None:
            continue
        else:
            # Get data from GBIF
            #morphosourcemd(ummzpath, fname)
            ummzdict['ic'] = gbiflist[0]
            ummzdict['cc'] = gbiflist[1]
            ummzdict['cn'] = gbiflist[2]
            #print(ummzdict['ic'], ummzdict['cc'], ummzdict['cn'])
            getgbif(ummzdict['ic'], ummzdict['cc'], ummzdict['cn'])
            #print(ummzdict)
            if ummzdict['ic'] == "error":
                continue
            mgName, uf, filepath = getmediagroup(ummzpath, fname, ummzdict['ic'], ummzdict['cc'], ummzdict['cn'], ummzdict['yuuid']) # Get media groups zip media group folders
            desc, msMetadata, roiName  = xtekdata(mgName) # Get values from xtekVolume
            #create file with MorphoSource metadata for each work

            writer.writerows(msMetadata)
            createyml(fname, uf, filepath, gbiflist[1], roiName)
csv_file.close()

            #create a file manifest for MorphoSource of all datasets in batch
