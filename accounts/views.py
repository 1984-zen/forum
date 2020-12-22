from django.shortcuts import render
from accounts.models import Users
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.template.response import TemplateResponse
from accounts.forms import RegisterForm

def index(request):
    return TemplateResponse(request, 'index.html', {})

def register(request):
    if(request.method == 'POST'):
        f = RegisterForm(request.POST) #獲取驗證資料的結果，從forms.py表單驗證user輸入的資料，request.POST就是user輸入的資料
        if f.is_valid(): #如果所有欄位都驗證通過的話
            account = f.cleaned_data.get("account") #拿取驗證通過的account值
            username = f.cleaned_data.get("username")
            password = f.cleaned_data.get("password")
            re_password = f.cleaned_data.get("re_password")
            find_account = Users.objects.filter(account = account).count()
            if(find_account):
                has_account = True
            else:
                has_account = False
            if(has_account):
                messages.error(request, "This account has been registerd!")
                return HttpResponseRedirect(reverse("login")) #如果這組帳號已經被註冊就redirect回log in畫面
            if(password == re_password):
                password_sha256 = make_password(password, "123", 'pbkdf2_sha256')
                create_user = Users(username = username, account = account, password = password_sha256, email = account, is_active = 1)
                create_user.save()
                messages.success(request, "Rgister successfully!")
                return HttpResponseRedirect(reverse("login"))
        else: #如果其中有一項沒有通過驗證
            f = RegisterForm(request.POST) #獲取驗證資料的結果
            return render(request, 'register.html', {'f': f}) #就逐一的回報錯誤訊息讓user知道
    else:
        f = RegisterForm() #再還沒user輸入的時候給她空白的表單
    return render(request, 'register.html', {'f': f})

def login(request):
    return render(request, 'login.html')

def login_post(request):
    if(request.method == 'POST'):
        try:
            account = request.POST.get("account")
            password = request.POST.get("password")
            user = Users.objects.get(account = account)
            if(check_password(password, user.password)):
                request.session['user_id'] = user.id
                messages.success(request, "Log in successfully!")
                return HttpResponseRedirect(reverse("index")) #登入成功就去index.html
            else:
                messages.error(request, "account or password is wrong!")
                return HttpResponseRedirect(reverse("login"))
        except Users.DoesNotExist:
            messages.error(request, "account or password is wrong!")
            return HttpResponseRedirect(reverse("login"))
    return render(request, 'login.html')

def logout(request):
    del request.session['user_id']
    messages.success(request, "Log out successfully!")
    return HttpResponseRedirect(reverse("login"))