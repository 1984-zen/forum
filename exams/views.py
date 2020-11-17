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
from openpyxl import Workbook


def show_exam_list(request):
    exam_list = Exams.objects.all().order_by('-created_at')
    return TemplateResponse(request, 'exam_list.html', {'exam_list': exam_list})

def show_exam_user_list(request, exam_id):
    user_list = Exam_Users.objects.filter(exam_id = exam_id).exclude(count = 0).select_related('user').values('user__id', 'user__name', 'date', 'count')
    exam = Exams.objects.get(id = exam_id)
    return TemplateResponse(request, 'exam_user_list.html', {'user_list': user_list, 'exam': exam})

def new_exam(request):
    return TemplateResponse(request, 'new_exam.html', {})

def get_ajax_answers_options(request):
    user_id = request.session.get('user_id')
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
    has_user_incomplete_record = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0).count() #找到user未完成的考卷count = 0
    if(has_user_incomplete_record):
        exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0)[0].id
        user_has_been_answered = Option_Users.objects.filter(exam_users_id = exam_users_id).values_list('question_id', flat=True)
    else:
        user_has_been_answered = []
    return TemplateResponse(request, 'show_exam.html', {'user_id': user_id, 'exam_id': exam_id, 'exam': exam, 'exam_id': exam_id, 'questions_in_page': questions_in_page, 'videos': videos, 'images': images, 'user_has_been_answered': user_has_been_answered})

def user_answers(request, exam_id):
    user_id = request.session.get('user_id')
    exam_id = exam_id
    current_page = request.POST.get('current_page') #從前端的input有個name叫做"current_page"，印出型別是str，所以next_page要加1之前要轉int()
    option_ids_list = request.POST.getlist("option_id[]")
    if(not option_ids_list): #如果考生沒有勾選答案就提交就回到原本題目
        messages.error(request, "You have not selected any answer!")
        return HttpResponseRedirect(reverse('show_exam', kwargs={"exam_id": exam_id}) + "?page=" + current_page) #跳回到同一題
    has_incomplete_exam_record = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0).count()#找出user在交卷紀錄裡面是否有count = 0的紀錄
    if(has_incomplete_exam_record):#如果user有尚未交卷的紀錄就讓user繼續作答
        for option_id in option_ids_list:
            question_id = Options.objects.filter(id = option_id)[0].question_id
            exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0)[0].id #目前user尚未完成的考卷id
            create_option_users = Option_Users(user_id = user_id, option_id = option_id, question_id = question_id, exam_id = exam_id, exam_users_id = exam_users_id) #把user答案寫入DB
            create_option_users.save()
        messages.success(request, "Answer has been sent successfully!")
    else:#表示user之前都交卷了，給他創建新的考卷，count = 0
        create_exam_users = Exam_Users(user_id = user_id, exam_id = exam_id, date = datetime.datetime.now(), count = 0)
        create_exam_users.save() #user作答完就紀錄在exam_user上，用來計算他是第幾次應考
        for option_id in option_ids_list:
            question_id = Options.objects.filter(id = option_id)[0].question_id
            exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0)[0].id #目前user尚未完成的考卷id
            create_option_users = Option_Users(user_id = user_id, option_id = option_id, question_id = question_id, exam_id = exam_id, exam_users_id = exam_users_id) #把user答案寫入DB
            create_option_users.save()
        messages.success(request, "Has sent successfully!")
    return HttpResponseRedirect(reverse('show_exam', kwargs={"exam_id": exam_id}) + "?page=" + int(current_page) + 1) #跳到下一題

def user_exam_completed(request, exam_id, user_id):
    user_id = request.session.get('user_id')
    exam_id = exam_id
    user_has_completed_exam_count = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 1).count() #算出已完成考試的數量
    update_exam_users_count_to_1 = Exam_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(count = 0) #找到user未完成的考卷count = 0
    update_exam_users_count_to_1.update(count = user_has_completed_exam_count + 1) #已完成考試的MAX數量+1
    return HttpResponse("Finished!! All answers have been sent successfully.<a href=\"/exams\">Go back to exam list</a>")

