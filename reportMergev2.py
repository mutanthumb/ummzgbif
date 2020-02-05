# merge csv files to create file manifest for MorphoSource.

# read in DBD_file_manifest.csv as a list of dicts where each row is a dict

import csv
#msMetadata = csv.DictReader(open("UMMZ-ms/DBD_file_manifest.csv"))
'''
with open('UMMZ-ms/DBD_file_manifest.csv') as f:
    msMetadata = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]
'''
# read in batch_ummz_import_report.csv match each row to dict to fill in empty fields

i = 0
with open("batch_ummz_import_report.csv") as f:
    dbdFileInfo = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]
    #print(type(dbdFileInfo))
    tripList = list()
    dbdFileInfo_iter = iter(dbdFileInfo)
    #print(dbdFileInfo)

    numrows = len(dbdFileInfo)
    for row in dbdFileInfo_iter:

        #rawCt = 0
        tripleDict = dict()
        # parse Title for Darwin Core triple
        umzDCtripleSciName = row['Title'].split('for ')[1]
        umzDCtriple = umzDCtripleSciName.split('-')[0]
        idSplit = umzDCtriple.split(":")

        if idSplit[1] and idSplit[2] not in tripList:
            # append row to tripList
            tripleDict['ic'] = idSplit[0] #institutioncode
            tripleDict['cc'] = idSplit[1] #collectioncode --> use this to get contact email
            tripleDict['cn'] = idSplit[2] #catalognumber

        #print(row)

        if "Raw" in row['File Name']:
            rawID = row['File Set ID']
            rawCt = 1
        #print(rawCt)
        if "Recon" in row['File Name']:
            #check next record
            #print(rawCt)

            if rawCt == 0:
                #print(rawCt)
                #print(row)
                nextRow = next(dbdFileInfo_iter)
                #print("I have next!")
                #print(nextRow['File Name'])
                while i < numrows:
                    if idSplit[1] and idSplit[2] and "Raw" in nextRow['File Name']:
                    #if "Raw" in nextRow['File Name']:
                        #print("This is the parent record")
                        #print(row)
                        row['Parent ID'] = nextRow['File Set ID']
                        #print(row)
                        rawCt = 0
                        i == numrows
                        break
                    else:
                        print("not a raw file")
                        i = i + 1
                        print(i)
                        nextRow = next(dbdFileInfo_iter)

            if rawCt == 1:
                row['Parent ID'] = rawID
                rawCt = 0
                #print(row)
        tripList.append(tripleDict)
    i = 0
print(dbdFileInfo)
