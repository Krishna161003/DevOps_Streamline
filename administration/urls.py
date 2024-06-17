from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard, name = 'dashboard'),
    path('login/',views.login, name = 'login'),
    path('password/',views.password, name = 'password'),
    path('register/',views.registers, name = 'registers'),
    path('tables/',views.tables, name = 'tables'),
    path('reports/',views.reports, name='reports'),
    path('deplyments/',views.deplyments, name='deplyments'),
    path('password/',views.password, name='password'),
]