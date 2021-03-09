# -*- coding: utf-8 -*-
from django.urls import path
from labelme_ncku import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
       path('labelme', views.show_training_list, name = 'show_training_list'),
       path('labelme/training_folder_name/<str:training_folder_name>', views.show_label_list, name = 'show_label_list'),
       path('labelme/create_label', views.create_label, name = 'create_label'),
       path('labelme/delete_label', views.delete_label, name = 'delete_label'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)