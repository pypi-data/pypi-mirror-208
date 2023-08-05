import json
import pandas as pd
import re
import xlsxwriter
from opsrampcli.opsrampenv import OpsRampEnv
import sys

RESOURCE_FILE_REQUIRED_FIELDS = ['client.uniqueId', 'client.name','resourceName','resourceType']

def assign_via_flattened_attribute_name(orig_object:dict, flatattr_name:str, value):
    if not orig_object:
        orig_object = {}

    if flatattr_name.startswith('tags.'):
        tagname = flatattr_name.split('.')[1]
        if 'tags' not in orig_object:
            orig_object['tags'] = []
        tag = {
                "name": tagname,
                "value": value,
                "metricLabel": False,
                "scope": "CLIENT"
        }
        orig_object['tags'].append(tag)
        return orig_object

    if flatattr_name.find('.') < 0:
        orig_object[flatattr_name] = value
        return orig_object
    
    attr_elements = flatattr_name.split('.')
    attrname = attr_elements.pop(0)
    if attrname in orig_object:
        subobject = orig_object[attrname]
    else:
        subobject = None
    orig_object[attrname] =  assign_via_flattened_attribute_name(subobject, ".".join(attr_elements), value)
    return orig_object






def do_cmd_import_resources(ops: OpsRampEnv, args):

    customattrs = ops.get_objects(obtype="customAttributes")
    if 'code' in customattrs:
        print("Error encountered retrieving custom attributes: %s" % customattrs)
        raise    

    attrinfo = {}
    for attr in customattrs:
        attrname = attr['name']
        attrinfo[attrname] = {}
        attrinfo[attrname]['id'] = attr['id']
        attrinfo[attrname]['client_id'] = attr['organization']['uniqueId']
        attrinfo[attrname]['values'] = {}
        if 'customAttributeValues' not in attr:
            attr['customAttributeValues'] = []
        for value in attr['customAttributeValues']:
            attrinfo[attrname]['values'][value['value']] = value['id']

    filename = args.filename
    if not re.match(".*\.xlsx$", filename):
        filename = filename + ".xlsx"

    df =  pd.read_excel(io=filename, engine="openpyxl", dtype=str)

    for required_col in RESOURCE_FILE_REQUIRED_FIELDS:
        if required_col not in set(df.columns):
            errors.append('Required column "' + required_col + '" is missing from the spreadsheet.')
            continue
        if (len(df[df[required_col] == '']) > 0) or (len(df[pd.isna(df[required_col])]) > 0):
            errors.append('Column "' + required_col + '" has blank values which is not permitted.')
        if required_col=='name' and df['name'].duplicated().any():
            errors.append('Column "name" has duplicate values which is not permitted.')

    resources = ops.get_objects(obtype="resources", queryString=None, countonly=False)
    if 'code' in resources:
        print("Error encountered retrieving resources: %s" % resources)
        raise    

    existing_resources_by_type_name = {}
    existing_resources_by_id = {}
    for resource in resources:
        existing_resources_by_id[resource['id']] = resource
        if resource['resourceType'] not in existing_resources_by_type_name:
            existing_resources_by_type_name[resource['resourceType']] = {}
        existing_resources_by_type_name[resource['resourceType']][resource['name']] = resource


    errors = []
    vals_to_add = {}
    customattr_names_in_file = []
    for columnhead in df.columns:
        df[columnhead] = df[columnhead].str.strip()
        if columnhead.startswith('tags.'):
            column = columnhead.split('.')[1]
            customattr_names_in_file.append(column)
        else:
            continue
        if column not in attrinfo:
            errors.append(f'Column header tags.{column} indicates a non-existent custom attribute name of {column} for the specified client.  Please create this custom attribute name in the OpsRamp UI first.' )
        else:
            for val in df[columnhead].unique():
                if pd.notna(val) and val != "" and str(val) not in attrinfo[column]['values']:
                    if args.addvalues:
                        strval = str(val)
                        if column not in vals_to_add:
                            vals_to_add[column] = []
                        vals_to_add[column].append(strval)
                    else:
                        errors.append('Value "' + str(val) + '" specified for custom attribute "' + column + '" is not a valid value.')

    if len(errors) > 0:
        print("\nErrors exist in the spreadsheet.  No updates to the platform have been made, please correct these errors before commiting:\n")
        for i,error in enumerate(errors):
            print("%s  %s" % (str(i+1).rjust(5),error))
        print("\nIf you want to auto-add new custom attr value definitions on the fly, use the --addvalues option otherwise undefined values will be treated as an error.\n")
        sys.exit(1)

    elif not args.commit:
        print("No errors were found in the spreadsheet.  To apply the changes to the platform, rerun the command with the --commit option added.")
        sys.exit(0)


    updateresults = {
        "updatesuccess": 0,
        "updatefail": 0,
        "updatenotneeded": 0,
        "clearskipped": 0,
        "clearsuccess": 0,
        "clearfail": 0,
        "rawresults": [],
        "errors": []
    }
    

    for column in vals_to_add.keys():
        newvalsarray = []
        for val in vals_to_add[column]:
            newvalsarray.append(val)
        newvals = ops.add_custom_attr_value(attrinfo[column]['id'], newvalsarray)
        for i,valobj in enumerate(newvals['customAttributeValues']):
            attrinfo[column]['values'][valobj['value']] = valobj['id']

    for idx,resource in df.iterrows():

        # See if it is a new resource or already existing
        if resource['resourceType'] in existing_resources_by_type_name and resource['resourceName'] in existing_resources_by_type_name[resource['resourceType']]:
            resourceId = existing_resources_by_type_name[resource['resourceType']][resource['resourceName']]['id']
            is_new = False
        else:
            is_new = True

        # Handle delete action if specified
        if not is_new and 'Processing Action' in resource and resource['Processing Action'] == 'Delete':
            response = ops.delete_resource(resourceId)
            print(f'Deleted resource name:{resource["resourceName"]} with id:{resourceId}')

        # Build the resource create/update payload
        resource_dict = {}
        for columnhead in df.columns:
            if columnhead.startswith('tags.'):
                column = columnhead.split('.')[1]
            else:
                column = columnhead
            resource_dict = assign_via_flattened_attribute_name(resource_dict, columnhead, resource[columnhead])
        if is_new:
            response = ops.create_resource(resource_dict)
            if 'resourceUUID' in response:
                resourceId = response['resourceUUID']
                print(f'Created resource name:{resource_dict["resourceName"]} with id:{resourceId}')
            else:
                print(f'ERROR - Unable to create resource {resource_dict["resourceName"]}.  Please check the data for this item.')
                continue
        else:
            response = ops.update_resource(resourceId, resource_dict)
            if 'success' in response and response['success']:
                print(f'Updated resource name:{resource_dict["resourceName"]} with id:{resourceId}')
            else:
                print(f'ERROR - Unable to update resource {resource_dict["resourceName"]} - {response["message"]}.  Please check the data for this item.')
                continue                


        for attrname in customattr_names_in_file:
            columnhead = f'tags.{attrname}'
            if pd.isnull(resource[columnhead]) or pd.isna(resource[columnhead]) or resource[columnhead]=='' :
                if args.writeblanks:
                    if is_new:
                        continue
                    if "tags" in existing_resources_by_id[resourceId] and any(attr['name']==column for attr in existing_resources_by_id[resourceId]['tags']):
                        # There are one or more values and we need to remove it/them
                        remove_values = [obj['value'] for obj in existing_resources_by_id[resourceId]['tags'] if obj['name'] == column]
                        for remove_value in remove_values:
                            ops.unset_custom_attr_on_devices(attrinfo[attrname]['id'], attrinfo[attrname]['values'][remove_value], resourceId)
                        updateresults['clearsuccess'] +=1
                    else:
                        # There is already no value so nothing to remove
                        updateresults['clearskipped'] +=1
                else:
                    updateresults['clearskipped'] +=1
                    continue
            elif not is_new and "tags" in existing_resources_by_id[resourceId] and any(attr['name']==column and attr['value']==resource[columnhead] for attr in existing_resources_by_id[resourceId]['tags']):
                # It already has the same value for this attr, no need to update
                updateresults['rawresults'].append({
                    "rownum": idx+1,
                    "resourceid": resourceId,
                    "attr_name": column,
                    "attr_value": resource[columnhead],
                    "attr_id": attrinfo[attrname]['id'],
                    "attr_value_id": attrinfo[attrname]['values'][resource[columnhead]],
                    "action": "update not needed"
                })
                updateresults['updatenotneeded'] +=1
                continue
            else:
                # It has no value or a different value for this attr so we need to update
                result = ops.set_custom_attr_on_devices(attrinfo[attrname]['id'], attrinfo[attrname]['values'][str(resource[columnhead])], resourceId)
                updateresults['rawresults'].append({
                    "rownum": idx+1,
                    "resourceid": resourceId,
                    "attr_name": column,
                    "attr_value": resource[columnhead],
                    "attr_id": attrinfo[attrname]['id'],
                    "attr_value_id": attrinfo[attrname]['values'][str(resource[columnhead])],
                    "action": "updated"
                })
                if result['successCount'] == 1:
                    updateresults['updatesuccess'] +=1
                else:
                    updateresults['updatefail'] +=1
                    updateresults['errors'].append({
                        "rownum": idx+1,
                        "resourceid": resourceId,
                        "attr_name": column,
                        "attr_value": resource[columnhead],
                        "attr_id": attrinfo[attrname]['id'],
                        "attr_value_id": attrinfo[attrname]['values'][str(resource[columnhead])],
                        "action": "updatefail",
                        "response": result
                    })             
    
    print("done") 

