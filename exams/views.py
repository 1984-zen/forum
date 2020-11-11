from django.shortcuts import render
from exams.models import Exams, Questions, Options, Option_Users, Exam_files, Exam_Users
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
from django.utils import timezone, dateformat
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def show_exam_list(request):
    exam_list = Exams.objects.all().order_by('-created_at')
    return TemplateResponse(request, 'exam_list.html', {'exam_list': exam_list})

def show_exam_user_list(request, exam_id):
    exam = Exams.objects.get(id = exam_id)
    user_list = Option_Users.objects.filter(exam_id = exam_id).values_list('user_exam_count', 'user_id').distinct().values('user_exam_count', 'user_id', 'created_at').order_by('user_id', '-created_at') #用('user_exam_count', 'user_id')分組排序user_exam_count是這位考生考exam的次數
    #[{'user_exam_count': 4, 'user_id': 1, 'created_at': datetime.datetime(2020, 11, 4, 11, 58, 14)}]
    user_list_get_name = []
    for user in user_list:
        user_name = Users.objects.get(id = user['user_id'])
        user_list_get_name.append((user['user_exam_count'], user_name, user['created_at'].strftime('%Y-%m-%d %H:%M'), user['user_id']))
        #[(4, <Users: zen>, '2020-11-04')]
    return TemplateResponse(request, 'exam_user_list.html', {'user_list': user_list_get_name, 'exam': exam})

def new_exam(request):
    return render(request, 'new_exam.html', {'username': username})

def get_ajax_answers_options(request):
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
    exam = Exams.objects.get(id = exam_id)
    questions = exam.questions.all()
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    return TemplateResponse(request, 'add_exam_questions.html', {'exam_id': exam_id, 'exam': exam, 'questions': questions, 'videos': videos, 'images': images})

def show_exam(request, exam_id):
    user_id = request.session.get('user_id')
    exam = Exams.objects.get(id = exam_id)
    questions = exam.questions.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(questions, 1)
    questions_in_page = paginator.page(page)
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(status = 0)[0].id
    user_has_been_answered = Option_Users.objects.filter(exam_users_id = exam_users_id).values_list('question_id', flat=True)
    return TemplateResponse(request, 'show_exam.html', {'exam_id': exam_id, 'exam': exam, 'exam_id': exam_id, 'questions_in_page': questions_in_page, 'videos': videos, 'images': images, 'user_has_been_answered': user_has_been_answered})

def user_answers(request, exam_id):
    user_id = request.session.get('user_id')
    exam_id = exam_id
    current_page = request.POST.get('current_page', '/')
    option_ids_list = request.POST.getlist("option_id[]")
    if(not option_ids_list):
        messages.error(request, "You have not selected any answer!")
        return HttpResponseRedirect(current_page)
    has_incomplete_exam_record = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(status = 0).count()#找出user在交卷紀錄裡面是否有status = 0的紀錄
    if(has_incomplete_exam_record):#如果user有尚未交卷的紀錄就讓user繼續作答
        for option_id in option_ids_list:
            question_id = Options.objects.filter(id = option_id)[0].question_id
            exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(status = 0)[0].id #目前user尚未完成的考卷id
            # user_answer_count = Option_Users.objects.filter(question_id = question_id).count()
            # user_exam_count = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).count() #算出這個user在這個exam考了幾次
            create_option_users = Option_Users(user_id = user_id, option_id = option_id, question_id = question_id, exam_id = exam_id, exam_users_id = exam_users_id) #把user答案寫入DB
            create_option_users.save()
        messages.success(request, "Answer has been sent successfully!")
    else:#表示user之前都交卷了，給他創建新的考卷，status = 0
        create_exam_users = Exam_Users(user_id = user_id, exam_id = exam_id, date = datetime.datetime.now(), status = 0)
        create_exam_users.save() #user作答完就紀錄在exam_user上，用來計算他是第幾次應考
        for option_id in option_ids_list:
            question_id = Options.objects.filter(id = option_id)[0].question_id
            exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(status = 0)[0].id #目前user尚未完成的考卷id
            create_option_users = Option_Users(user_id = user_id, option_id = option_id, question_id = question_id, exam_id = exam_id, exam_users_id = exam_users_id) #把user答案寫入DB
            create_option_users.save()
        messages.success(request, "Has sent successfully!")
    return HttpResponseRedirect(current_page)

def user_finish_exam(request, exam_id):
    user_id = request.session.get('user_id')
    exam_id = exam_id
    return HttpResponse("Test result has been sent successfully.<a href=\"/exams\">Go back to exam list</a>")

def show_user_exam_result(request, exam_id, user_id, user_exam_count):
    exam = Exams.objects.get(id = exam_id)
    questions = Questions.objects.filter(exam_id = exam_id)
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    user_answers = Option_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(user_exam_count = user_exam_count)
    user_answer_list = []
    for user in user_answers:
        user_answer_list.append(user.option_id)
    return TemplateResponse(request, 'show_user_exam_result.html', {'questions': questions, 'user_answer_list': user_answer_list, 'videos': videos, 'images': images, 'exam': exam})

def delete_question(request, exam_id, question_id):
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