import json
from multiprocessing import context
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
# from . import consumers 

def index(request):
  template = loader.get_template('index.html')
  return HttpResponse(template.render())

def main(request):
  template = loader.get_template('deployment_service/main.html')
  return HttpResponse(template.render())

def create(request):
  template = loader.get_template('deployment_service/create.html')
  return HttpResponse(template.render())

def UserDash(request):
  template = loader.get_template('deployment_service/UserDash.html')
  return HttpResponse(template.render())

def CreateServer(request):
  template = loader.get_template('deployment_service/create_server.html')
  return HttpResponse(template.render())


def InstallSuccess(request):
        template = loader.get_template('deployment_service/install_success.html')
        return HttpResponse(template.render())

def BuildSuccess(request):
        template = loader.get_template('deployment_service/build_success.html')
        return HttpResponse(template.render())

def success(request):
    if request.method == 'POST':
        return render(request,"deployment_service/install_success.html")
    else:
        return HttpResponse("ERROR!...")

def InstallFail(request):
  template = loader.get_template('deployment_service/install_fail.html')
  return HttpResponse(template.render())

def UserDashreports(request):
  template = loader.get_template('deployment_service/UserDashreports.html')
  return HttpResponse(template.render())

def Userprofile(request):
  template = loader.get_template('deployment_service/userprofile.html')
  return HttpResponse(template.render())

def landing(request):
  template = loader.get_template('deployment_service/land.html')
  return HttpResponse(template.render())

def buildform(request):
  template = loader.get_template('deployment_service/build.html')
  return HttpResponse(template.render())

def prj_deploy(request):
  template = loader.get_template('deployment_service/prj_deployment.html')
  return HttpResponse(template.render())

#Server Creation
import subprocess
from django.shortcuts import render
import paramiko
import datetime
import os
# from django.http import JsonResponse
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def deploy_ec2(request):

    if request.method == 'POST':
        server_name = request.POST.get('server-name')
        os_type = request.POST.get('os-type')  # Assuming 'os_type' is the name attribute of your input field
        
        if not server_name or not os_type:
            return HttpResponse("Server name and OS type are required.", status=400)
        
        # Determine the AMI based on the selected OS type
        if os_type == 'Ubuntu':
            ami = 'ami-080e1f13689e07408'  # Ubuntu 20.04 LTS AMI ID
        elif os_type == 'Amazon Linux':
            ami = 'ami-0a91cd140a1fc148a'  # Amazon Linux AMI ID (example)
        else:
            return HttpResponse("Unsupported OS type")
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Add a timestamp to the configuration file name
        tf_config_filename = f'terraform_{timestamp}.tf'  # Create a unique configuration file name

        # Define a list of regions for each instance
        regions = ["us-east-1"]  # Add more regions as needed

        for idx, region in enumerate(regions):
            # Define the Terraform configuration for each instance
            terraform_config = f"""
            provider "aws" {{
                region     = "{region}"
                access_key = ""
                secret_key = ""
            }}

            resource "aws_key_pair" "my_key_pair_{idx}" {{
                key_name   = "my-key-pair"
                public_key = file("C:/Key Pairs/my-key-pair.pem.pub")  # Path to your public key
            }}

            resource "aws_instance" "example_{idx}" {{
                ami           = "{ami}"
                instance_type = "t2.micro"
                key_name      = aws_key_pair.my_key_pair_{idx}.key_name  # Reference the key pair name here

                user_data = <<-EOF
                #!/bin/bash
                sudo apt-get update -y
                sudo apt-get install -y apache2
                sudo systemctl start apache2
                sudo systemctl enable apache2
                curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
                    /usr/share/keyrings/jenkins-keyring.asc > /dev/null
                echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
                    https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
                    /etc/apt/sources.list.d/jenkins.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y openjdk-17-jdk
                sudo apt-get install -y jenkins
                sudo systemctl start jenkins
                sudo systemctl enable jenkins
                sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
                sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
                sudo apt-get update
                sudo apt-get install -y docker-ce
                sudo usermod -aG docker \$USER
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo apt-get install -y gnupg software-properties-common curl
                curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
                sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
                sudo apt-get update
                sudo apt-get install -y terraform
                sudo apt-get update -y
                sudo apt-get install -y software-properties-common
                sudo add-apt-repository --yes --update ppa:ansible/ansible
                sudo apt-get update -y
                sudo apt-get install -y ansible
                sudo chown jenkins:jenkins /var/www/html/
                sudo chown jenkins:jenkins /var/www/html
                sudo chmod 777 /var/www/html/
                sudo chmod 777 /var/www/html
                EOF

                tags = {{
                    Name = "{server_name}"
                }}
            }}

            resource "aws_security_group" "instance_sg_{idx}" {{
                name        = "instance_sg"
                description = "Security group for the EC2 instance"
                vpc_id      = "vpc-098aba3da65b9810e"  # Specify your VPC ID here

                ingress {{
                    from_port   = 80
                    to_port     = 80
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 443
                    to_port     = 443
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 9090
                    to_port     = 9090
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 3000
                    to_port     = 3000
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 8080
                    to_port     = 8080
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 9090
                    to_port     = 9090
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                ingress {{
                    from_port   = 3000
                    to_port     = 3000
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

                egress {{
                    from_port   = 0
                    to_port     = 65535
                    protocol    = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }}

            }}
            output "instance_ip" {{
                value = aws_instance.example_{idx}.public_ip
            }}
            """

            # Write the Terraform configuration to a file
            with open(tf_config_filename, 'w') as f:
                f.write(terraform_config)

            # Run Terraform commands to initialize and apply the configuration
            subprocess.run(['C:\\terraform\\terraform.exe', 'init'])
            subprocess.run(['C:\\terraform\\terraform.exe', 'apply', '-auto-approve'])

            # Read the Terraform output to get the instance ID and IP address
            instance_ip = subprocess.run(['C:\\terraform\\terraform.exe', 'output', 'instance_ip'], capture_output=True).stdout.decode().strip()
            
            # instance_id = subprocess.run(['C:\\terraform\\terraform.exe', 'output', 'instance_id'], capture_output=True).stdout.decode().strip()
            instance_ip= subprocess.run(['C:\\terraform\\terraform.exe', 'output', 'instance_ip'], capture_output=True).stdout.decode().strip()
            # Clean up the Terraform configuration file
            os.remove(tf_config_filename)
            # Clean up

            # Prepare the context to pass to the success template
            context = {
                'ip_address': instance_ip,
                'servername':server_name,
                'OS':os_type,
            }
            messages.success(request, 'Successfull !') 
            return render(request, 'deployment_service/install_success.html', context)

    return render(request, 'index.html')            
      

