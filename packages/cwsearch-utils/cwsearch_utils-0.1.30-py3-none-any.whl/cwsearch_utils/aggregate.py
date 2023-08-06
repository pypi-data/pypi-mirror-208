import os
import json
import tempfile
import datetime
from arnparse import arnparse
from cwsearch_utils import infinstor_lock, infinstor_dbutils
import sqlite3
from typing import List

def my_sort_fnx(a):
    return a[0]

def my_filelisting_sort_fnx(a):
    return a[2]

def get_files_list_one_group(s3client, bucket, prefix, olg, resources, rv:List[List[str]]):
    """
    get all files in s3://<bucket>/<prefix + olg> that is a super string of an entry in 'resources', if resources is specified.  If not, return all files in s3://<bucket>/<prefix>.

    Args:
        s3client (_type_): _description_
        
        bucket (_type_): _description_
        
        prefix (_type_): cwsearch cache bucket prefix under which all cwsearch data is stored
        
        olg (_type_): one log group; log group name with '/' replaced with '_'
        
        resources (List[str]): List of resource ARNs 
        
        rv (List[List[str]]): return value; List of List[name_of_file in the bucket (including the prefix), size, last_modified']
    """
    # get_files_list_one_group: Entered. prefix=index2/, group=None, resources=['arn:aws:apigateway:us-east-1::/domainnames/api.isstage8.com', 'arn:aws:apigateway:us-east-1::/restapis/x7ja5rzq90/stages/Prod', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30-getinfinstorversion-yRD9rzBQDoPy', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-M-executedag-tMColaCQlIg6', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPM-objectstoreevent-mJAaeTZHNvc4', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-M-runproject-92tuid9CKtBh', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-infinauth-wFJOHuebuVnS', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-MLflo-router-jFbERCi8NrOG', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3-ListObjectsV2Function-nHJ6ECCBOkon', 'arn:aws:apigateway:us-east-1::/restapis/x7ja5rzq90', 'arn:aws:apigateway:us-east-1::/restapis/moavtyu662/stages/Prod', 'arn:aws:cloudformation:us-east-1:687391518391:stack/infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-MLflowService-WWZFG8OOZ1AB/60ed4a20-bb8d-11ed-8a2b-0ef6bc9ed83f', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3CZKD4M-WebhdfsFunction-dkq0d0tMCAGe', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3C-CloudHandlerFunction-4MOL4nHQdDXn', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboar-NewSubscriptionHandlerFu-aKw79V6zweVi', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3CZKD4M7-RouterFunction-VB6ATGsxNyej', 'arn:aws:apigateway:us-east-1::/domainnames/mlflow.isstage8.com', 'arn:aws:cloudformation:us-east-1:687391518391:stack/infinstor-mlflow-dashboard-3CZKD4M755AW-InfinStorDashboard-1FC6UTZ5SCDCD/62048680-bb8d-11ed-87b1-0a8057042631', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-S3EventsHandlerFunction-i7bwYnBGnLlf', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30V-cliclientauthorize-i0tEwOAxGre3', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-periodrun-ok9uuam34Iw2', 'arn:aws:apigateway:us-east-1::/restapis/moavtyu662', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-createrun-eRo1ijdWfM8S', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3-getlambdaconfiguration-omZbY05qXJCD', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMP-settaggroupsalt-m1gcwfwazMd1']
    print(f"get_files_list_one_group: Entered. prefix={prefix}, group={olg}, resources={resources}")
    if olg:
        prefix = prefix + olg
    nextContinuationToken = None
    while True:
        if nextContinuationToken:
            resp = s3client.list_objects_v2(Bucket=bucket, Delimiter='/', Prefix=prefix, ContinuationToken=nextContinuationToken)
        else:
            resp = s3client.list_objects_v2(Bucket=bucket, Delimiter='/', Prefix=prefix)
        if 'Contents' in resp:
            for one in resp['Contents']:
                nm = one['Key']
                if not nm[-1] == '/':
                    if resources:
                        for res in resources:
                            arn = arnparse(res)
                            munged_resource_id = arn.resource.replace('/', '_')
                            if munged_resource_id in nm:
                                print(f"get_files_list_one_group: Adding. munged_resource_id={munged_resource_id}, nm={nm}")
                                rv.append([nm, one['Size'], one['LastModified']])
                            else:
                                print(f"get_files_list_one_group: Skipping. munged_resource_id={munged_resource_id}, nm={nm}")
                    else:
                        rv.append([nm, one['Size'], one['LastModified']])
        if not resp['IsTruncated']:
            break
        else:
            nextContinuationToken = resp['NextContinuationToken']

