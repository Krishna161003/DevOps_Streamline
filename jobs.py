import paramiko

    
host = "54.204.222.16"
port = "22"
username ="ubuntu" 
password = "123"

            # Connect to the EC2 instance
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=host, port=port, username=username, password=password)

            # Execute commands to install Jenkins
commands = [
                'sudo apt-get update',
                'sudo apt-get install -y openjdk-17-jdk',
                'sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key',
                'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null',
                'sudo apt-get update',
                'sudo apt-get install -y jenkins',
                'sudo systemctl restart jenkins.service'
            ]

for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)
                print(stdout.read().decode('utf-8'))

            # Close the SSH connection
ssh_client.close()