# #Jenkins Installation
# import paramiko
# from django.shortcuts import render
# import boto3
# from botocore.config import Config

# def install_jenkins(request):
#     if request.method == 'POST':
#             ip_address = request.POST.get('ipaddress')
      
    # ec2_client = boto3.client('ec2',
                            #   region_name='us-east-1',
                            #   aws_access_key_id='',
                            #   aws_secret_access_key='')

#     # Describe instances and get the instance ID
#     # response = ec2_client.describe_instances()

#     # # # Extract the instance ID
#     # instance_id = response["InstanceID"]
#     # public_ip=response["PublicIpAddress"]

#     # #  # Create a boto3 client for EC2
#     # ec2_client = boto3.client('ec2', region_name='us-east-1')  # Replace 'us-east-1' with your region

#     # # Use the client to describe the instance and get its public IP address
#     # response = ec2_client.describe_instances(InstanceIds=[instance_id])
#     # public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
#     # config = Config(connect_timeout=120, read_timeout=120)
#     # ec2_client = boto3.client('ec2',region_name='us-east-1',config=config)

# # Get the instance ID by instance name
#     # response = ec2_client.describe_instances(
#     #     Filters=[
#     #         {
#     #           'Name': 'tag:Name',
#     #             'Values': ['None']
#     #         }
#     #     ]
#     # )
#     # instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
    
#     # response = ec2_client.describe_instances(InstanceIds=[instance_id])

#     # # Extract the IP address from the response
#     # ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    
#     # SSH configuration
#     host = '13.48.248.38'
#     port = 22
#     username = 'ubuntu'
#     key_filename = '\Key Pairs\my-key-pair.pem'

#     # Connect to the EC2 instance
#     ssh_client = paramiko.SSHClient()
#     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh_client.connect(hostname=host, port=port, username=username, key_filename=key_filename)

#     # Execute commands to install Jenkins
#     commands = [
#         'sudo apt-get update',
#         'sudo apt-get install -y openjdk-17-jdk',
#         'sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \ https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key',
#         'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \ https://pkg.jenkins.io/debian-stable binary/ | sudo tee \ /etc/apt/sources.list.d/jenkins.list > /dev/null' ,
#         'sudo apt-get update',
#         'sudo apt-get install -y jenkins',
#         'sudo systemctl restart jenkins.service'
#     ]

#     for command in commands:
#         stdin, stdout, stderr = ssh_client.exec_command(command)
#         print(stdout.read().decode('utf-8'))

#     # Close the SSH connection
#     ssh_client.close()

#     return HttpResponse("Jenkins installation completed successfully!")


