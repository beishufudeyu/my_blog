from django import template
from blog import models
from django.db.models import Count

register = template.Library()



@register.inclusion_tag("articles/category_bar.html")
def category_bar():
    category_list = models.Category.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    # 查文章标签及对应的文章数
    return {"category_list": category_list,}

@register.inclusion_tag("articles/tags_bar.html")
def tag_bar():
    tag_list = models.Tag.objects.all().annotate(c=Count("article")).values("id", "title", "c")
    return {"tag_list": tag_list,}

@register.filter(name="str_format")
def str_format(value):
    return str(value)


@register.filter(name="remainder")
def str_format(value):
    result = value % 2
    return result
