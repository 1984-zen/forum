# -*- coding: utf-8 -*-
from django.urls import path
from labelme_ncku import views

urlpatterns = [
       path('labelme/json_file', views.get_labelme_json_file)
]