import jenkins
import time
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def build_job(request):
    if request.method == "POST":
        githubURL = request.POST.get('git_url')
        server_url = request.POST.get('server_url')
        username = request.POST.get('username')
        api_token = request.POST.get('api_token')
        job_name = request.POST.get('job_name')

        if not githubURL or not job_name or not username or not api_token or not server_url:
            return HttpResponse("Fill out the Empty fields", status=400)

        # Jenkins Pipeline script with dynamic GitHub URL
        pipeline_script = f"""
        pipeline {{
            agent any

            triggers {{
                pollSCM('* * * * *')
            }}

            stages {{
                stage('Clone') {{
                    steps {{
                        git '{githubURL}'
                    }}
                }}
                stage('Deploy') {{
                    steps {{
                        sh 'rm -f /var/www/html/index.html'
                        sh 'cp -r * /var/www/html/'
                    }}
                }}
            }}
        }}
        """

        # Jenkins job XML configuration
        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job@2.39">
            <actions/>
            <description>Job to deploy web page from GitHub repository</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
                <script>{pipeline_script}</script>
                <sandbox>true</sandbox>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
        """

        # Connect to Jenkins server
        jenkins_server = jenkins.Jenkins(server_url, username=username, password=api_token)

        try:
            # Create or update the pipeline job
            if jenkins_server.job_exists(job_name):
                print(f"Job '{job_name}' already exists. Reconfiguring it.")
                jenkins_server.reconfig_job(job_name, job_config)
            else:
                print(f"Creating job '{job_name}'.")
                jenkins_server.create_job(job_name, job_config)

            # Build the job
            print(f"Building job '{job_name}'.")
            jenkins_server.build_job(job_name)

            # Wait for the job to finish
            print(f"Waiting for job '{job_name}' to finish.")
            while True:
                last_build = jenkins_server.get_job_info(job_name).get('lastBuild')
                if last_build is None:
                    time.sleep(1)
                    continue

                build_number = last_build.get('number')
                build_info = jenkins_server.get_build_info(job_name, build_number)
                if build_info.get('result') is not None:
                    print(f"Job Status: {build_info['result']}")
                    break

                time.sleep(1)

            context = {
                'githubURL': githubURL,
                'server_url': server_url,
                'username': username,
                'job_name': job_name,
            }

            return render(request, 'deployment_service/build_success.html', context)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

    return HttpResponse("Unsuccessful!", status=400)

    
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import jenkins
import time

@csrf_exempt
def docker_deploy(request):
    if request.method == "POST":
        username = request.POST.get('username')
        api_token = request.POST.get('apitoken')
        server_url = request.POST.get('jenkins-ip')
        job_name = request.POST.get('job-name')
        project_name = request.POST.get('prj-name')
        github_url = request.POST.get('githubURL')
        port_number = request.POST.get('port')

        # Define the Jenkins pipeline script
        pipeline_script = f"""
        pipeline {{
            agent any

            environment {{
                REPO_URL = '{github_url}'
                DOCKER_IMAGE = "krishna16100/devopsstreamline"
                DOCKER_COMPOSE_PATH = 'docker-compose.yml'
                PORT_NUMBER = "{port_number}"  // User-defined port number
            }}

            triggers {{
                pollSCM('* * * * *')
            }}

            stages {{
                stage('Clone Repository') {{
                    steps {{
                        git branch: 'main', url: "${{REPO_URL}}"
                    }}
                }}

                stage('Build Docker Image') {{
                    steps {{
                        script {{
                            docker.build("${{DOCKER_IMAGE}}")
                        }}
                    }}
                }}

                stage('Run Tests') {{
                    steps {{
                        script {{
                            docker.image("${{DOCKER_IMAGE}}").inside {{
                                sh 'python manage.py test'
                            }}
                        }}
                    }}
                }}

                stage('Deploy on Jenkins Server') {{
                    steps {{
                        script {{
                            // Stop existing containers
                            sh '''
                            if [ -f ${{DOCKER_COMPOSE_PATH}} ]; then
                                docker-compose -f ${{DOCKER_COMPOSE_PATH}} down
                            fi
                            '''
                            // Pull the latest image and start the container
                            sh '''
                            if [ -f ${{DOCKER_COMPOSE_PATH}} ]; then
                                docker-compose -f ${{DOCKER_COMPOSE_PATH}} pull
                                docker-compose -f ${{DOCKER_COMPOSE_PATH}} up -d
                            fi
                            '''
                        }}
                    }}
                }}
            }}

            post {{
                always {{
                    cleanWs()
                }}
            }}
        }}
        """

        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job@2.39">
            <actions/>
            <description>Job to deploy web page from GitHub repository</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
                <script>{pipeline_script}</script>
                <sandbox>true</sandbox>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
        """

        jenkins_server = jenkins.Jenkins(server_url, username=username, password=api_token)
        try:
            # Create or update the pipeline job
            if jenkins_server.job_exists(job_name):
                print(f"Job '{job_name}' already exists. Reconfiguring it.")
                jenkins_server.reconfig_job(job_name, job_config)
            else:
                print(f"Creating job '{job_name}'.")
                jenkins_server.create_job(job_name, job_config)

            # Build the job
            print(f"Building job '{job_name}'.")
            jenkins_server.build_job(job_name)

            # Wait for the job to finish
            print(f"Waiting for job '{job_name}' to finish.")
            while True:
                last_build = jenkins_server.get_job_info(job_name).get('lastBuild')
                if last_build is None:
                    time.sleep(1)
                    continue

                build_number = last_build.get('number')
                build_info = jenkins_server.get_build_info(job_name, build_number)
                if build_info.get('result') is not None:
                    print(f"Job Status: {build_info['result']}")
                    break

            response_data = {"status": "success", "message": f"Job '{job_name}' completed with status: {build_info['result']}"}

        except Exception as e:
            response_data = {"status": "error", "message": str(e)}
        
        # Create Nginx configuration file
        nginx_conf = f"""
        <VirtualHost *:80>
            ServerAdmin webmaster@localhost
            DocumentRoot /var/www/html

            Alias /static /app/static
            <Directory /app/static>
                Require all granted
            </Directory>

            <Directory /app/{project_name}>
                <Files wsgi.py>
                    Require all granted
                </Files>
            </Directory>

            WSGIDaemonProcess {project_name} python-path=/app python-home=/usr/local
            WSGIProcessGroup {project_name}
            WSGIScriptAlias / /app/{project_name}/wsgi.py
        </VirtualHost>
        """
        with open('nginx.conf', 'w') as f:
            f.write(nginx_conf)

        prj_nginx_config = f"""
        server {{
            listen 80;
            server_name your_server_ip;  # Replace 'your_server_ip' with the actual server IP

            location / {{
                proxy_pass http://127.0.0.1:{port_number};
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}

            location /static/ {{
                alias /app/static/;
            }}

            location /media/ {{
                alias /app/media/;
            }}

            error_log /var/log/nginx/error.log;
            access_log /var/log/nginx/access.log;
        }}
        """
        with open('myproject_nginx.conf', 'w') as f:
            f.write(prj_nginx_config)

        docker_compose = f"""
        version: '3.8'
        services:
            web:
                build: .
                command: bash -c "python manage.py migrate && gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000 --workers 3"
                volumes:
                    - .:/app
                ports:
                    - "8000:8000"

            nginx:
                image: nginx:latest
                ports:
                    - "{port_number}:80"  # Use the environment variable PORT_NUMBER or default to 80
                volumes:
                    - ./nginx.conf:/etc/nginx/conf.d/default.conf
                depends_on:
                    - web
        """
        with open('docker-compose.yml', 'w') as f:
            f.write(docker_compose)

        start_file = f"""
        #!/bin/bash

        # Start Gunicorn
        gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000 --workers 3 &

        # Start Nginx
        nginx -g 'daemon off;'
        """
        with open('start.sh', 'w') as f:
            f.write(start_file)

        print("Jenkins job and Nginx configuration files have been created.")
        return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})










