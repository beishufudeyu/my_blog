from django.core.paginator import Paginator

from django.conf import settings


def page_paginator(articles, page_num):
    # 分页
    paginator_list = []
    pages_inavtor = Paginator(articles, settings.EACH_PAGE_PAGINATOR_NUM)
    page_of_blogs = pages_inavtor.page(page_num)

    paginator_list.append(page_of_blogs)


    # 分页显示,加入当前页
    current_page_num = page_of_blogs.number
    paginator_list.append(current_page_num)

    # 页码
    page_range = list(range(max(current_page_num - 3, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 3, pages_inavtor.num_pages) + 1))
    # 加上省略页码
    if page_range[0] - 1 >= 2:
        page_range.insert(0, "...")
    if pages_inavtor.num_pages - page_range[-1] >= 2:
        page_range.append("...")
    # 加上首页尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != pages_inavtor.num_pages:
        page_range.append(pages_inavtor.num_pages)
    # 添加到列表
    paginator_list.append(page_range)
    return paginator_list