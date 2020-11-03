from django.shortcuts import render
from exams.models import Exams, Questions, Options, Option_Users, Exam_files
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
from django.conf import settings

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
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    exam = Exams.objects.get(id = exam_id)
    user_ids = Option_Users.objects.filter(exam_id = exam_id).values('user_id').distinct()
    # users = Users.objects.prefetch_related('option_users').filter(id__in=user_ids) #同下users
    users = Users.objects.filter(id__in=user_ids)
    #下面兩個是筆記
    # exams = Users.objects.filter(id__in=user_ids).prefetch_related('option_users')
    # users = Users.objects.prefetch_related('option_users').all()
    return render(request, 'exam_user_list.html', {'users': users, 'exam': exam, 'username': username})

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
   
    question = request.POST.get("question")
    option_list = request.POST.get("option_list").split(',') #因為從前端接收到的值= True,False所以用split(',')變成['True', 'False']
    answer_list = request.POST.get("answer_list").split(',') #因為從前端接收到的值= True,False所以用split(',')變成['True', 'False']
    if(request.POST.get("exam_id")): #如果已經創立好exam只是要增加問題跟選項
        exam_id = request.POST.get("exam_id")
        create_question = Questions(question = question, exam_id = exam_id)
        create_question.save()

        for i in range(len(option_list)):
            create_option = Options(option = option_list[i], is_answer = answer_list[i], question_id = create_question.id)
            create_option.save()

        if(request.FILES.getlist('media_file')):
            files = request.FILES.getlist('media_file')
            for file in files:
                fname, file_relative_path = handle_uploaded_media_file(file)
                create_file_path = Exam_files(name = fname, file_path = file_relative_path, type = "media", exam_id = exam_id, question_id = create_question.id)
                create_file_path.save()
        
        if(request.FILES.getlist('image_list')):
            images = request.FILES.getlist('image_list')
            for image in images:
                fname, file_relative_path = handle_uploaded_image_file(image)
                create_file_path = Exam_files(name = fname, file_path = file_relative_path, type = "image", exam_id = exam_id, question_id = create_question.id)
                create_file_path.save()
        return JsonResponse({'exam_id': exam_id})
    else: #如果是新建立exam
        exam_title = request.POST.get("exam_title")
        create_exam = Exams(user_id = user_id, name = exam_title)
        create_exam.save()
        create_question = Questions(question = question, exam_id = create_exam.id)
        create_question.save()
        
        for i in range(len(option_list)):
            create_option = Options(option = option_list[i], is_answer = answer_list[i], question_id = create_question.id)
            create_option.save()
        
        if(request.FILES.getlist('media_file')):
            files = request.FILES.getlist('media_file')
            for file in files:
                fname, file_relative_path = handle_uploaded_media_file(file)
                create_file_path = Exam_files(name = fname, file_path = file_relative_path, type = "media", exam_id = create_exam.id, question_id = create_question.id)#拿取剛建立完的create_exam.id
                create_file_path.save()

        if(request.FILES.getlist('image_list')):
            images = request.FILES.getlist('image_list')
            for image in images:
                fname, file_relative_path = handle_uploaded_image_file(image)
                create_file_path = Exam_files(name = fname, file_path = file_relative_path, type = "image", exam_id = create_exam.id, question_id = create_question.id)#拿取剛建立完的create_exam.id
                create_file_path.save()
        return JsonResponse({'exam_id': create_exam.id})

def handle_uploaded_media_file(f):
    timestamp = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    file_relative_path = timestamp + '_' + f.name
    file_path = os.path.join(os.path.dirname(__file__),'upload_file/media', file_relative_path)
    with open(file_path, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return f.name, file_relative_path

def handle_uploaded_image_file(i):
    timestamp = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    file_relative_path = timestamp + '_' + i.name
    file_path = os.path.join(os.path.dirname(__file__),'upload_file/media', file_relative_path)
    with open(file_path, 'wb') as destination:
        for chunk in i.chunks():
            destination.write(chunk)
    return i.name, file_relative_path

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
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    return render(request, 'add_exam_questions.html', {'exam_id': exam_id, 'username': username, 'exam': exam, 'questions': questions, 'videos': videos, 'images': images})

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
    videos = exam.exam_files.filter(type = 'media')
    return render(request, 'show_exam.html', {'exam_id': exam_id, 'username': username, 'exam': exam, 'exam_id': exam_id, 'questions': questions, 'videos': videos})

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
    return HttpResponse("Test result has been sent successfully.<a href=\"/exams\">Go back to exam list</a>")

def show_user_exam_result(request, exam_id, user_id):
    username = Users.objects.get(id = user_id)
    exam = Exams.objects.get(id = exam_id)
    questions = Questions.objects.filter(exam_id = exam_id)
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    user_answers = Option_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id)
    user_answer_list = []
    for user in user_answers:
        user_answer_list.append(user.option_id)
    return render(request, 'show_user_exam_result.html', {'username': username, 'questions': questions, 'user_answer_list': user_answer_list, 'videos': videos, 'images': images, 'exam': exam})

def delete_question(request, exam_id, question_id):
    question_files = Exam_files.objects.filter(question_id = question_id)
    question_files.delete()
    option_users = Option_Users.objects.filter(question_id = question_id)
    option_users.delete()
    options = Options.objects.filter(question_id = question_id)
    options.delete()
    question = Questions.objects.filter(id = question_id)
    question.delete()
    return HttpResponseRedirect(reverse("add_more_questions", kwargs={"exam_id": exam_id}))

def delete_question_media(request, exam_id, question_id, question_media_id):
    question_media_file = Exam_files.objects.get(id = question_media_id)
    question_media_file.delete()
    return HttpResponseRedirect(reverse("add_more_questions", kwargs={"exam_id": exam_id}))

def delete_question_image(request, exam_id, question_id, question_image_id):
    question_image_file = Exam_files.objects.get(id = question_image_id)
    question_image_file.delete()
    return HttpResponseRedirect(reverse("add_more_questions", kwargs={"exam_id": exam_id}))

def delete_option(request, exam_id, option_id):
    option = Options.objects.get(id = option_id)
    option.delete()
    return HttpResponseRedirect(reverse("add_more_questions", kwargs={"exam_id": exam_id}))

def delete_exam(request, exam_id):
    exam = Exams.objects.get(id = exam_id)
    exam.delete()
    return HttpResponseRedirect(reverse("show_exam_list"))