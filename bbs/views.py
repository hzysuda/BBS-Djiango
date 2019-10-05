from django.shortcuts import render, HttpResponse,redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate,login
from bbs.check import check_name, CheckForm
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
import random,os
from bbs.models import *

from bs4 import BeautifulSoup
import markdown

from django.db.models import Count
from django.db.models.functions import TruncMonth
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger

# 定义接口规范

#主页
response_dic = {
        'status': 1,
        'msg': 'ok',
        'data': {}
    }

def index(request):

    article_list = Article.objects.all().order_by('-create_time')
    lately_article_list = Article.objects.all().order_by('-create_time')[0:10]
    blog = Blog.objects.all().first()  # type:Blog
    category_list = Category.objects.all()

    l=[]
    for i in category_list:
        l.append(i.name)
    d5 = dict.fromkeys(l, 0)
    ll=[]
    for article in article_list:
        ll.append(article.article_detail.catagory.name)

    result = {}
    for i in set(ll):
        result[i] = ll.count(i)

    time_list = blog.article_set.all() \
        .annotate(month=TruncMonth('create_time')) \
        .values('month').annotate(c=Count('pk')).order_by('-month')


    for i in time_list:
        y =i["month"].year
        m = i["month"].month
        i["article_detail_list"] =Article.objects.values("title","blog__site","pk").filter(create_time__year=y, create_time__month=m)

    # 分页制作
    try:
        page = request.GET.get('page', 1)


    except PageNotAnInteger:
        page = 1

    p = Paginator(article_list, 5, request=request)

    orgs = p.page(page)

    return render(request,'index.html',locals())



#注销
def logout(request):
    return redirect('/')

#登录 -----------------------------------------------------------------
def my_login(request):
    if request.method == 'GET':
        next_url = request.GET.get('next',0)
        return render(request,'login.html',locals())

    if request.method == "POST":
        client_code = request.POST.get('img_code').lower()
        server_code = request.session.get('img_code').lower()

       
        if client_code != server_code:
            res = JsonResponse({
                'status':2,
                'msg':'验证码错误',
                'data':{}
            })
            return res

        # 验证通过就可以进行用户登录
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url ="/"+username
      
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return JsonResponse({
                'status': 1,
                'msg': "登录成功",
                'data': {
                    'backurl':next_url
                }

            })
        return JsonResponse({
            'status': 2,
            'msg': "登录失败",
            'data': {}

        })


