"""HCC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from v1 import views

urlpatterns = [
    path('v1/auth/csrf', views.auth_csrf_func),
    path('v1/auth/token', views.auth_token_func),
    path('v1/auth/password', views.auth_password_func),
    path("v1/auth/access-keys", views.auth_access_keys_func),
    path("v1/<cloud_id>/auth/access-keys", views.cloud_auth_access_keys_func),
    path('v1/instances', views.instances_func),
    path('v1/<cloud_id>/instances', views.cloud_instances_func),
    path('v1/<cloud_id>/instances/create', views.cloud_instances_create_func),
    path('v1/<cloud_id>/instances/<instance_id>', views.cloud_instances_instance_func),
    path('v1/<cloud_id>/instances/<instance_id>/action', views.cloud_instances_instance_action_func),
    path('v1/key-pairs', views.key_pairs_func),
    path('v1/<cloud_id>/key-pairs', views.cloud_key_pairs_func),
    path('v1/<cloud_id>/key-pairs/<key_pair_name>', views.cloud_key_pairs_key_pair_func),
    path('v1/vpcs', views.vpcs_func),
    path('v1/vpcs/create', views.vpcs_create_func),
    path('v1/vpcs/<vpc_id>', views.vpcs_vpc_func),
    path('v1/routers', views.routers_func),
    path('v1/<cloud_id>/routers/<router_id>', views.cloud_routers_router_func),
    path('v1/security-groups', views.security_groups_func),
]
