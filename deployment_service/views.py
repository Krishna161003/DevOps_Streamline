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

def nginx(request):
  template = loader.get_template('deployment_service/deploy_forms/nginx.html')
  return HttpResponse(template.render())

def ansible(request):
  template = loader.get_template('deployment_service/deploy_forms/ansible.html')
  return HttpResponse(template.render())

def git(request):
  template = loader.get_template('deployment_service/deploy_forms/git.html')
  return HttpResponse(template.render())

def python(request):
  template = loader.get_template('deployment_service/deploy_forms/python.html')
  return HttpResponse(template.render())

def chef(request):
  template = loader.get_template('deployment_service/deploy_forms/chef.html')
  return HttpResponse(template.render())

def docker(request):
  template = loader.get_template('deployment_service/deploy_forms/docker.html')
  return HttpResponse(template.render())

def terraform(request):
  template = loader.get_template('deployment_service/deploy_forms/terraform.html')
  return HttpResponse(template.render())

def infra(request):
  template = loader.get_template('deployment_service/infrastructure.html')
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
                access_key = "AKIAUZ7LQVC6Z2H3X3HA"
                secret_key = "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"
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
                sudo usermod -aG docker jenkins
                sudo systemctl restart jenkins
                sudo systemctl restart docker
                sudo apt install git
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
import tempfile

@csrf_exempt
def install_nginx(request):
    if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
    print("FILES keys:", request.FILES.keys())

    if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

    key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
    port = 22
    # username = 'ubuntu'
    # key_filename = 'C:/Key Pairs/my-key-pair.pem.pub'

    # Connect to the EC2 instance
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
    commands = [
        'sudo apt-get update',
        'sudo apt install -y nginx',
        'sudo systemctl start nginx',
        'sudo systemctl enable nginx',
        'sudo systemctl status nginx',
    ]

    for command in commands:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stdout.read().decode('utf-8'))

    # Close the SSH connection
    ssh_client.close()

    return HttpResponse("installation completed successfully!")

# ANSIBLE
@csrf_exempt
def install_ansible(request):
     if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
     print("FILES keys:", request.FILES.keys())

     if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

     key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
     with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
     port = 22
    # username = 'ubuntu'
    # key_filename = 'C:/Key Pairs/my-key-pair.pem.pub'

    # Connect to the EC2 instance
     ssh_client = paramiko.SSHClient()
     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
     commands = [
        'sudo apt-get update',
        'sudo apt install -y software-properties-common',
        'sudo add-apt-repository --yes --update ppa:ansible/ansible',
        'sudo apt update',
        'sudo apt install -y ansible',
    ]

     for command in commands:
         stdin, stdout, stderr = ssh_client.exec_command(command)
         print(stdout.read().decode('utf-8'))

    # Close the SSH connection
     ssh_client.close()

     return HttpResponse("installation completed successfully!")

# CHEFSOLO
@csrf_exempt
def install_chef(request):
     if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
     print("FILES keys:", request.FILES.keys())

     if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

     key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
     with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
     port = 22
    # username = 'ubuntu'
    # key_filename = 'C:/Key Pairs/my-key-pair.pem.pub'

    # Connect to the EC2 instance
     ssh_client = paramiko.SSHClient()
     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
     commands = [
        'sudo apt-get update',
        'sudo apt install wget',                                                
        'wget https://packages.chef.io/files/stable/chefdk/4.15.6/ubuntu/20.04/chefdk_4.15.6-1_amd64.deb',
        'sudo dpkg -i chefdk_4.15.6-1_amd64.deb',
        'echo "eval "$(chef shell-init bash)"" >> ~/.bash_profile',
        'source ~/.bash_profile',
        'chef --version',
    ]

     for command in commands:
         stdin, stdout, stderr = ssh_client.exec_command(command)
         print(stdout.read().decode('utf-8'))

    # Close the SSH connection
     ssh_client.close()

     return HttpResponse("installation completed successfully!")

# git
@csrf_exempt
def install_git(request):
     if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
     print("FILES keys:", request.FILES.keys())

     if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

     key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
     with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
     port = 22
    # username = 'ubuntu'
    # key_filename = 'C:/Key Pairs/my-key-pair.pem.pub'

    # Connect to the EC2 instance
     ssh_client = paramiko.SSHClient()
     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
     commands = [
        'sudo apt-get update',
        'sudo apt install git',                                                
        'git --version',
    ]

     for command in commands:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stdout.read().decode('utf-8'))

    # Close the SSH connection
     ssh_client.close()

     return HttpResponse("Jenkins installation completed successfully!")

#python
@csrf_exempt
def install_python(request):
    if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
    print("FILES keys:", request.FILES.keys())

    if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

    key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
    with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
    port = 22
    # username = 'ubuntu'
    # key_filename = 'C:/Key Pairs/my-key-pair.pem.pub'

    # Connect to the EC2 instance
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
    commands = [
        'sudo apt-get update',
        'sudo apt install python3',                                                
        'python3 --version',
        'sudo apt install python3-pip',
    ]

    for command in commands:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stdout.read().decode('utf-8'))


#docker
@csrf_exempt
def install_docker(request):
     if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
     print("FILES keys:", request.FILES.keys())

     if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

     key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
     with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
     port = 22
     ssh_client = paramiko.SSHClient()
     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
     commands = [
        'sudo apt update',
        'sudo apt install curl',
        'sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common',
        'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
        'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
        'sudo apt-get update',
        'sudo apt-get install -y docker-ce',
        'sudo usermod -aG docker $USER',
        'sudo systemctl start docker',
        'sudo systemctl enable docker',
    ]

     for command in commands:
         stdin, stdout, stderr = ssh_client.exec_command(command)
         print(stdout.read().decode('utf-8'))


    # Close the SSH connection
     ssh_client.close()

     return HttpResponse("Installation completed successfully!")

