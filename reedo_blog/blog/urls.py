from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r'^login/', views.login, name="login"),
    url(r'^logout/', views.logout_view, name="logout"),
    url(r'^register/', views.register, name="register"),
    url(r"^check_username_exist/", views.check_username_exist, name="check_username_exist"),
    # 极验滑动验证码 获取验证码的url
    url(r'^pc-geetest/register', views.pcgetcaptcha),
    url(r"^check_email_exist/", views.check_email_exist, name="check_email_exist"),

    url(r'^article/(?P<article_id>\d+)/$', views.article_detail, name="article_articles"),
    url(r'^category/(?P<category_id>\d{1,6})/$', views.category_list, name="category_articles"),
    url(r'^dates/$', views.dates_list, name="dates_articles"),
    url(r'^tags/(?P<tag_id>\d{1,6})/$', views.tag_list, name="tags_articles"),
    url(r"^comment/$", views.comment, name="comments"),
    url(r"^about_me/$", views.about_me, name="about_me"),
    url(r"^gustbook/$", views.messages, name="message"),
    url(r"^ajax_message/$", views.ajax_message, name="ajax_message"),
    url(r'^search', views.search,name="search"),

    url(r"^manage/$", views.manager, name="manage_articles"),
    url(r"^manage/draft/$", views.manager_draft, name="draft_articles"),
    url(r"^manage/delete/$", views.delete_article, name="delete_article"),
    url(r"^manage/publish/$", views.publish_article, name="publish_article"),
    url(r"^manage/dispublish/$", views.dispublish_article, name="dispublish_article"),
    url(r"^manage/new_article/$", views.new_article, name="new_article"),

    url(r"^manage/edit/(?P<article_id>\d+)/$", views.edit_article, name="edit_article"),
    url(r"^manage/change_article/$", views.change_article, name="change_article"),
]
