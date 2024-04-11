# merge csv files to create file manifest for MorphoSource.

# read in DBD_file_manifest.csv as a list of dicts where each row is a dict

import csv
#msMetadata = csv.DictReader(open("UMMZ-ms/DBD_file_manifest.csv"))
with open('Phase1-MorphoSource_file_manifest_filename.csv') as f:
    msMetadata = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

#print(msMetadata)
# read in batch_ummz_import_report_4MS.csv match each row to dict to fill in empty fields
with open("20240402152956-prod-batch_ummz_import_report_4MS.csv") as dbdf:
    dbdInfo = [{k: v for k, v in row.items()}
        for row in csv.DictReader(dbdf, skipinitialspace=True)]

fn_fid = dict()

msFilePath = "MorphoSource_file_manifest_doi.csv"
with open(msFilePath, mode='w', encoding='utf8', newline='') as csv_file:
    fieldnames = ["file_name", "file_url", "ms_id", "media_type", "ingestable", "parent_file_name", "parent_file_url", "parent_ms_id", "parent_identifier", "media.identifier", "occurrence_id", "institution_code", "collection_code", "catalog_number", "scandate", "device_model", "device_manufacturer", "device_modality", "device_description", "device_organization_name", "x_spacing", "y_spacing", "z_spacing",  "unit", "number_of_images_in_set", "processing_activity_type", "creator", "part", "license", "media_ct_series_type", "media_ct_number_of_images_in_set"]
    #fieldnames = ["file_name", "media.media_file", "media.preview_file", "ms_id", "media.media_type", "media.raw_or_derived", "media.parent_file", "parent_file_url", "parent_ms_id", "media.identifier", "occurrence_id", "institution_code", "collection_code", "catalog_number", "scandate", "device_model", "device_manufacturer", "device_modality", "device_description", "device_organization_name", "x_spacing", "y_spacing", "z_spacing",  "unit", "number_of_images_in_set", "processing_activity_type", "creator", "part", "license", "media_ct_series_type", "media_ct_number_of_images_in_set"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for row in dbdInfo:
    	if row['DOI'] != '':
    		fn_fid['media.identifier'] = row['DOI']
    	else:
    		fn_fid['media.identifier'] = fn_fid['media.identifier']
    	#print(fn_fid['media.identifier'])
    	fn_fid.update({row["File Name"]:row['File Set ID']})
    	
    
    for specimen in msMetadata:
        if specimen["file_name"] in fn_fid.keys():
            #print(fn_fid[specimen["file_name"]])
            specimen['media.identifier'] = fn_fid['media.identifier']
            specimen["file_url"] = 'https://deepblue.lib.umich.edu/data/downloads/' + fn_fid[specimen["file_name"]]
            if specimen["parent_file_name"] in fn_fid.keys():
                specimen["parent_file_url"] = 'https://deepblue.lib.umich.edu/data/downloads/' + fn_fid[specimen["parent_file_name"]]

            writer.writerow(specimen)

