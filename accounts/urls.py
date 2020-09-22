# -*- coding: utf-8 -*-
from django.urls import path
from accounts import views

urlpatterns = [
    path('register', views.register, name = 'register'),
    path('login', views.login, name = 'login'),
    path('login/method_post', views.login_post),
    path('logout', views.logout),
    ]