#Monitoring

import boto3
from datetime import datetime, timedelta
import json

def ec2_metrics(request):
    # AWS credentials and region
    aws_access_key_id= ""
    aws_secret_access_key= ""
    aws_region=''

    # EC2 instance ID
    instance_id = 'your-ec2-instance-id'

    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch', aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_region)

    # Get metrics for the last hour
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cpu',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                },
                'ReturnData': True
            },
            {
                'Id': 'memory',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'MemoryUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                },
                'ReturnData': True
            }
        ],
        StartTime=start_time,
        EndTime=end_time
    )

    # Process the response and format the data for the chart
    cpu_timestamps = [point['Timestamp'] for point in response['MetricDataResults'][0]['Timestamps']]
    cpu_values = [point['Average'] for point in response['MetricDataResults'][0]['Values']]

    memory_timestamps = [point['Timestamp'] for point in response['MetricDataResults'][1]['Timestamps']]
    memory_values = [point['Average'] for point in response['MetricDataResults'][1]['Values']]

    metrics_data = {
        'cpu_labels': cpu_timestamps,
        'cpu_values': cpu_values,
        'memory_labels': memory_timestamps,
        'memory_values': memory_values
    }

    # Pass the data to the template
    return render(request, 'UserDashreports.html', {'metrics_data': json.dumps(metrics_data)})