def resources_for_tag(resources, tag) -> List[str]:
    """
    return the 'resources' that match the specified 'tag'.  See 'returns' below

    Args:
        resources (_type_): resource_tag_mapping_list.json contents.
                [
                    {
                        "ResourceARN": "arn:aws:apigateway:us-east-1::/domainnames/api.isstage8.com",
                        "Tags": [
                            {
                                "Key": "serverlessrepo:semanticVersion",
                                "Value": "2.0.58"
                            },
                            {
                                "Key": "lambda:createdBy",
                                "Value": "SAM"
                            },
                            .
                            .
                    },
                .
                    .
                ]        
        tag (str): format is tag_name=tag_value

    Returns:
        List[str]: list of resource_arns for the specified tag.
    """
    retval = []
    if tag == 'notag':
        for res in resources:
            retval.append(res['ResourceARN'])
        print(f"resources_for_tag: tag={tag}, rv={retval}")
        return retval
    else:
        ind = tag.find('=')
        if ind == -1:
            print('resources_for_tag: tag does not have = ???')
            return None
        tagkey = tag[:ind]
        tagval = tag[ind+1:]
        # [
        #     {
        #         "ResourceARN": "arn:aws:apigateway:us-east-1::/domainnames/api.isstage8.com",
        #         "Tags": [
        #             {
        #                 "Key": "serverlessrepo:semanticVersion",
        #                 "Value": "2.0.58"
        #             },
        #             {
        #                 "Key": "lambda:createdBy",
        #                 "Value": "SAM"
        #             },
        #             .
        #             .
        #     },
        #     .
        #     .
        # ]        
        for res in resources:
            for tg in res['Tags']:
                if tg['Key'] == tagkey:
                    retval.append(res['ResourceARN'])
        # resources_for_tag: tag=serverlessrepo:applicationId=arn:aws:serverlessrepo:us-east-1:986605205451:applications/InfinStor-Dashboard-Lambdas, rv=['arn:aws:apigateway:us-east-1::/domainnames/api.isstage8.com', 'arn:aws:apigateway:us-east-1::/restapis/x7ja5rzq90/stages/Prod', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30-getinfinstorversion-yRD9rzBQDoPy', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-M-executedag-tMColaCQlIg6', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPM-objectstoreevent-mJAaeTZHNvc4', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-M-runproject-92tuid9CKtBh', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-infinauth-wFJOHuebuVnS', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-MLflo-router-jFbERCi8NrOG', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3-ListObjectsV2Function-nHJ6ECCBOkon', 'arn:aws:apigateway:us-east-1::/restapis/x7ja5rzq90', 'arn:aws:apigateway:us-east-1::/restapis/moavtyu662/stages/Prod', 'arn:aws:cloudformation:us-east-1:687391518391:stack/infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-MLflowService-WWZFG8OOZ1AB/60ed4a20-bb8d-11ed-8a2b-0ef6bc9ed83f', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3CZKD4M-WebhdfsFunction-dkq0d0tMCAGe', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3C-CloudHandlerFunction-4MOL4nHQdDXn', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboar-NewSubscriptionHandlerFu-aKw79V6zweVi', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-3CZKD4M7-RouterFunction-VB6ATGsxNyej', 'arn:aws:apigateway:us-east-1::/domainnames/mlflow.isstage8.com', 'arn:aws:cloudformation:us-east-1:687391518391:stack/infinstor-mlflow-dashboard-3CZKD4M755AW-InfinStorDashboard-1FC6UTZ5SCDCD/62048680-bb8d-11ed-87b1-0a8057042631', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-dashboard-S3EventsHandlerFunction-i7bwYnBGnLlf', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30V-cliclientauthorize-i0tEwOAxGre3', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-periodrun-ok9uuam34Iw2', 'arn:aws:apigateway:us-east-1::/restapis/moavtyu662', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMPY4Q-ML-createrun-eRo1ijdWfM8S', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3-getlambdaconfiguration-omZbY05qXJCD', 'arn:aws:lambda:us-east-1:687391518391:function:infinstor-mlflow-mlflow-1N3Y30VPMP-settaggroupsalt-m1gcwfwazMd1']
        print(f"resources_for_tag: tag={tag}, rv={retval}")
        return retval

