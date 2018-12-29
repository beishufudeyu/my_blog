from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from geetest import GeetestLib
from blog import forms, models
from django.db.models import F, Count
from . import paginator_tool
from .xss_tag_filter import xss_filter
from bs4 import BeautifulSoup

# 使用极验滑动验证码的登录
# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def validate_article(article, user):
    flag = False
    user_article_list = models.Article.objects.filter(user=user).all()
    if article in user_article_list:
        flag = True
    return flag


# 处理极验 获取验证码的视图
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 登陆的视图函数
def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 从URL里面取到 next 参数
        next_url = request.GET.get("next")
        # 是否记住用户
        remember_me = request.POST.get("remember_me")

        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        # 验证通过
        if result:
            # 利用auth模块做用户名和密码的校验
            # 判断是用户名还是邮箱登陆
            user_login = auth.authenticate(username=username, password=pwd)
            email_login = auth.authenticate(email=username, password=pwd)
            # 用户名密码正确
            if user_login or email_login:
                # 用用户名登陆
                if user_login:
                    auth.login(request, user_login)
                # 用邮箱登陆
                else:
                    auth.login(request, email_login)
                # 如果是记住用户，设置为7天免登陆
                if remember_me == "true":
                    request.session.set_expiry(604800)
                # 如果不是，关闭浏览器失效
                else:
                    request.session.set_expiry(0)
                # 如果有跳转下一url，跳转
                if next_url:
                    ret["msg"] = next_url
                # 无，默认跳转index页面
                else:
                    ret["msg"] = "/"
            else:
                # 用户名密码错误，返回错误信息
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "common/login.html")


# 注册的视图函数
def register(request):
    if request.is_ajax():
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret["msg"] = "/login/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    return render(request, "common/register.html", {"form_obj": form_obj})


# 判断用户名是否已存在
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    is_exist = models.UserInfo.objects.filter(username=username).first()
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册！"
    return JsonResponse(ret)


# 判断邮箱是否已存在
def check_email_exist(request):
    ret = {"status": 0, "msg": ""}
    email = request.GET.get("email")
    is_exist = models.UserInfo.objects.filter(email=email).first()
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "邮箱已被使用！"
    return JsonResponse(ret)


# 注销函数
@login_required(login_url="/login/")
def logout_view(request):
    auth.logout(request)
    return redirect("/login/")


# 主页
def index(request):
    article_list = models.Article.objects.filter(published=True).order_by("-create_time")
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(article_list, page_num)
    result = {"article_list": page_list[0], "current_page_num": page_list[1],
              "page_range": page_list[2], "title": "主页"}
    return render(request, "articles/article_index.html", result)


# 文章详情页
def article_detail(request, article_id):
    article = models.Article.objects.filter(pk=article_id).first()
    is_read = request.COOKIES.get("is_read")
    if is_read is None:
        article.read_num += 1
        article.save()
    # 找到当前的文章
    comment_list = models.Comment.objects.filter(article=article).all()
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(comment_list, page_num)
    previous_article = article.pre_article()
    next_article = article.next_article()
    rep = render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "previous": previous_article,
            "next": next_article,
            "comment_list": page_list[0], "current_page_num": page_list[1],
            "page_range": page_list[2],
        }
    )
    rep.set_cookie("is_read", True, max_age=60)
    return rep


# 文章详情页
def messages(request):
    message_list = models.Messages.objects.all()
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(message_list, page_num)
    return render(
        request,
        "articles/article_gustbook.html",
        {
            "message_list": page_list[0], "current_page_num": page_list[1],
            "page_range": page_list[2],
        }
    )


# 分类集合页
def category_list(request, category_id):
    article_list = models.Article.objects.filter(category__id=category_id).all().filter(published=True)
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(article_list, page_num)
    result = {"article_list": page_list[0], "current_page_num": page_list[1],
              "page_range": page_list[2], "title": "分类集合"}
    return render(request, "articles/article_index.html", result)


# 归档页
def dates_list(request):
    blog_dates = models.Article.objects.filter(published=True).datetimes('create_time', 'month', order='DESC').all()
    article_dict = {}
    for i in blog_dates:
        date = str(i.year) + '-' + str(i.month)
        article_list = models.Article.objects.filter(create_time__year=i.year, create_time__month=i.month).filter(
            published=True)
        article_dict[date] = article_list
    return render(request, "articles/article_archives.html", {"article_dict": article_dict, })


