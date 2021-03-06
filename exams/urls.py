# -*- coding: utf-8 -*-
from django.urls import path
from exams import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('exams', views.show_exam_list, name = 'show_exam_list'),
    path('exams/new', views.new_exam, name = 'new_exam'),
    path('exams/new/answers-options', views.get_ajax_answers_options),
    path('exams/new/<int:exam_id>', views.add_exam_questions, name = 'add_more_questions'),
    path('exams/<int:exam_id>', views.show_exam, name = 'show_exam'),
    path('exams/answer/<int:exam_id>', views.user_answers, name = 'user_answers'),
    path('exams/<int:exam_id>/users', views.show_exam_user_list, name = 'show_exam_user_list'),
    path('exams/<int:exam_id>/users/<int:user_id>/result/<int:user_exam_count>', views.show_user_exam_result, name = 'show_user_exam_result'),
    path('exams/<int:exam_id>/users/<int:user_id>/exam_completed', views.user_exam_completed, name = 'user_exam_completed'),
    path('exams/<int:exam_id>/questions/<int:question_id>/update', views.update_question, name = 'update_question'),
    path('exams/<int:exam_id>/questions/<int:question_id>/options/<int:option_id>/update', views.update_next_question_id, name = 'update_next_question_id'),
    path('exams/<int:exam_id>/questions/<int:question_id>/delete', views.delete_question, name = 'delete_question'),
    path('exams/<int:exam_id>/questions/<int:question_id>/question_files/<int:question_media_id>/delete', views.delete_question_media, name = 'delete_question_media'),
    path('exams/<int:exam_id>/questions/<int:question_id>/question_files/<int:question_image_id>/delete', views.delete_question_image, name = 'delete_question_image'),
    path('exams/<int:exam_id>/options/<int:option_id>/delete', views.delete_option, name = 'delete_option'),
    path('exams/<int:exam_id>/delete', views.delete_exam, name = 'delete_exam'),
    path('exams/<int:exam_id>/users/<int:user_id>/result/<int:user_exam_count>/download', views.export_user_answer_xls, name = 'export_user_answer_xls'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)