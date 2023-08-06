import boto3
import botocore
import os
import sys
import yaml

class Functions:
    """ Helper functions for interacting with AWS"""


    def parse_yaml(file):
        """Exposes configuration YAML file

        Args:
            file (.yml): Config

        Returns:
            dict: access like yml_filename['aws']['our_bucket'] 
        """
        try: 
            with open(file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f'{e}\nDid you create the config file described in the README?')
            sys.exit(1)


    def connect_to_s3():
        """Connect to S3 resource using boto3

        Returns:
            boto3 resource: boto3 S3 resource
        """
        try:
            return boto3.resource("s3")
        except Exception as e:
            print(f"Can't connect to S3. Error: {e}")
            sys.exit(1)

    def assure_s3_bucket(s3, bckt):
        """Check if bucket exists and create if not

        Args:
            s3 (boto3 resource): boto3 S3 resource
            bckt (S3 bucket): S3 bucket
        """
        try:
            s3.meta.client.head_bucket(Bucket = bckt)
            print('Specified bucket exists')
        except botocore.exceptions.ClientError as e:
            print(f'Error code: {e}')
            if e.response["Error"]["Code"] == "404":
                print ('Bucket failed head_bucket() call, likely does not exist')
                s3.create_bucket(Bucket = bckt)
                print(f'Created {bckt}')


    def diff_bucket_objs(s3, bucket_1, prefix_1, bucket_2, prefix_2):
        """Identifies the objects in bucket_1 that are not in bucket_2

        Args:
            s3 (boto3 resource): boto3 S3 resource
            bucket_1 (S3 bucket): 1st S3 bucket
            prefix_1 (String): prefix for objects in bucket 1
            bucket_2 (S3 bucket): 2nd S3 bucket
            prefix_2 (String): prefix for objects in bucket 2

        Returns:
            set: diff in bucket contents
        """
        # Define lists of each bucket's keys minus any prefixes and file names
        get_filename = lambda key: os.path.splitext(os.path.basename(key))[0]
        bucket_1_keys = set(get_filename(obj.key) for obj in s3.Bucket(bucket_1).objects.filter(Prefix=prefix_1))
        bucket_2_keys = set(get_filename(obj.key) for obj in s3.Bucket(bucket_2).objects.filter(Prefix=prefix_2))
        dif = bucket_1_keys.difference(bucket_2_keys)
        print(f'There were {len(dif)} objects missing')
        return dif


    def copy_over_all_objects(s3, source, source_prefix, dest, dest_prefix):
        """Copy all prefixed objects from AWS S3 bucket to another

        Args:
            s3 (boto3 resource): boto3 S3 resource
            source (S3 bucket): source S3 bucket
            source_prefix (String): prefix for objects in source
            dest (S3 bucket): destination S3 bucket
            dest_prefix (String): prefix for objects in destination
        """
        missing_keys = diff_bucket_objs(s3, source, source_prefix, dest, dest_prefix)
        ct = 0
        for key in missing_keys:
            key_dict = {'Bucket' : source, 'Key': f'{source_prefix}{key}'}
            s3.Bucket(dest).copy(key_dict, f'{dest_prefix}{key}')
            print (f'Copied over: {key}')
            ct += 1
        print (f'Extraction complete, {dest_prefix} folder on destination bucket updated. {ct} objects copied over.')