def get_files_list(s3client, bucket, prefix, log_groups, tag, resources) -> List[List[str]]:
    """
    either 'log_groups' or 'tag' can be specified.
    
    for the given 'tag', get the list of resources for the 'tag'. For each 'resource', get the corresponding munged log group (replace '/' with '_') and read the correspoding file from s3://<bucket>/<prefix> that is a super string of this log group name (usually a .db file) 
    
    for the given 'log_groups', for each log_group_name, get the corresponding munged log group name (replace '/' with '_') and then read corresponding file from s3://<bucket>/<prefix + munged_log_group_name>.  This filename is a super string of the specified prefix (usually a .db file)

    Args:
        s3client (_type_): an infinslice scoped s3client
        
        bucket (_type_): cwsearch cache bucket
        
        prefix (_type_): prefix in the cwsearch cache bucket under which all cwsearch content is stored
        
        log_groups (_type_): list of log group ARNs.  comma separated. see description above.
        
        tag (str): format is tag_name=tag_value.  see description above.
        
        resources (dict): resource_tag_mapping_list.json contents

    Returns:
        (List[List[str]]): List of List[name_of_file in the bucket (including the prefix), size, last_modified']
    """
    rv:List[List[str]] = []
    if log_groups:
        lga:List = log_groups.split(',')  # lga == log groups all ???
        for olg in lga:   # olg == one log group
            get_files_list_one_group(s3client, bucket, prefix, olg.replace('/', '_'), None, rv)
    elif tag:
        rft:List[str] = resources_for_tag(resources, tag)
        if rft:
            get_files_list_one_group(s3client, bucket, prefix, None, rft, rv)
        else:
            print(f"tag specified={tag}, but could not get resources for tag. Ignoring tag..")
            get_files_list_one_group(s3client, bucket, prefix, None, None, rv)
    else:
        get_files_list_one_group(s3client, bucket, prefix, None, None, rv)
    rv.sort(reverse=True, key=my_filelisting_sort_fnx)
    # get_files_list: log_groups=None, tag=serverlessrepo:applicationId=arn:aws:serverlessrepo:us-east-1:986605205451:applications/InfinStor-Dashboard-Lambdas, rv=[['index2/_aws_lambda_infinstor-mlflow-dashboard-3CZKD4M7-RouterFunction-VB6ATGsxNyej-2023_04_24_[$LATEST]ea3d9049f53f4d65950e9ad080e33b03-1682310918000.db', 12288, datetime.datetime(2023, 4, 24, 4, 49, 18, 8000)]]
    print(f"get_files_list: log_groups={log_groups}, tag={tag}, rv={rv}")
    return rv

def process_file(client, bucket, key:str, dstcon:sqlite3.Connection, infinstor_time_spec, tag) -> bool:
    """
    Read the source .db file specified by 'key'. copy contents into 'dstcon' destination .db file for the specified 'tag'

    Args:
        client (_type_): S3Client
        bucket (_type_): _description_
        key (str): source .db file name
        dstcon (sqlite3.Connection): sqllite3 connection for destination .db file
        infinstor_time_spec (_type_): _description_
        tag (_type_): _description_

    Returns:
        bool: _description_
    """
    if tag:
        use_tag=tag
    else:
        use_tag='notag'
    try:
        dstcur = dstcon.cursor()

        dnm = os.path.join('/tmp', key[key.rindex('/') + 1:])
        print(f"Downloading object {key} to local file {dnm}")
        client.download_file(bucket, key, dnm)

        srccon = sqlite3.connect(dnm)
        srccur = srccon.cursor()
        res = srccur.execute(f"SELECT name, timestamp, link, msg FROM links WHERE tag='{use_tag}'")
        while True:
            one_entry = res.fetchone()
            if not one_entry:
                break
            name = one_entry[0]
            estr = f"INSERT INTO links VALUES ('{use_tag}', '{one_entry[0]}', '{one_entry[1]}', '{one_entry[2]}', '{one_entry[3]}')"
            dstcur.execute(estr)
        dstcon.commit()
        os.remove(dnm)
        return True
    except Exception as e:
        print(f"Caught {e} while downloading {key} from bucket {bucket}. Ignoring and trying next object..")
    return False

