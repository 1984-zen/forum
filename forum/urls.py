# -*- coding: utf-8 -*-
from django.urls import path
from forum import views

urlpatterns = [
    path('boards', views.show_boards, name = 'show_boards'),
    path('boards/<int:board_id>/posts', views.show_posts, name='show_posts'),
    path('boards/<int:board_id>/posts/new', views.new_post),
    path('download/<str:file_relative_path>', views.download),
    path('boards/<int:board_id>/posts/<int:post_id>/recommands', views.show_recommands, name='show_recommands'),
    path('boards/<int:board_id>/posts/<int:post_id>/recommands/new', views.new_recommand),
    path('boards/<int:board_id>/posts/<int:post_id>/recommands/<int:recommand_id>/file/<int:file_id>/delete', views.delete_recommand_file),
    path('boards/<int:board_id>/posts/<int:post_id>/recommands/<int:recommand_id>/delete', views.delete_recommand),
    path('boards/<int:board_id>/posts/<int:post_id>/recommands/<int:recommand_id>/update', views.update_recommand),
    path('boards/<int:board_id>/posts/<int:post_id>/delete', views.delete_post),
    path('boards/<int:board_id>/posts/<int:post_id>/file/<int:file_id>/delete', views.delete_post_file),
    path('boards/<int:board_id>/posts/<int:post_id>/update', views.update_post)
]