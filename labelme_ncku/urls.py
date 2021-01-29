# -*- coding: utf-8 -*-
from django.urls import path
from labelme_ncku import views

urlpatterns = [
       path('labelme/json_file_path', views.get_labelme_json_file_path, name = 'get_labelme_json_file_path'),
       path('labelme', views.show_label_list, name = 'show_label_list')
]