def populate_names(bucket, prefix, infinstor_time_spec, resources, log_groups, tag, max_size_allowed=None, max_time_allowed=None) -> bool:
    """
    generates the aggreated .db files: <prefix>/<infinslice_time_spec>/names-<tag_name=tag_value>.db and <prefix>/<infinslice_time_spec>/names.db

    Args:
        bucket (_type_): the cwsearch cache/state bucket
        prefix (_type_): the <prefix> under the cwsearch cache bucket, where all cwsearch data is stored.  specified during run of MLproject
        infinstor_time_spec (_type_): _description_
        resources (_type_): resource_tag_mapping_list.json contents
        log_groups (_type_): comma separated list of log_group ARNs; either 'log_groups' or 'tag' is specified ???
        tag ( str ): tag_name=tag_group; either 'log_groups' or 'tag' is specified  ???

    Returns:
        bool : True on success; False on failure
    """
    # populate_names: Entered. bucket=cwsearch-pandi-isstage12-isstage8, prefix=index2, infinstor_time_spec=tm20230423120000-tm20230424120000, log_groups=None, tag=serverlessrepo:applicationId=arn:aws:serverlessrepo:us-east-1:986605205451:applications/InfinStor-Dashboard-Lambdas
    print(f'populate_names: Entered. bucket={bucket}, prefix={prefix}, infinstor_time_spec={infinstor_time_spec}, log_groups={log_groups}, tag={tag}')
    start_time = datetime.datetime.utcnow()

    prefix = prefix.rstrip('/') + '/'

    import boto3
    # first list files in reverse chrono order
    try:
        s3client = boto3.client('s3', infinstor_time_spec=infinstor_time_spec)
        files = get_files_list(s3client, bucket, prefix, log_groups, tag, resources)
    except Exception as ex:
        print(f'Caught {ex} while list_objects_v2 of {bucket} prefix {prefix} time {infinstor_time_spec}', flush=True)
        return False

    if not files:
        print(f'No files found. bucket={bucket}, prefix={prefix}, infinstor_time_spec={infinstor_time_spec}, log_groups={log_groups}, tag={tag}')
        return False

    # next, read each file and fill aggregated db
    if tag:
        sluggified = infinstor_dbutils.slugify(tag)
        tfname = f"names-{sluggified}.db"
    else:
        tfname = "names.db"
    tdir = tempfile.mkdtemp()
    tfile = os.path.join(tdir, tfname)
    print(f'populate_names: tdir={tdir}, tfile={tfile}')
    con:sqlite3.Connection = sqlite3.connect(tfile)
    infinstor_dbutils.create_table(con)

    total_sz = 0
    for one_entry in files:
        print(f"Processing file {one_entry[0]} last_modified {one_entry[2]}")
        if process_file(s3client, bucket, one_entry[0], con, infinstor_time_spec, tag):
            total_sz = total_sz + one_entry[1]
        if max_size_allowed and total_sz > max_size_allowed:
            print(f"Stopping after processing files of size {total_sz}")
            break
        else:
            print(f"Continuing after processing {total_sz} bytes")
        tnow = datetime.datetime.utcnow()
        delta = tnow - start_time
        if max_time_allowed and delta.total_seconds() > max_time_allowed:
            print(f"Stopping after working for {delta.total_seconds()} seconds")
            break
        else:
            print(f"Continuing after working for {delta.total_seconds()} seconds")
    con.close()

    # finally, write ner_entites to s3
    object_name = f"{prefix}index/{infinstor_time_spec}/{tfname}"
    try:
        response = s3client.upload_file(tfile, bucket, object_name)
    except Exception as ex:
        print(f"Caught {ex} while uploading names entry for timespec {infinstor_time_spec}. Objectname={object_name}")
    os.remove(tfile)

    return True