# 注册 -----------------------------------------------------------------
def regsiter(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        check_form = CheckForm(request.POST)
        # 校验

        if check_form.is_valid():
            cleaned_form = check_form.cleaned_data
            cleaned_form.pop('re_password')
            if avatar:
                cleaned_form['avatar'] = avatar
            #数据库插入数据,得到注册用户
            user = User.objects.create_user(**cleaned_form)
            if user:
                # 创建该用户的站点
                u_name=user.username
                blog = Blog.objects.create(
                    site=u_name,
                    title= u_name +"的站点",
                )

                user.blog = blog
                user.save()

                return JsonResponse({
                        'status':1,
                        'msg':"注册成功",
                        'data':{}
                    }
                )

        return JsonResponse({
            'status':2,
            'msg':"注册失败",
            'data':{}
        })


# 校验用户名是否重名 -------------------------------------------------
def check_username(request):

    if request.is_ajax():
        username = request.GET.get('username')
        # 校验
        msg = check_name(username,is_ajax=True)
        response_dic['msg'] = msg
        # print(response_dic['msg'])
        return JsonResponse(response_dic)


#创建画板,保存在服务器本地
def save_local():
    img = Image.new('RBG',(230,32), (40, 20, 10))

    wf = open('code.png','wb')

    img.save(wf,'png')

    with open('code.png','rb')as f:

        data = f.read()

    return data

#随机RGB元组
def random_RGB(min,max):
    return  tuple([random.randint(min,max) for i in range(3)])


# 随机产生六位验证码
def random_six_code():
    code = ""
    for i in range(4):
        tag = random.randint(1,3)
        if tag == 1:
            code += chr(random.randint(65,90))
        elif tag ==2:
            code += chr(random.randint(97,122))
        else:
            code +=str(random.randint(0,9))

    return code


#获取验证码
def login_code(request):
    
    #新建画板  选择model size color
    img = Image.new('RGB', (70, 15), random_RGB(150,255))

    # 在画板中画字
    img_draw = ImageDraw.Draw(img)

    # 设置ImageFont字体
    img_font = ImageFont.truetype('static/font/kumo.ttf', size=16)

    # 获取六位验证码
    img_code = random_six_code()
    # 将img_code存储到session中，与会话绑定，用来完成登录验证码的验证
    request.session['img_code'] = img_code

    # 画文字：xy轴、文本、颜色、ImageFont字体
    for i, ch in enumerate(img_code):
        img_draw.text((5 + i * 16, 0), ch, random_RGB(0, 150), img_font)
    bf = BytesIO()
    img.save(bf,'png')
    data = bf.getvalue()
    return HttpResponse(data)

#后台管理
def backend(request):
    #获取用于文章列表
    article_list = Article.objects.all().filter(blog=request.user.blog).order_by('-create_time','-pk')
    return render(request,'backens/backend.html',locals())

#添加文章
def add_article(request):
    blog = request.user.blog
    if request.method == "GET":
        return render(request,'backens/add_article.html')

    if request.method =="POST":
        title = request.POST.get('titile')
        content = request.POST.get('content')
        category_id = request.POST.get('category_id')
        tag_ids = request.POST.getlist('tag_ids')

        soup = BeautifulSoup(content,'html.parser')
        desc = soup.text.strip()[0:100]

        article = Article.objects.create(
            title = title,
            desc = desc,
            blog= blog,
        )

        article_detail = ArticleDetail.objects.create(
            content=content,
            category_id = category_id,
        )

        article_detail.tag.add(*tag_ids)

        article.article_detail = article_detail
        article.save()

        return redirect('/add_article/')

# 添加文章正文图片
def add_imge(request):
    path = 'media/img'
    #如果没有这个路径 就创建可以这个文件夹
    if not os.path.exists(path):
        os.mkdir(path)
    #从前台获取这个文件数据
    file = request.FILES.get('imgFile')
    #拼接路径
    img_path = path + '/' + file.name
    #写入文件
    with open(img_path,'wb') as f:
        for line in file:
            f.write(line)

    return JsonResponse({
        'error':0,
        'url':'/'+img_path
    })


# 个人站点

#错误页面
def error(request):
    return  render(request,'error.html')


# 个人站点
def site_page(request,site,group=None,key=None):
    blog = Blog.objects.filter(site=site).first() #type:Blog
    if not blog:
        return redirect('/error/')

    # article_list = Article.objects.filter(blog=blog).all().order_by('-create_time','-pk')
    article_list = Article.objects.all().order_by('-create_time')


    # if group and key:
    #     if group == 'category':
    #         article_list = article_list.filter(article_detail__catagory__name=key)
    #     elif group == 'tag':
    #         article_list = article_list.filter(article_detail__tag__name=key)
    #     else:
    #         times = key.splist('-')
    #         article_list = article_list.filter(create_time__year=times[0],create_time_month=times[1])

    return render(request,'site/site.html',locals())


#文章详情
def article_page(request,site,aid):

    blog = Blog.objects.filter(site=site).first() #type:Blog

    article =Article.objects.filter(pk=aid).first()
    # article1 = Article.objects.filter(pk=1).first()

    md=markdown.Markdown(extensions=['markdown.extensions.extra','markdown.extensions.codehilite'])
    article.article_detail.content = md.convert(article.article_detail.content)


    if not blog or not article:
        return redirect('/error/')

    if request.user.is_authenticated():
        is_up = request.user.upordown_set.filter(article=article).values('is_up').first()

        commmet_list = Comment.objects.filter(article=article).all()

    return render(request,'site/article.html', locals())