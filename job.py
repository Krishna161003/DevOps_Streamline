import jenkins
import time

# Jenkins server configuration
server_url = 'http://100.27.197.162:8080/'
username = 'Krishna1610'
api_token = '0987'
job_name = 'webpage-deployment'
githubURL = 'https://github.com/Krishna161003/MyRepo1.git'

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
except Exception as e:
    print(f"An error occurred: {str(e)}")
# stage('Push Docker Image') {{
                    #     steps {{
                    #         script {{
                    #             docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials-id') {{
                    #                 docker.image("${{DOCKER_IMAGE}}").push('latest')
                    #             }}
                    #         }}
                    #     }}
                    # }}