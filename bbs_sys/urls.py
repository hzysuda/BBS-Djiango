"""bbs_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from bbs import views
from django.views.static import serve
from bbs_sys import settings

urlpatterns = [
    url('admin/', admin.site.urls),
    # #注册用户
    url('^register/$',views.regsiter),
    # 登录界面
    url(r'^index/$',views.index),
    url(r'^$', views.index),
    url(r'^login$', views.my_login),
    url(r'^login/$', views.my_login),
    #
    #检验用户是否重名
    url(r'^check_username/$', views.check_username),

    #获取静态码
    url(r'^login_code/$', views.login_code),
    #主页

    #后台管理
    url(r'^backend/$',views.backend),
    #添加文章
    url('^add_article/$',views.add_article),
    url('^add_article$',views.add_article),
    # 用户上传的静态文件，可以在外网通过接口可以直接访问
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

    #注销
    url('^logout/$', views.logout),
    #错误
    url('^error/$',views.error),
    #文章详情
    url(r'^(?P<site>\w+)/article/(?P<aid>\d+).html$', views.article_page),

    # 个人站点
    url(r'^(?P<site>\w+)/(?P<group>category|tag|archive)/(?P<key>.+)$', views.site_page),

    url(r'^(?P<site>\w+)$', views.site_page),
    url(r'^(?P<site>\w+)/$', views.site_page),
    url('^.*$',views.error),
]