#terraform
@csrf_exempt
def install_terraform(request):
     if request.method == 'POST':
            ip_address = request.POST.get('ipaddress')
            username = request.POST.get('username')
            key_file=request.FILES['keypair']
    # SSH configuration
    # Debugging: Print request.FILES keys
     print("FILES keys:", request.FILES.keys())

     if 'keypair' not in request.FILES:
            return HttpResponse("No key pair uploaded.", status=400)

     key_file = request.FILES['keypair']

        # Create a temporary file to save the uploaded key pair
     with tempfile.NamedTemporaryFile(delete=False) as temp_key_file:
            key_file_path = temp_key_file.name
            for chunk in key_file.chunks():
                temp_key_file.write(chunk)
     port = 22
     ssh_client = paramiko.SSHClient()
     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     ssh_client.connect(hostname=ip_address, port=port, username=username, key_filename=key_file_path)

    # Execute commands to install Jenkins
     commands = [
        'sudo apt update',
        'sudo apt-get install -y gnupg software-properties-common curl',
        'curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -'
        'sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"'
        'sudo apt-get update'
        'sudo apt-get install -y terraform'
        'sudo apt-get update -y'
    ]

     for command in commands:
         stdin, stdout, stderr = ssh_client.exec_command(command)
         print(stdout.read().decode('utf-8'))

#terraform
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import paramiko
import tempfile

@csrf_exempt
def docker_deploy(request):
    if request.method == 'POST':
        github_url = request.POST.get('githubURL')
        job_name = request.POST.get('job-name')

        if not github_url or not job_name:
            return JsonResponse({"status": "error", "message": "Missing required parameters."}, status=400)

        # SSH configuration
        key_file_path = 'C:/Key Pairs/my-key-pair.pem'
        hostname = 'your-server-ip'  # Add your server IP address here
        port = 22
        username = 'DevOps0987'

        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=hostname, port=port, username=username, key_filename=key_file_path)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"SSH connection failed: {str(e)}"}, status=500)

       # Extract the repository name from the GitHub URL
        repo_name = github_url.split('/')[-1].replace('.git', '')

        commands = [
            'sudo apt update',
            f'sudo mkdir -p /home/ubuntu/docker/{job_name}',
            f'cd /home/ubuntu/docker/{job_name}',
            f'git clone {github_url}',
            f'cd {repo_name}',  # Navigate into the cloned repository directory
            'sudo docker-compose up -d --build'
        ]


        try:
            for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                if error:
                    return JsonResponse({"status": "error", "message": f"Command '{command}' failed: {error}"}, status=500)
                print(output)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Command execution failed: {str(e)}"}, status=500)
        finally:
            ssh_client.close()

        return JsonResponse({"status": "success", "message": "Installation completed successfully!"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


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
import requests
import jenkins
import time

@csrf_exempt
def docker_deploy(request):
    if request.method == "POST":
        # username = request.POST.get('username')
        # api_token = request.POST.get('apitoken')
        # server_ip = request.POST.get('jenkins-ip')
        job_name = request.POST.get('job-name')
        github_url = request.POST.get('githubURL')
        # port_number = request.POST.get('port')

        username = 'DevOps0987'
        api_token = '0987'
        server_ip = '3.90.210.189'

        pipeline_script = f"""
        pipeline {{
            agent any
            stages {{
                stage('Checkout') {{
                    steps {{
                        git url: '{github_url}', branch: 'main'
                    }}
                }}
                stage('Build Docker Image') {{
                    steps {{
                        sh 'sudo docker build -t {job_name}/devopsstreamline .'
                    }}
                }}
                stage('Deploy with Docker Compose') {{
                    steps {{
                        script {{
                            try {{
                                sh 'sudo docker-compose down'
                            }} catch (Exception e) {{
                                echo 'docker-compose down failed, possibly because there was no running container'
                            }}
                            sh 'sudo docker-compose up -d'
                        }}
                    }}
                }}
            }}
        }}
        """

        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job@2.40">
            <actions/>
            <description>Pipeline job to deploy Django project from GitHub repository</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.93">
                <script>{pipeline_script}</script>
                <sandbox>true</sandbox>
            </definition>
            <triggers>
                <hudson.triggers.SCMTrigger>
                    <spec>* * * * *</spec>
                </hudson.triggers.SCMTrigger>
            </triggers>
        </flow-definition>
        """

        server_url = f"http://{server_ip}:8080"
        auth = (username, api_token)

        # Fetch the Jenkins crumb
        crumb_response = requests.get(f"{server_url}/crumbIssuer/api/json", auth=auth)
        if crumb_response.status_code != 200:
            return JsonResponse({"status": "error", "message": "Failed to fetch Jenkins crumb"})

        crumb = crumb_response.json()['crumb']
        headers = {
            'Jenkins-Crumb': crumb,
        }

        try:
            jenkins_server = jenkins.Jenkins(server_url, username=username, password=api_token)
            
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

        return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})





#Monitoring

import boto3
from datetime import datetime, timedelta
import json

def ec2_metrics(request):
    # AWS credentials and region
    aws_access_key_id= "AKIAUZ7LQVC6WMWU73TN"
    aws_secret_access_key= "eVamLjfTjLZQzQ8fyrpXYcdGuXeHm09hZj7Dmzsn"
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