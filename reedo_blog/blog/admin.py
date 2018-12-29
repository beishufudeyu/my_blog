from django.contrib import admin
from blog import models
from django_summernote.admin import SummernoteModelAdmin

@admin.register(models.UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "is_superuser", "username", "email", "is_active")
    # 定制列可以点击跳转
    list_display_links = ('id', "username", "email",)
    # 定制右侧快速筛选。
    list_filter = ("is_superuser", "is_active")
    # 列表时，模糊搜索的功能
    search_fields = ('username', 'email')


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "title", "published", "comment_count", "category", "user")
    # 定制列可以点击跳转
    list_display_links = ('id', "title",)
    # 定制右侧快速筛选。
    list_filter = ("category","user")
    # 列表时，模糊搜索的功能
    search_fields = ("title", "category","user")


@admin.register(models.ArticleDetail)
class ArticleDetailAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "article")
    # 定制列可以点击跳转
    list_display_links = ("id",)
    # 列表时，模糊搜索的功能
    search_fields = ("article",)
    summernote_fields = ('content',)



@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("article", "user", "create_time")
    # 定制列可以点击跳转
    list_display_links = ('article',)
    # 定制右侧快速筛选。
    list_filter = ("user", "create_time")
    # 列表时，模糊搜索的功能
    search_fields = ("article", "user", "create_time")


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "title",)
    # 定制列可以点击跳转
    list_display_links = ('id', "title",)
    # 定制右侧快速筛选。
    list_filter = ("title",)
    # 列表时，模糊搜索的功能
    search_fields = ("title",)


@admin.register(models.Article2Tag)
class Article2TagAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("article", "tag",)
    # 定制列可以点击跳转
    list_display_links = ("article", "tag",)
    # 定制右侧快速筛选。
    list_filter = ("tag",)
    # 列表时，模糊搜索的功能
    search_fields = ("article", "tag",)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "title",)
    # 定制列可以点击跳转
    list_display_links = ('id', "title",)
    # 定制右侧快速筛选。
    list_filter = ("title",)
    # 列表时，模糊搜索的功能
    search_fields = ("title",)

@admin.register(models.Messages)
class MessagesAdmin(admin.ModelAdmin):
    # 定制显示的列
    list_display = ("id", "create_time",)
    # 定制列可以点击跳转
    list_display_links = ('id', "create_time",)
    # 定制右侧快速筛选。
    list_filter = ("create_time",)
    # 列表时，模糊搜索的功能
    search_fields = ("content",)