def do_cmd_get_resources(ops,args):
    if args.search:
        result = ops.get_objects(obtype="resourcesNewSearch", searchQuery=args.search, countonly=args.count)
    else:
        result = ops.get_objects(obtype="resources", queryString=args.query, countonly=args.count)

    if args.delete:
        confirm_delete = 'NO'
        confirm_delete = input(f'This will result in the deletion of {len(result)} resources.  Enter YES (upper case) to confirm deletion or enter anything else to just print a list of the resources that would be deleted: ')
    
        if confirm_delete == 'YES':
            for (idx, resource) in enumerate(result):
                print(f'Deleting resource #{idx+1} - {resource["name"]} ({resource["resourceType"]}) with uniqueId {resource["id"]}')
                try:
                    print(ops.delete_resource(resource['id']))
                except Exception as e:
                    print(e)
        else:
            return result

    elif args.manage:
        confirm_manage = 'NO'
        confirm_manage = input(f'This will result in managing {len(result)} resources.  Enter YES (upper case) to confirm or enter anything else to just print a list of the resources that would be managed: ')
    
        if confirm_manage == 'YES':
            for (idx, resource) in enumerate(result):
                print(f'Managing resource #{idx+1} - {resource["name"]}')
                try:
                    print(ops.do_resource_action("manage", resource['id']))
                except Exception as e:
                    print(e)

        else:
            return result      


    else:
         return result

