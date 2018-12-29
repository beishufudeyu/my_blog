from django import forms
from django.core.exceptions import ValidationError
from . import models
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

# 定义一个注册的form类
class RegForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=4,
        label="用户名",
        error_messages={
            "max_length": "用户名最长16位",
            "min_length": "用户名最短4位",
            "required": "用户名不能为空",
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control input-sm", "placeholder": "用户名"},
        )
    )

    password = forms.CharField(
        min_length=6,
        max_length=16,
        label="密码",
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control input-sm", "placeholder": "密码"},
            render_value=True,
        ),
        error_messages={
            "min_length": "密码至少要6位！",
            "max_length": "密码最长16位",
            "required": "密码不能为空",
        }
    )

    re_password = forms.CharField(
        min_length=6,
        max_length=16,
        label="确认密码",
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control input-sm", "placeholder": "确认密码"},
            render_value=True,
        ),
        error_messages={
            "min_length": "确认密码至少要6位！",
            "max_length": "确认密码最长16位",
            "required": "确认密码不能为空",
        }
    )

    email = forms.EmailField(
        label="邮箱",
        widget=forms.widgets.EmailInput(
            attrs={"class": "form-control input-sm", "placeholder": "邮箱"},

        ),
        error_messages={
            "invalid": "邮箱格式不正确！",
            "required": "邮箱不能为空",
        }
    )

    # 重写username字段的局部钩子
    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_exist = models.UserInfo.objects.filter(username=username).first()
        if is_exist:
            # 表示用户名已注册
            self.add_error("username", ValidationError("用户名已存在"))
        else:
            return username

    # 重写email字段的局部钩子
    def clean_email(self):
        email = self.cleaned_data.get("email")
        is_exist = models.UserInfo.objects.filter(email=email).first()
        if is_exist:
            # 表示邮箱已注册
            self.add_error("email", ValidationError("邮箱已被注册"))
        else:
            return email

    # 重写全局的钩子函数，对确认密码做校验
    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))

        else:
            return self.cleaned_data


# 定义一个新建文章的form类
class ArticleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = models.Category.objects.all().values_list("id", "title")
        self.fields['tags'].choices = models.Tag.objects.all().values_list("id", "title")

    title = forms.CharField(
        max_length=32,
        min_length=4,
        label="标题",
        error_messages={
            "max_length": "标题最长32位",
            "min_length": "标题不能短于4位",
            "required": "标题不能为空",
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control", "placeholder": "文章标题"},
        )
    )

    published = forms.BooleanField(required=False, label='是否发布')
    category = forms.fields.ChoiceField(
        label="分类",
        initial=1,
        widget=forms.widgets.Select(attrs={})
    )

    tags = forms.fields.MultipleChoiceField(
        required=False,
        label="标签",
        initial=[2, ],
        widget=forms.widgets.CheckboxSelectMultiple()
    )

    content = forms.CharField(widget=SummernoteWidget())

#
class ArticleDetailForm(forms.Form):
    content = forms.CharField(widget=SummernoteWidget())
