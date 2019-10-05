from django.template import Library
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = Library()

@register.inclusion_tag('site/menu_list.html',name='menu_list_tag')
def menu_list(blog):
    # 该站点下的分组与该分组下的文章数
    # [(py, 2), (h5, 1), (java, 1)]
    category_set = blog.category.all().filter(articledetail__article__blog=blog).values('name').annotate(c=Count('articledetail')) \
        .values_list('name', 'c')

    # 标签
    # [{'name': '个人', 'c': 6}, {'name': '大牛', 'c': 5}, {'name': '技术', 'c': 6}]
    tag_list = blog.tag.all() \
        .filter(articledetail__article__blog=blog) \
        .values('name').annotate(c=Count('articledetail'))

    article_list = blog.article_set.all().order_by('-create_time')

    # 档案
    # [{'month': datetime.date(2018, 3, 1), 'c': 1}, {'month': datetime.date(2019, 2, 1), 'c': 2}, {'month': datetime.date(2019, 3, 1), 'c': 1}]>
    time_list = blog.article_set.all().annotate(month=TruncMonth('create_time')) \
                .values('month').annotate(c=Count('pk')).order_by('-month')

    for i in time_list:
        y =i["month"].year
        m = i["month"].month
        i["article_detail_list"] =blog.article_set.values("title","blog__site","pk").filter(create_time__year=y, create_time__month=m)


    res = { 'category': category_set,
            'tag_list': tag_list,
            'time_list': time_list,
            'article_list':article_list
    }

    return res