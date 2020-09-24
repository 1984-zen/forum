from django.shortcuts import render
from forum.models import Boards, Posts, Post_files, Recommands, Recommand_files
from accounts.models import Users
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
import os
from django.http import FileResponse
from django.db.utils import DatabaseError,IntegrityError

def show_boards(request):
    boards = Boards.objects.all().order_by('-created_at')
    count_posts = Posts.objects.all().count()
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    return render(request, 'board.html', {'boards': boards, 'user_id': user_id, 'username': username, 'count_posts': count_posts})

def show_posts(request, board_id):
    board = Boards.objects.get(id = board_id)
    posts = board.posts.preferred_order().filter(other="stuff")
    categorys = board.posts.make_category().filter(other="stuff")
    for post in posts:
        for category in categorys:
            if(category.id == post.id):
                post.category_color_code = category.category_color_code
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    return render(request, 'posts.html', {'posts': posts, 'board_id': board_id, 'user_id': user_id, 'board': board, 'username': username, 'categorys': categorys})

def new_post(request, board_id):
    try:
        title = request.POST.get("title")
        content = request.POST.get("content")
        is_on_top = request.POST.get("on_top_status")
        category = request.POST.get("category")
        user_id = request.session.get('user_id')
        create_post = Posts(title = title, content = content, board_id = board_id, user_id = user_id, other = "stuff", pref = is_on_top, category = category)
        create_post.save()
        files = request.FILES.getlist('myfile')
        if(files):
            for file in files:
                fname, file_relative_path = handle_uploaded_file(file)
                create_file_path = Post_files(name = fname, file_path = file_relative_path, post_id = create_post.id)#拿取剛建立完的create_post.id
                create_file_path.save()
        return HttpResponseRedirect(reverse("show_posts", kwargs={"board_id": board_id}))
    
    except IntegrityError:
        return HttpResponseRedirect(reverse("show_posts", kwargs={"board_id": board_id}))
       
        
def handle_uploaded_file(f):
    today = str(datetime.date.today())
    file_relative_path = today + '_' + f.name
    file_path = os.path.join(os.path.dirname(__file__),'upload_file', file_relative_path)
    with open(file_path, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return f.name, file_relative_path

def download(request, file_relative_path):
    file=open(os.path.join(os.path.dirname(__file__), "upload_file", file_relative_path),'rb')
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition']='attachment;filename="{}"'.format(file_relative_path)
    return response

def show_recommands(request, board_id, post_id):
    board = Boards.objects.get(id = board_id)
    post = Posts.objects.get(id = post_id)
    recommands = post.recommands.all().order_by('-created_at')
    user_id = request.session.get('user_id')
    has_user = Users.objects.filter(id = user_id).count()
    if(has_user):
        user = Users.objects.get(id = user_id)
        username = user.name
    else:
        username = ""
    return render(request, 'recommands.html', {'post_id': post_id, 'recommands': recommands, 'post' : post, 'user_id': user_id, 'board': board, 'username': username})

def new_recommand(request, board_id, post_id,):
    title = request.POST.get("title")
    content = request.POST.get("content")
    user_id = request.session.get('user_id')
    create_recommand = Recommands(title = title, content = content, post_id = post_id, user_id = user_id)
    create_recommand.save()
    files = request.FILES.getlist('myfile')
    if(files):
        for file in files:
            fname, file_relative_path = handle_uploaded_file(file)
            create_file_path = Recommand_files(name = fname, file_path = file_relative_path, recommand_id = create_recommand.id) #拿取剛建立完的recommand.id
            create_file_path.save()
    return HttpResponseRedirect(reverse("show_recommands", kwargs={"board_id": board_id, "post_id": post_id}))

def delete_recommand_file(request, board_id, post_id, recommand_id, file_id):
    recommand_file = Recommand_files(id = file_id)
    recommand_file.delete()
    return HttpResponseRedirect(reverse("show_recommands", kwargs={"board_id": board_id, "post_id": post_id}))

def delete_post(request, board_id, post_id):
    post = Posts.objects.get(id = post_id)
    post.delete()
    return HttpResponseRedirect(reverse("show_posts", kwargs={"board_id": board_id}))

def delete_post_file(request, board_id, post_id, file_id):
    post_file = Post_files(id = file_id)
    post_file.delete()
    return HttpResponseRedirect(reverse("show_posts", kwargs={"board_id": board_id}))

def update_post(request, board_id, post_id):
    post = Posts.objects.get(id = post_id)
    title = post.title
    content = post.content
    if(request.method == 'POST'):
        title = request.POST.get("title")
        content = request.POST.get("content")
        is_on_top = request.POST.get("on_top_status")
        category = request.POST.get("category")
        Posts.objects.filter(id = post_id).update(title = title, content = content, pref = is_on_top, category = category)
        return HttpResponseRedirect(reverse("show_posts", kwargs={"board_id": board_id}))
    return render(request, 'posts_update.html', {'board_id': board_id, 'post_id': post_id, 'title': title, 'content': content, 'post': post})
def delete_recommand(request, board_id, post_id, recommand_id):
    recommand = Recommands.objects.get(id = recommand_id)
    recommand.delete()
    return HttpResponseRedirect(reverse("show_recommands", kwargs={"board_id": board_id, "post_id": post_id}))
def update_recommand(request, board_id, post_id, recommand_id):
    Recommand = Recommands.objects.get(id = recommand_id)
    title = Recommand.title
    content = Recommand.content
    if(request.method == 'POST'):
        title = request.POST.get("title")
        content = request.POST.get("content")
        Recommands.objects.filter(id = recommand_id).update(title = title, content = content)
        return HttpResponseRedirect(reverse("show_recommands", kwargs={"board_id": board_id, "post_id": post_id}))
    return render(request, 'recommand_update.html', {'board_id': board_id, 'post_id': post_id, 'recommand_id': recommand_id, 'title': title, 'content': content})