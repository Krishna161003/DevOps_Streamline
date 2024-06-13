from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class role(models.Model):
    
class MyModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        permissions = [
            ("can_view_dashboard", "Can view dashboard"),
            ("can_edit_projects", "Can edit projects"),
            ("can_add_user","Can add user")
            # Add other custom permissions as needed
        ]

