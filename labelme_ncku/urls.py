# -*- coding: utf-8 -*-
from django.urls import path
from labelme_ncku import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
       path('labelme', views.show_training_list, name = 'show_training_list'),
       path('labelme/training_folder_name/<str:training_folder_name>/search', views.search, name = 'search'),
       path('labelme/training_folder_name/<str:training_folder_name>/patients', views.show_patient_list, name = 'show_patient_list'),
       path('labelme/training_folder_name/<str:training_folder_name>/patients/<str:patient_folder_name>', views.show_patient_labels, name = 'show_patient_labels'),
       path('labelme/create_label', views.create_label, name = 'create_label'),
       path('labelme/update_label', views.update_label, name = 'update_label'),
       path('labelme/delete_label', views.delete_label, name = 'delete_label'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)