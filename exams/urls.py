# -*- coding: utf-8 -*-
from django.urls import path
from exams import views

urlpatterns = [
    path('exams', views.show_exam_list, name = 'show_exam_list'),
    path('exams/new', views.new_exam, name = 'new_exam'),
    path('exams/new/answers-options', views.get_ajax_answers_options),
    path('exams/new/<int:exam_id>', views.add_exam_questions, name = 'add_more_questions'),
    path('exams/<int:exam_id>', views.show_exam, name = 'show_exam'),
    path('exams/answer/<int:exam_id>', views.user_answers, name = 'user_answers'),
    path('exams/<int:exam_id>/users', views.show_exam_user_list, name = 'show_exam_user_list'),
    path('exams/<int:exam_id>/users/<int:user_id>/result', views.show_user_exam_result, name = 'show_user_exam_result'),
]