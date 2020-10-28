from django.shortcuts import render
from exams.models import Exams, Questions, Options, Option_Users
from accounts.models import Users
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
import os
from django.db.utils import DatabaseError, IntegrityError
from django.contrib import messages
# from pprint import pprint
from django.http import JsonResponse
from django.http import HttpResponse
import json

def show_exam_list(request):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    exam_list = Exams.objects.all().order_by('-created_at')
    return render(request, 'exam_list.html', {'exam_list': exam_list, 'username': username})

def show_exam_user_list(request, exam_id):
    exam_id = exam_id
    user_ids = Option_Users.objects.filter(exam_id = exam_id).values('user_id').distinct()
    # exams = Users.objects.filter(id__in=user_ids).prefetch_related('option_users')
    # users = Users.objects.prefetch_related('option_users').all()
    users = Users.objects.prefetch_related('option_users').filter(id__in=user_ids)
    return render(request, 'exam_user_list.html', {'users': users, 'exam_id': exam_id})

def new_exam(request):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    return render(request, 'new_exam.html', {'username': username})

def get_ajax_answers_options(request):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    
    question = json.loads(request.body)['question']
    option_list = json.loads(request.body)['option_list']
    answer_list = json.loads(request.body)['answer_list']
    if(json.loads(request.body)['exam_id']):
        exam_id = json.loads(request.body)['exam_id']
        create_question = Questions(question = question, exam_id = exam_id)
        create_question.save()
        for i in range(len(option_list)):
            create_option = Options(option = option_list[i], is_answer = answer_list[i], question_id = create_question.id)
            create_option.save()
        return JsonResponse({'exam_id': exam_id})
    else:
        exam_title = json.loads(request.body)['exam_title']
        create_exam = Exams(user_id = user_id, name = exam_title)
        create_exam.save()
        create_question = Questions(question = question, exam_id = create_exam.id)
        create_question.save()
        for i in range(len(option_list)):
            create_option = Options(option = option_list[i], is_answer = answer_list[i], question_id = create_question.id)
            create_option.save()
        return JsonResponse({'exam_id': create_exam.id})

def add_exam_questions(request, exam_id):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    exam = Exams.objects.get(id = exam_id)
    questions = exam.questions.all()
    return render(request, 'add_exam_questions.html', {'exam_id': exam_id, 'username': username, 'exam': exam, 'questions': questions})

def show_exam(request, exam_id):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    exam = Exams.objects.get(id = exam_id)
    questions = exam.questions.all()
    return render(request, 'show_exam.html', {'exam_id': exam_id, 'username': username, 'exam': exam, 'exam_id': exam_id, 'questions': questions})

def user_answers(request, exam_id):
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    exam_id = exam_id
    option_ids_list = request.POST.getlist("option_id[]")
    for option_id in option_ids_list:
        question_id = Options.objects.filter(id = option_id)[0].question_id
        create_option_users = Option_Users(user_id = user_id, option_id = option_id, question_id = question_id, exam_id = exam_id)
        create_option_users.save()
    return HttpResponse("Test result has been sent successfully.")

def show_user_exam_result(request, exam_id, user_id):
    username = Users.objects.get(id = user_id)
    questions = Questions.objects.filter(exam_id = exam_id)
    user_answers = Option_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id)
    user_answer_list = []
    for user in user_answers:
        user_answer_list.append(user.option_id)
    return render(request, 'show_user_exam_result.html', {'username': username, 'questions': questions, 'user_answer_list': user_answer_list})