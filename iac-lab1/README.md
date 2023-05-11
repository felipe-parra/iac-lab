# Infrastructure as Code - Lab 1 (S3 Bucket)

## Getting started

- Check if you already have installed aws cli or start with next line
  [AWS Docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

- Check if you already have installed pulumi or start with next line

```
brew install pulumi/tap/pulumi
```

### Step 1 - Create new pulumi project

```
pulumi new python -y
```

### Step 2 - Install pulumi aws package

```
pip3 install pulumi-aws
```

### Step 3 - Configure your region

```
pulumi config set aws:region us-east-1
```

### Step 4 - Create your files (or add your directory) and directory (www)

```
mkdir www
echo "<!DOCTYPE html><html><body>Example Site - Index - IaC Lab</body></html>" > www/index.html
echo "<!DOCTYPE html><html><body>Example Site - About - IaC Lab</body></html>" > www/about.html
```

### Step 5 - Setup project on _`__main__.py`_ file:

```
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
```

### Step 6 - Set site_dir where site it is:

```
pulumi config set iac-lab1:site_dir www
```

### Step 7 - Deploy to pulumi & aws (Dev):

```
pulumi up
```

### Step 8 - Create new stack, (Production):

```
pulumi stack init prod
```

### Step 8 - Set region to new stack(Production):

```
pulumi config set aws:region eu-west-1
```

### Step 9 - Set new site directory (wwwprod) (Production):

```
pulumi config set iac-lab1:site_dir wwwprod
```

### Optional - Delete resources in the stack:

```
pulumi destroy
```

### Optional - Delete the history and configuration associated with the stack:

```
pulumi stack rm prod
```

### Optional - Select an specific stack & choose:

```
pulumi stack select
```
