from django.shortcuts import render
from accounts.models import Users
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.template.response import TemplateResponse

def index(request):
    return TemplateResponse(request, 'index.html', {})

def register(request):
    if(request.method == 'POST'):
        account = request.POST.get("account")
        username = request.POST.get("username")
        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        find_account = Users.objects.filter(account = account).count()
        if(find_account):
            has_account = True
        else:
            has_account = False
        if(has_account):
            return HttpResponseRedirect(reverse("register"))
        if(password == re_password):
            password_sha256 = make_password(password, "123", 'pbkdf2_sha256')
            create_user = Users(name = username, account = account, password = password_sha256)
            create_user.save()
            return HttpResponseRedirect(reverse("login"))
    return render(request, 'register.html')

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
    return HttpResponseRedirect(reverse("login"))