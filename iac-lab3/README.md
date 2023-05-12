# Infrastructure as Code - Lab 3 (ECS Cluster with Fargate)

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

### Step 1 - Create new pulumi project:

```
pulumi new aws-python
```

### Step 2 - Create virtual enviroment:

```
python3 -m venv venv
```

### Step 3 - Activate virtual enviroment:

```
source venv/bin/activate
```

### Step 4 - Install packages:

```
pip3 install -r requirements.txt
```

### Step 5 - Configure your region

```
pulumi config set aws:region us-east-1
```

### Step 6 - Setup project on _`__main__.py`_ file:

```
"""An AWS Python Pulumi program - ECS Cluster with Fargate"""

import pulumi
import pulumi_aws as aws
import json

cluster = aws.ecs.Cluster("my-cluster")  # Create an ECS cluster

vpc = aws.ec2.get_vpc(default=True)  # Get the default VPC
vpc_subnets = aws.ec2.get_subnet_ids(
    vpc_id=vpc.id)  # Get the default VPC subnets

group = aws.ec2.SecurityGroup(
    "web-security-group",  # Create a security group for our cluster
    vpc_id=vpc.id,  # Use the default VPC
    description="Enable HTTP access",  # Set a description
    ingress=[
        {
            "protocol": "icmp",
            "from_port": 8,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"]
        }
    ]
)

# Load Balancer config
alb = aws.lb.LoadBalancer(
    "app-lb",  # Create a load balancer for our cluster
    internal=False,  # Create an internet-facing load balancer
    security_groups=[group.id],  # Add the security group to the load balancer
    subnets=vpc_subnets.ids,  # Add the subnets to the load balancer
    load_balancer_type="application"  # Set the load balancer type
)

# Target Group config
atg = aws.lb.TargetGroup(
    "app-tg",  # Create a target group
    port=80,  # Port 80 for traffic
    protocol="HTTP",  # HTTP traffic
    target_type="ip",  # IP addresses as targets
    vpc_id=vpc.id  # Use the default VPC
)

# Listener config
awl = aws.lb.Listener(
    "web-listener",  # Create a listener for our load balancer
    load_balancer_arn=alb.arn,  # Reference the load balancer ARN
    port=80,  # Traffic from port 80
    default_actions=[{  # Default action is to route traffic to the target group
        "type": "forward",
        "target_group_arn": atg.arn
    }]
)

# Task Execution Role config
role = aws.iam.Role(
    "task-execution-role",  # Create a task execution role
    assume_role_policy=json.dumps({
        "Version": "2008-10-17",
        "Statement": [{
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    })
)

# Attach a policy to the role
rpa = aws.iam.RolePolicyAttachment(
    "task-execution-policy",  # Attach a policy to the role
    role=role.name,  # Reference the role name
    # Use an AWS managed policy
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
)

# Task Definition config
task_definition = aws.ecs.TaskDefinition(
    "app-task",  # Create a task definition
    family="fargate-app-task",  # Set a name for the task definition
    cpu="256",  # 256 CPU units
    memory="512",  # 512MB of memory
    network_mode="awsvpc",  # Use the awsvpc network mode
    requires_compatibilities=["FARGATE"],  # Use the Fargate launch type
    execution_role_arn=role.arn,  # Use the task execution role
    container_definitions=json.dumps([{
        "name": "app",  # Set a name for the container
        "image": "nginx",  # Use the latest stable Alpine image
        # "image": "nginx:stable-alpine3.17",  # Use the latest stable Alpine image
        "portMappings": [{  # Map port 80 in the container to port 80 on the host
            "containerPort": 80,
            "hostPort": 80,
            "protocol": "tcp"
        }],
        # "essential": True,  # This container is essential to the task
        # "memory": 512,  # 512MB of memory for the container
        # "cpu": 256,  # 256 CPU units for the container
        # "logConfiguration": {  # Configure logging
        #     "logDriver": "awslogs",
        #     "options": {
        #         "awslogs-group": "ecs-tasks",  # Create a log group
        #         "awslogs-region": aws.config.region,  # Use the region
        #         "awslogs-stream-prefix": "app"  # Set a prefix for the log streams
        #     }
        # }
    }])
)

# Service config
service = aws.ecs.Service(
    "app-svc",  # Create a service
    cluster=cluster.arn,  # Add the cluster ARN
    desired_count=3,  # Number of tasks to run (3 instances)
    launch_type="FARGATE",  # Use the Fargate launch type
    task_definition=task_definition.arn,  # Add the task definition ARN
    network_configuration={  # Use the network configuration
        "subnets": vpc_subnets.ids,  # Add the subnets to the network configuration
        "assign_public_ip": True,  # Assign a public IP address to the task
        # Add the security group to the network configuration
        "security_groups": [group.id]
    },
    load_balancers=[{  # Add the load balancer to the service
        "target_group_arn": atg.arn,  # Add the target group ARN
        "container_name": "app",  # Add the container name
        "container_port": 80  # Add the container port
    }],
    # Wait for the listener to be created
    opts=pulumi.ResourceOptions(depends_on=[awl])
)

# Export the URL
pulumi.export("url", alb.dns_name)
```

### Step 7 - Deploy to pulumi & aws (Dev):

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
