import jenkins
import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def docker_deploy(request):
    if request.method == "POST":
        username = request.POST.get('username')
        api_token = request.POST.get('apitoken')
        server_ip = request.POST.get('jenkins-ip')
        job_name = request.POST.get('job-name')
        project_name = request.POST.get('prj-name')
        github_url = request.POST.get('githubURL')
        port_number = request.POST.get('port')

        if not all([username, api_token, server_ip, job_name, project_name, github_url, port_number]):
            return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)

        server_url = f"http://{server_ip}:8080"
        
        try:
            # Fetch Jenkins crumb for CSRF protection
            crumb_issuer_url = f"{server_url}/crumbIssuer/api/json"
            response = requests.get(crumb_issuer_url, auth=(username, api_token))
            response.raise_for_status()
            crumb_data = response.json()
            crumb = crumb_data['crumb']
            crumb_field = crumb_data['crumbRequestField']

            # Jenkins job configuration in XML format
            job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
            <flow-definition plugin="workflow-job@2.39">
                <actions/>
                <description>Job to deploy web page from GitHub repository</description>
                <keepDependencies>false</keepDependencies>
                <properties/>
                <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
                    <script>
                        pipeline {{
                            agent any

                            environment {{
                                REPO_URL = '{github_url}'
                                DOCKER_IMAGE = "krishna16100/devopsstreamline"
                                DOCKER_COMPOSE_PATH = 'docker-compose.yml'
                                PORT_NUMBER = "{port_number}"
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

                                stage('Copy Nginx Configuration Files') {{
                                    steps {{
                                        script {{
                                            def repo_dir = pwd()
                                            def nginx_conf_path = "${{repo_dir}}/nginx.conf"
                                            def myproject_nginx_conf_path = "${{repo_dir}}/myproject_nginx.conf"
                                            def docker_compose_path = "${{repo_dir}}/docker-compose.yml"
                                            def start_script_path = "${{repo_dir}}/start.sh"

                                            writeFile file: nginx_conf_path, text: '''
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
    '''

                                            writeFile file: myproject_nginx_conf_path, text: '''
    server {{
        listen {port_number};
        server_name {server_ip};

        location / {{
            proxy_pass http://127.0.0.1:8000;
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
    '''

                                            writeFile file: docker_compose_path, text: '''
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
                - "{port_number}:80"
            volumes:
                - ./nginx.conf:/etc/nginx/conf.d/default.conf
            depends_on:
                - web
    '''

                                            writeFile file: start_script_path, text: '''
    #!/bin/bash
    gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000 --workers 3 &
    nginx -g 'daemon off;'
    '''
                                        }}
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
                                            sh '''
                                            if [ -f ${{DOCKER_COMPOSE_PATH}} ]; then
                                                docker-compose -f ${{DOCKER_COMPOSE_PATH}} down
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
                    </script>
                    <sandbox>true</sandbox>
                </definition>
                <triggers/>
                <disabled>false</disabled>
            </flow-definition>
            """

            jenkins_server = jenkins.Jenkins(server_url, username=username, password=api_token)
            
            # Create or reconfigure the job using Jenkins REST API with crumb header
            job_url = f"{server_url}/job/{job_name}/config.xml"
            create_url = f"{server_url}/createItem?name={job_name}"
            headers = {crumb_field: crumb, 'Content-Type': 'application/xml'}

            if jenkins_server.job_exists(job_name):
                print(f"Job '{job_name}' already exists. Reconfiguring it.")
                response = requests.post(job_url, data=job_config, headers=headers, auth=(username, api_token))
            else:
                print(f"Creating job '{job_name}'.")
                response = requests.post(create_url, data=job_config, headers=headers, auth=(username, api_token))

            response.raise_for_status()

            # Build the job
            print(f"Building job '{job_name}'.")
            build_url = f"{server_url}/job/{job_name}/build"
            response = requests.post(build_url, headers=headers, auth=(username, api_token))
            response.raise_for_status()

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

        except requests.exceptions.HTTPError as http_err:
            response_data = {"status": "error", "message": f"HTTP error occurred: {http_err}"}
        except Exception as e:
            response_data = {"status": "error", "message": str(e)}
        
        return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})


import jenkins
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def docker_deploy(request):
    if request.method == "POST":
        username = request.POST.get('username')
        api_token = request.POST.get('apitoken')
        server_ip = request.POST.get('jenkins-ip')
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
                    DOCKER_IMAGE = "{job_name}/devopsstreamline"
                    DOCKER_COMPOSE_PATH = 'docker-compose.yml'
                    PORT_NUMBER = "{port_number}"
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

                    stage('Run Docker Compose') {{
                        steps {{
                            script {{
                                sh '''
                                if [ -f ${{DOCKER_COMPOSE_PATH}} ]; then
                                    docker-compose -f ${{DOCKER_COMPOSE_PATH}} down
                                    docker-compose -f ${{DOCKER_COMPOSE_PATH}} up -d
                                else
                                    echo "Docker compose file not found"
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
            <description>Job to deploy Django project from GitHub repository</description>
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


        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
        <project>
            <actions/>
            <description>Job to deploy Django project from GitHub repository</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <scm class="hudson.plugins.git.GitSCM" plugin="git@4.8.2">
                <configVersion>2</configVersion>
                <userRemoteConfigs>
                    <hudson.plugins.git.UserRemoteConfig>
                        <url>{github_url}</url>
                    </hudson.plugins.git.UserRemoteConfig>
                </userRemoteConfigs>
                <branches>
                    <hudson.plugins.git.BranchSpec>
                        <name>*/main</name>
                    </hudson.plugins.git.BranchSpec>
                </branches>
                <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                <submoduleCfg class="list"/>
                <extensions/>
            </scm>
             <triggers>
                <hudson.triggers.SCMTrigger>
                    <spec>* * * * *</spec>
                </hudson.triggers.SCMTrigger>
            </triggers>
            <builders>
                <hudson.tasks.Shell>
                    <command>
                        sudo docker build -t {job_name}/devopsstreamline .
                        sudo docker-compose down || true
                        sudo docker-compose up -d
                    </command>
                </hudson.tasks.Shell>
            </builders>
            <publishers/>
            <buildWrappers/>
        </project>
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
            
            # Create or update the freestyle job
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
