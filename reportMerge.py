# merge csv files to create file manifest for MorphoSource.

# read in DBD_file_manifest.csv as a list of dicts where each row is a dict

import csv
#msMetadata = csv.DictReader(open("UMMZ-ms/DBD_file_manifest.csv"))
with open('UMMZ-ms/DBD_file_manifest.csv') as f:
    msMetadata = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

#print(msMetadata)
# read in batch_ummz_import_report.csv match each row to dict to fill in empty fields
with open("REAL_batch_ummz_import_report.csv") as dbdf:
    dbdInfo = [{k: v for k, v in row.items()}
        for row in csv.DictReader(dbdf, skipinitialspace=True)]

fn_fid = dict()

msFilePath = "MorphoSource_file_manifest.csv"
with open(msFilePath, mode='w', encoding='utf8', newline='') as csv_file:
    fieldnames = ["file_name", "ms_id", "media_type", "ingestable", "parent_file_name", "parent_ms_id", "parent_identifier", "occurrence_id", "institution_code", "collection_code", "catalog_number", "scandate", "device_model", "device_manufacturer", "device_modality", "device_description", "device_organization_name", "x_spacing", "y_spacing", "z_spacing",  "unit", "number_of_images_in_set", "processing_activity_type", "creator", "part", "license", "media_ct_series_type", "media_ct_number_of_images_in_set"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for row in dbdInfo:
        fn_fid.update({row["File Name"]:row['File Set ID']})
    for specimen in msMetadata:
        if specimen["file_name"] in fn_fid.keys():
            #print(fn_fid[specimen["file_name"]])
            specimen["file_name"] = 'https://deepblue.lib.umich.edu/data/downloads/' + fn_fid[specimen["file_name"]]
            if specimen["parent_file_name"] in fn_fid.keys():
                specimen["parent_file_name"] = 'https://deepblue.lib.umich.edu/data/downloads/' + fn_fid[specimen["parent_file_name"]]
            #for msrow in msMetadata:
                #dlURL = 'https://deepblue.lib.umich.edu/data/downloads/' + row['File Set ID']
                #print(dlURL)
                # recon comes first find related Raw entry and load that first then recon

            #print(specimen)
            writer.writerow(specimen)





    # look for match in manifest dict
    # further parse on File Name for "Raw" or "Recon"
    # Raw file will be parent to Recon file
