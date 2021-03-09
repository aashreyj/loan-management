"""loan_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from .views import RegistrationView, UserViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    # create new user
    path('account/register', RegistrationView.as_view()),

    # list all users
    path('account/users', UserViewSet.as_view({
        'get': 'list',
    })),

    # retrieve or edit users using id
    # can only be done by 'agent' and 'admin' roles
    path('account/users/<id>', UserViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
    })),

    # go to loan-related urls
    path('loan/', include('loan.urls')),
]
