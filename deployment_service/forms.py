from django import forms

class ServerForm(forms.Form):
    server_name = forms.CharField(label='Server Name', max_length=100)
    description=forms.CharField(label='Description',max_length=100)