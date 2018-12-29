from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class UserInfo(AbstractUser):
    """
    用户信息表
    """
    avatar = models.FileField(upload_to="avatars/", default="avatars/default.png", verbose_name="头像")
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    个人博客文章分类
    """
    title = models.CharField(max_length=32)  # 分类标题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
    标签
    """
    title = models.CharField(max_length=32)  # 标签名

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章
    """
    title = models.CharField(max_length=32, verbose_name="文章标题")  # 文章标题
    desc = models.CharField(max_length=255)  # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间  --> datetime()

    # 评论数
    read_num = models.IntegerField(verbose_name="阅读数",default=0)
    comment_count = models.IntegerField(verbose_name="评论数", default=0)
    published = models.BooleanField(verbose_name="发布", default=1)

    category = models.ForeignKey(to="Category", to_field="id")
    user = models.ForeignKey(to="UserInfo", to_field="id")
    tags = models.ManyToManyField(  # 中介模型
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),  # 注意顺序！！！
    )

    # 下一篇
    def next_article(self):
        return Article.objects.filter(id__gt=self.id).order_by('id').first()

    # 上一篇
    def pre_article(self):
        return Article.objects.filter(id__lt=self.id).order_by('-id').first()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ["-create_time", ]


class ArticleDetail(models.Model):
    """
    文章详情表
    """
    content = models.TextField()
    article = models.OneToOneField(to="Article", to_field="id")

    def __str__(self):
        return self.article.title

    class Meta:
        verbose_name = "文章详情"
        verbose_name_plural = verbose_name


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    article = models.ForeignKey(to="Article", to_field="id")
    tag = models.ForeignKey(to="Tag", to_field="id")

    def __str__(self):
        return "{}-{}".format(self.article.title, self.tag.title)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name = "文章-标签"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """
    评论表
    """
    article = models.ForeignKey(to="Article", to_field="id")
    user = models.ForeignKey(to="UserInfo", to_field="id")
    content = models.CharField(max_length=255)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:6]

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        ordering = ["-create_time", ]


class Messages(models.Model):
    user = models.ForeignKey(to="UserInfo", to_field="id")
    content = models.CharField(max_length=255)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:6]

    class Meta:
        verbose_name = "留言"
        verbose_name_plural = verbose_name
        ordering = ["-create_time", ]