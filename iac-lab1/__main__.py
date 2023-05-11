"""A Python Pulumi program"""

import os
import pulumi
import pulumi_aws as aws
import mimetypes

config = pulumi.Config()  # Get the config file
site_dir = config.require("site_dir")  # Get the site directory

bucket = aws.s3.Bucket("my-bucket",
                       website={
                           "index_document": "index.html"
                       })  # Create an AWS resource (S3 Bucket)

for file in os.listdir(site_dir):  # Iterate over the files in the directory
    filepath = os.path.join(site_dir, file)  # Get the path to the file
    mime_type, _ = mimetypes.guess_type(filepath)  # Get the MIME type
    bucket_object = aws.s3.BucketObject(
        file,  # Create an object in the bucket
        bucket=bucket.bucket,  # Name of the bucket
        source=pulumi.FileAsset(filepath),  # Upload the file to the bucket
        acl="public-read",  # Allow read access to the object
        content_type=mime_type
    )  # Upload a file to the bucket

pulumi.export("bucket_name", bucket.bucket)  # Export the name of the bucket
pulumi.export("bucket_endpoint", pulumi.Output.concat(
    "http://", bucket.website_endpoint))  # Export the website endpoint
pulumi.export("example_export", "my example export case")
