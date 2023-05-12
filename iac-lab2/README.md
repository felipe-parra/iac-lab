# Infrastructure as Code - Lab 2 (EC2 Instances)

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
pulumi new aws-python -y
```

### Step 2 - Create virtual enviroment:

```
python3 -m venv venv
```

### Step 3 - Activate virtual enviroment:

```
source venv/bin/activate
```

### Step 4 - Install packages from `requirements.txt`:

```
pip3 install -r requirements.txt
```

### Step 5 - Setup project on _`__main__.py`_ file:

```
"""A Python Pulumi program"""
from pulumi import export
import pulumi_aws as aws

ami = aws.ec2.get_ami(
    most_recent=True, # Get the latest image
    owners=["137112412989"], # Amazon
    filters=[{"name": "name", "values": ["amzn-ami-hvm-*-x86_64-ebs"]}] # Filter by AMI name
)

group = aws.ec2.SecurityGroup(
    "web-secgrp", # Name of the security group
    description='Enable HTTP access', # Description of the security group
    ingress=[
        {
            'protocol': 'icmp', # ICMP is the protocol that ping uses
            'from_port': 8, # Enable ping
            'to_port': 0, # Enable ping
            'cidr_blocks': ['0.0.0.0/0'] # Specify from where the ping can come from
        },
        {
            'protocol': 'tcp', # TCP is the protocol type used for HTTP traffic
            'from_port': 80, # HTTP uses port 80
            'to_port': 80, # HTTP uses port 80
            'cidr_blocks': ['0.0.0.0/0'] # Specify from where the HTTP traffic can come from
        },
    ],
    egress=[
        {
            'protocol': 'tcp',
            'from_port': 80,
            'to_port': 80,
            'cidr_blocks': ['0.0.0.0/0']
        },
    ]
)

default_vpc = aws.ec2.get_vpc(default="true")
default_vpc_subnets = aws.ec2.get_subnet_ids(vpc_id=default_vpc.id)

lb = aws.lb.LoadBalancer("external-loadbalancer",
                         internal="false",
                         security_groups=[group.id],
                         subnets=default_vpc_subnets.ids,
                         load_balancer_type="application",
                         )

target_group = aws.lb.TargetGroup("target-group",
                                  port=80,
                                  protocol="HTTP",
                                  target_type="ip",
                                  vpc_id=default_vpc.id
                                  )

listener = aws.lb.Listener("listener",
                           load_balancer_arn=lb.arn,
                           port=80,
                           default_actions=[{
                               "type": "forward",
                               "target_group_arn": target_group.arn
                           }]
                           )

ips = []
hostnames = []
for az in aws.get_availability_zones().names:
    server = aws.ec2.Instance(f'web-server-{az}',
                              instance_type="t2.micro",
                              vpc_security_group_ids=[group.id],
                              ami=ami.id,
                              user_data="""#!/bin/bash
echo \"Hello, World -- from {}!\" > index.html
nohup python -m SimpleHTTPServer 80 &
""".format(az),
        availability_zone=az,
        tags={
            "Name": "web-server",
                              },
    )
    ips.append(server.public_ip)
    hostnames.append(server.public_dns)

    attachment = aws.lb.TargetGroupAttachment(
        f'web-server-{az}',
        target_group_arn=target_group.arn,
        target_id=server.private_ip,
        port=80,
    )

export('ips', ips)
export('hostnames', hostnames)
export("url", lb.dns_name)
```

### Step 6 - Deploy to pulumi & aws :

```
pulumi up
```

### Optional - Delete resources in the stack:

```
pulumi destroy
```

### Optional - Delete the history and configuration associated with the stack:

```
pulumi stack rm dev
```

### Optional - Select an specific stack & choose:

```
pulumi stack select
```