def show_user_exam_result(request, exam_id, user_id, user_exam_count):
    exam = Exams.objects.get(id = exam_id)
    questions = Questions.objects.filter(exam_id = exam_id)
    videos = exam.exam_files.filter(type = 'media')
    images = exam.exam_files.filter(type = 'image')
    page = request.GET.get('page', 1)
    paginator = Paginator(questions, 1)
    questions_in_page = paginator.page(page)

    exam_users_id = Exam_Users.objects.filter(user_id = user_id).filter(exam_id =exam_id).filter(count = user_exam_count)[0].id
    user_answers = Option_Users.objects.filter(user_id = user_id).filter(exam_id = exam_id).filter(exam_users_id = exam_users_id)
    user_answer_list = [] #user再這張exam所勾選過的選項
    for user in user_answers:
        user_answer_list.append(user.option_id) #把所有user對這張exam的所有勾選的option都存進到user_answer_list
    return TemplateResponse(request, 'show_user_exam_result.html', {'questions_in_page': questions_in_page, 'user_answer_list': user_answer_list, 'videos': videos, 'images': images, 'exam': exam})

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

def export_user_answer_xls(request, exam_id, user_id, user_exam_count):
    user_name = Users.objects.get(id = user_id).name
    exam_date = Exam_Users.objects.filter(exam_id = exam_id).filter(user_id = user_id).filter(count = user_exam_count).values('date')[0]['date'].strftime('%Y-%m-%d_%H%M')
    exam_title = Exams.objects.get(id = exam_id).name
    response = HttpResponse(content_type='application/ms-excel') #匯出excel是用response的content-type
    response['Content-Disposition'] = f"attachment; filename = {user_name}_answer_{exam_date}.xlsx" #匯出excel的檔名

    wb = Workbook()
    wb.create_sheet()
    ws = wb.active #拿到地1個sheet[0]
    ws.title = f"{user_name}_answer_{exam_date}" #命名sheet名稱

    questions = Questions.objects.filter(exam_id = 217).values('id') #考捲id=217
    #[{'id': 1724}, {'id': 1725}...]
    user_answers = Option_Users.objects.filter(exam_id = 217).filter(user_id = user_id).select_related('option').values('question_id','option__option')
    #<QuerySet [{'question_id': 1728, 'option__option': 'Apical 3-chamber–color'},...]

    #開始寫入excel
    #寫入欄位
    ws.cell(1, 1).value = '試卷名稱_Exam_title' # row=1, col=1欄位名稱'試卷名稱_Exam_title'
    ws.cell(2, 1).value = 'Question' # row=2, col=1欄位名稱'Question'
    ws.cell(2, 2).value = 'Answers' # row=2, col=2欄位名稱'Answers'

    #寫入內容
    ws.cell(1, 2).value = exam_title # row=1, col=2'Exam_title'
    for i in range(len(questions)): #印出題目的流水號從1~13809
        ws.cell(i+3, 1).value = i + 1 #question流水號從1開始
        for user_answer in user_answers: #user_answers[]
            if(user_answer['question_id'] == questions[i]['id']): #檢查user有回答這個question的話...就紀錄user勾選的選項
                count_user_answer_has_more_than_one = Option_Users.objects.filter(exam_id = exam_id).filter(user_id = user_id).filter(question_id = user_answer['question_id']).values('question_id','option__option')#如果user複選的話...
                for j in range(count_user_answer_has_more_than_one.count()): #用for迴圈去橫向紀錄在excel表格
                    ws.cell(i+3, 2+j).value = count_user_answer_has_more_than_one[j]['option__option'] #user勾選的ansers從row=3, col=2...col=2+j寫入
    wb.save(response) #存檔
    return response #匯出到瀏覽器下載