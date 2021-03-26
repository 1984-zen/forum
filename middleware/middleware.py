from django.http import HttpResponse
from django.http import HttpResponseRedirect
from accounts.models import Users
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CheckUserAuthorizationMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    # process_view(), process_exception(), process_template_response()
    # special methods to class-based middleware

    def process_view(self, request, view_func, view_args, view_kwargs):
        # process_view() is called just before Django calls the view.
        # It should return either None or an HttpResponse object
        user_id = request.session.get('user_id')
        has_user = Users.objects.filter(id = user_id).count()
        is_super_admin = Users.objects.filter(id = user_id).filter(is_admin = 2).count()
        is_admin = Users.objects.filter(id = user_id).filter(is_admin = 1).count()
        
        
        if (view_func.__name__ == "delete_exam"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))
                
        if (view_func.__name__ == "update_question"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "update_next_question_id"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))
                
        if (view_func.__name__ == "login"):
            if(has_user): #如果具有member身分
                return HttpResponseRedirect(reverse("index")) # 回傳None可以繼續往下一個middleware走
            else: #如果不具有member身分的話
                return None
                
        if (view_func.__name__ == "show_exam"):
            if(has_user): #如果具有member身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有member身分的話
                messages.error(request, "you have no authority to access this router, please log in")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "new_recommand"):
            if(has_user): #如果具有member身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有member身分的話
                messages.error(request, "you have no authority to access this router, please log in")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "new_post"):
            if(has_user): #如果具有member身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router, please log in")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "show_user_exam_result"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "add_exam_questions"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "show_exam_user_list"):
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "new_exam"): #可透過Django轉址
            if(is_admin or is_super_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router")
                return HttpResponseRedirect(reverse("show_exam_list"))

        if (view_func.__name__ == "get_ajax_answers_options"): #必須透過ajax轉址，所以獨立寫出來這if
            if(is_admin or is_super_admin): #如果具有admin身分
                return None 
                # return view_func(request, *view_args, **view_kwargs) #同上return None，也能讓middleware允許繼續執行這view
            else: #如果不具有admin身分的話就讓前端ajax的success去redirect回到"show_exam_list"頁面
                messages.error(request, "you have no authority to access this router")
                return JsonResponse({
                'success': True,
                'redirect': reverse('show_exam_list')})
        ##########################################################labelMe
        if (view_func.__name__ == "show_label_list"):
            if(is_admin): #如果具有admin身分
                return None # 回傳None可以繼續往下一個middleware走
            else: #如果不具有admin身分的話
                messages.error(request, "you have no authority to access this router, please log in")
                return HttpResponseRedirect(reverse("show_training_list"))

        return None # 回傳None可以繼續往下一個middleware走

    def process_exception(self, request, exception):
        # Django calls process_exception() when a view raises an exception
        # It should return either None or an HttpResponse object
        logger.warning('---- exception.args ----')
        return None

    def process_template_response(self, request, response): #物件reponse下有context_data["key"]可傳送給template{{ key }}使用
        # return TemplateResponse object
        user_id = request.session.get('user_id')
        has_user = Users.objects.filter(id = user_id).count()
        if(has_user):
            user_name = Users.objects.get(id = user_id).username
            response.context_data["user_name"] = user_name #把user_name會透過view的TemplateResponse去傳到全部template
        is_admin = Users.objects.filter(id = user_id).filter(is_admin = 1).count()
        if(is_admin):
            response.context_data["is_admin"] = True
        else:
            response.context_data["is_admin"] = False
        is_super_admin = Users.objects.filter(id = user_id).filter(is_admin = 2).count()
        if(is_super_admin):
            response.context_data["is_super_admin"] = True
        else:
            response.context_data["is_super_admin"] = False
        return response