# 标签页
def tag_list(request, tag_id):
    article_list = models.Article.objects.filter(tags__article2tag__tag=tag_id).all().filter(published=True)
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(article_list, page_num)
    result = {"article_list": page_list[0], "current_page_num": page_list[1],
              "page_range": page_list[2], "title": "标签集合"}
    return render(request, "articles/article_index.html", result)


# 评论ajax提交
@login_required(login_url="/login/")
def comment(request):
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user = request.user
    response = {}
    if len(content.strip()) == 0:
        response["error"] = "评论不能为空"
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, user=user, content=content)
        article = models.Article.objects.get(id=article_id)
        article.comment_count += 1
        article.save()
        response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        response["content"] = comment_obj.content
        response["comment_id"] = comment_obj.id
        response["username"] = comment_obj.user.username
    return JsonResponse(response)


# 留言ajax提交
@login_required(login_url="/login/")
def ajax_message(request):
    content = request.POST.get("content")
    user = request.user
    response = {}
    if len(content.strip()) == 0:
        response["error"] = "留言不能为空"
    else:
        message_obj = models.Messages.objects.create(user=user, content=content)
        response["create_time"] = message_obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        response["content"] = message_obj.content
        response["message_id"] = message_obj.id
        response["username"] = message_obj.user.username
    return JsonResponse(response)


# 关于我
def about_me(request):
    return render(request, "articles/article_link.html")


def search(request):
    s_name = request.GET.get("s", None)
    article_list = models.Article.objects.filter(title__icontains=s_name).all()
    count_num = article_list.count()
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(article_list, page_num)
    result = {"article_list": page_list[0], "current_page_num": page_list[1],
              "page_range": page_list[2], "s_name": s_name, "count_num": count_num}
    return render(request, "articles/article_search.html", result)


# 我的空间
@login_required(login_url="/login/")
def manager(request):
    user = request.user
    article_list = models.Article.objects.filter(user=user).all().filter(published=True)
    page_num = request.GET.get("page", 1)
    page_list = paginator_tool.page_paginator(article_list, page_num)
    category_list = models.Category.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    return render(request, "manage/user_manage.html",
                  {"article_list": page_list[0], "category_list": category_list, "page_list": page_list,
                   "page_range": page_list[2], })


# 草稿箱
@login_required(login_url="/login/")
def manager_draft(request):
    user = request.user
    article_list = models.Article.objects.filter(user=user).all().filter(published=False)
    page_num = request.GET.get("page", 1)
    category_list = models.Category.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    page_list = paginator_tool.page_paginator(article_list, page_num)
    return render(request, "manage/user_manager_draft.html",
                  {"article_list": page_list[0], "category_list": category_list, "page_list": page_list,
                   "page_range": page_list[2], })


# 删除文章
@login_required(login_url="/login/")
def delete_article(request):
    response = {}
    article_id = request.POST.get("article_id")
    user = request.user
    article = models.Article.objects.get(id=article_id)
    try:
        flag = validate_article(article, user)
        if flag:
            article.delete()
        else:
            response["error"] = "你不能删除不属于你的文章!!!"
    except Exception:
        response["error"] = "该文章不存在!!!"
    return JsonResponse(response)


# 取消发布
@login_required(login_url="/login/")
def dispublish_article(request):
    response = {}
    article_id = request.POST.get("article_id")
    user = request.user
    article = models.Article.objects.get(id=article_id)
    try:
        flag = validate_article(article, user)
        if flag:
            article.published = False
            article.save()
            response["img"] = "取消发布成功!!!"
        else:
            response["error"] = "你不能取消发布不属于你的文章!!!"
    except Exception:
        response["error"] = "该文章不存在!!!"
    return JsonResponse(response)


# 发布
@login_required(login_url="/login/")
def publish_article(request):
    response = {}
    article_id = request.POST.get("article_id")
    user = request.user
    article = models.Article.objects.get(id=article_id)
    try:
        flag = validate_article(article, user)
        if flag:
            article.published = True
            article.save()
            response["img"] = "发布成功!!!"
        else:
            response["error"] = "你不能发布不属于你的文章!!!"
    except Exception:
        response["error"] = "该文章不存在!!!"
    return JsonResponse(response)


