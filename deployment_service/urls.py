from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path


urlpatterns = [
    path('',views.index, name = 'index'),
    path('main/',views.main, name = 'main'),
    path('create/',views.create, name = 'create'),
    path('UserDash/',views.UserDash,name='UserDash'),
    path('CreateServer/',views.CreateServer,name='CreateServer'),
    path('build-job/',views.build_job,name='build_job'),
    path('buildform/',views.buildform,name='buildform'),
    path('deploy-ec2/', views.deploy_ec2, name='deploy_ec2'),
    # path('install_jenkins/', views.install_jenkins, name='install_jenkins'),
    path('installsuccess/', views.InstallSuccess, name='install_success'),
    path('installfail/', views.InstallFail, name='install_fail'),
    path('UserReports/',views.UserDashreports,name='UserReports'),
    path('profile/',views.Userprofile,name='profile'),
    path('landing/',views.landing,name='landing'),
    path('build/',views.buildform,name='build'),
    path('buildsuccess/',views.BuildSuccess,name='BuildSuccess'),
    path('projectdeploy/',views.prj_deploy,name='prj_deploy'),
    path('docker_deploy/',views.docker_deploy,name='docker_deploy'),
    path('nginx/',views.nginx,name='nginx'),
    path('install_nginx/',views.install_nginx,name='install_nginx'),
    path('ansible/',views.ansible,name='ansible'),
    path('install_ansible/',views.install_ansible,name='install_ansible'),
    path('git/',views.git,name='git'),
    path('install_git/',views.install_git,name='install_git'),
    path('python/',views.python,name='python'),
    path('install_python/',views.install_python,name='install_python'),
    path('chef/',views.chef,name='chef'),
    path('install_chef/',views.install_chef,name='install_chef'),
    path('infra/',views.infra,name='infra'),
    path('docker/',views.docker,name='docker'),
    path('install_docker/',views.install_docker,name='install_docker'),
    path('terraform/',views.terraform,name='terraform'),
    path('install_terraform/',views.install_terraform,name='install_terraform'),
    #  path('CreateServer/', views.server_form_view, name='CreateServer'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)