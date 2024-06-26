from django.shortcuts import redirect, render
from django.forms import *

# Create your views here.
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
# from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import login, authenticate , logout
from django.contrib.auth.models import auth
from administration.forms import LoginForm, RegistrationForm
from django.shortcuts import render
from django.contrib import messages

def dashboard(request):
  template = loader.get_template('administration/dashboard.html')
  return HttpResponse(template.render())



def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request,email=email, password=password)
            if user is not None:
              auth.login(request, user)
              return redirect('main')
            else:   
              messages.error(request, "Invalid username or password.")
            
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def password(request):
  template = loader.get_template('administration/password.html')
  return HttpResponse(template.render())


def tables(request):
  template = loader.get_template('administration/tables.html')
  return HttpResponse(template.render())


def reports(request):
  template = loader.get_template('administration/reports.html')
  return HttpResponse(template.render())


def deplyments(request):
  template = loader.get_template('administration/deplyments.html')
  return HttpResponse(template.render())

def Users(request):
  template = loader.get_template('administration/Users.html')
  return HttpResponse(template.render())

def admininfra(request):
  template = loader.get_template('administration/admininfra.html')
  return HttpResponse(template.render())









    


def registers(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created ! You are now able to log in')
            return redirect('login')  # Replace 'home' with the name of your homepage URL pattern
    else:
        form = RegistrationForm()
    return render(request, 'administration/register.html',{'form':form})

import boto3 
import datetime
#Monitoring
def ec2_metrics(request):
    # AWS credentials and region
    aws_access_key_id = 'your-access-key-id'
    aws_secret_access_key = 'your-secret-access-key'
    aws_region = 'your-region'

    # EC2 instance ID
    instance_id = 'your-ec2-instance-id'

    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch', aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_region)

    # Get metrics for the last hour
    end_time = datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=1)

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
    return render(request, 'reports.html', {'metrics_data': json.dumps(metrics_data)})

