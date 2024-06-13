from django.urls import path
from . import views

urlpatterns = [
    path('error_401/',views.error_401, name = '401_error'),
    path('error_404/',views.error_404, name = '404_error'),
    path('error_500/',views.error_500, name = '500_error'),
    path('charts/',views.charts, name = 'charts'),
    path('dashboard/',views.dashboard, name = 'dashboard'),
    path('layout_sidenav_light/',views.layout_sidenav_light, name = 'layout_sidenav_light'),
    path('layout_static/',views.layout_static, name = 'layout_static'),
    path('login/',views.login, name = 'login'),
    path('login/',views.login_view, name = 'login_view'),
    path('password/',views.password, name = 'password'),
    path('register/',views.register, name = 'register'),
    path('register/',views.registers, name = 'registers'),
    path('tables/',views.tables, name = 'tables'),
    path('Users/',views.Users, name='Users'),
    path('project/',views.projects, name='projects'),
    path('reports/',views.reports, name='reports'),
    path('deplyments/',views.deplyments, name='deplyments'),
    path('password/',views.password, name='password'),


    
]