# 新建文章
@login_required(login_url="/login/")
def new_article(request):
    if request.method == "POST":
        ret = {"status": 1, "msg": ""}
        # 获取传来的信息
        tags = list(request.POST.get("tags"))
        title = request.POST.get("title")
        published = request.POST.get("published")
        category = int(request.POST.get("category"))
        content = request.POST.get("content")
        user = request.user

        content = xss_filter.process(content)
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.get_text()[:150] + "..."

        # 处理传来的信息
        if published == "true":
            published = True
        else:
            published = False
        my_tags_list = []
        for i in list(tags):
            if i != ",":
                my_tags_list.append(int(i))

        # 验证传来的信息
        if not user:
            ret["msg"] = "您必须登陆!!!"
        if len(title.strip()) == 0:
            ret["msg"] = "标题不能为空"
            return JsonResponse(ret)
        if len(content.strip()) == 0:
            ret["msg"] = "内容不能为空"
            return JsonResponse(ret)
        if not category:
            ret["msg"] = "必须需要一个分类"
            return JsonResponse(ret)

        # 创建新文章
        try:
            # pass
            article = models.Article.objects.create(title=title, desc=desc, published=published, category_id=category,
                                                    user=user)
            models.ArticleDetail.objects.create(content=content, article=article)
            for i in my_tags_list:
                models.Article2Tag.objects.create(article=article, tag_id=i)
            ret["status"] = 0
            ret["msg"] = "/manage/"
        except Exception:
            ret["status"] = 1
            ret["msg"] = "创建文章错误!!!"
        return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.ArticleForm()
    category_list = models.Category.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    return render(request, "manage/new_article.html", {"form_obj": form_obj, "category_list": category_list})


# 编辑文章
@login_required(login_url="/login/")
def edit_article(request, article_id):
    article = models.Article.objects.get(id=article_id)
    form_obj = forms.ArticleDetailForm()
    user = request.user
    category_list = models.Category.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    try:
        flag = validate_article(article, user)
        if flag:
            tag_list = []
            tags = article.tags.values("id")
            for i in tags:
                tag_list.append(str(i["id"]))
            tag_str = ",".join(tag_list)
            select_category = article.category_id
            select_published = article.published
            content = article.articledetail.content
            category = models.Category.objects.all().values_list("id", "title")
            tags = models.Tag.objects.all().values_list("id", "title")
        else:
            return HttpResponse("你不能编辑不属于你的文章!!!")
    except Exception as e:
        return HttpResponse("该文章不存在!!!")
    return render(request, "manage/edit_article.html",
                  {"article": article, "select_tag": tag_str, "select_category": select_category,
                   "category": category, "tags": tags,
                   "select_published": select_published, "category_list": category_list, "form_obj": form_obj,"content":content})



# 编辑提交处理文章
@login_required(login_url="/login/")
def change_article(request):
    if request.method == "POST":
        ret = {"status": 1, "msg": ""}
        article_id = request.POST.get("article_id")
        tags = list(request.POST.get("tags"))
        title = request.POST.get("title")
        published = request.POST.get("published")
        category = int(request.POST.get("category"))
        content_text = request.POST.get("content")
        user = request.user
        content = xss_filter.process(content_text)
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.get_text()[:150] + "..."


        if published == "true":
            published = True
        else:
            published = False

        my_tags_list = []
        for i in list(tags):
            if i != ",":
                my_tags_list.append(int(i))

        if not user:
            ret["msg"] = "您必须登陆!!!"
        if len(title.strip()) == 0:
            ret["msg"] = "标题不能为空"
            return JsonResponse(ret)
        if len(content.strip()) == 0:
            ret["msg"] = "内容不能为空"
            return JsonResponse(ret)
        if not category:
            ret["msg"] = "必须需要一个分类"
            return JsonResponse(ret)

        try:
            article_obj = models.Article.objects.get(id=article_id)
            flag = validate_article(article_obj, user)

            if flag:
                article_obj.published = published
                article_obj.title = title
                article_obj.category_id = category
                article_obj.desc = desc
                article_obj.save()
                aaa = models.ArticleDetail.objects.filter(article=article_obj).update(content=content)
                # models.Article.objects.get(id=article_id).update(published=published,title=title,category_id=category,)

                article_obj.tags.clear()
                for i in my_tags_list:
                    models.Article2Tag.objects.create(article=article_obj, tag_id=i)
                ret["status"] = 0
                ret["msg"] = "/manage/"
            else:
                ret["status"] = 1
                ret["msg"] = "你不能修改不属于你的文章!!!"
        except Exception as e:
            ret["status"] = 1
            ret["msg"] = "修改文章错误!!!"
        return JsonResponse(ret)
