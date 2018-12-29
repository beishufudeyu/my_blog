from bs4 import BeautifulSoup


class XSSFilter(object):
    __instance = None

    def __init__(self):
        # XSS白名单
        self.valid_tags = {
            "font": ['color', 'size', 'face', 'style'],
            'b': ['style'],
            'i':['style'],
            'u':['style'],
            'sup':['style'],
            'sub':['style'],

            'div': ['style'],
            "span": ['class','style'],
            "table": [
                'border', 'cellspacing', 'cellpadding','style'
            ],
            'tbody':['style'],
            'th': [
                'colspan', 'rowspan','style'
            ],
            'td': [
                'colspan', 'rowspan','style'
            ],
            "a": ['href', 'target', 'name','style'],
            "img": ['src', 'alt', 'title','style'],
            'p': [
                'align','style'
            ],
            "pre": ['class','style'],
            "hr": ['class','style'],
            'strong': ['style'],
            'blockquote': ['style'],
            'ol':['style'],
            'li':['style'],
            'ul':['style'],
            'strike':['style'],
            'h1':['style'],
            'h2': ['style'],
            'h3': ['style'],
            'h4': ['style'],
            'h5': ['style'],
            'h6': ['style'],
            'br':['style'],


        }

    def __new__(cls, *args, **kwargs):
        """
        单例模式
        :param cls:
        :param args:
        :param kwargs:
        :return:
        """
        if not cls.__instance:
            obj = object.__new__(cls, *args, **kwargs)
            cls.__instance = obj
        return cls.__instance

    def process(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        # 遍历所有HTML标签
        for tag in soup.find_all(recursive=True):
            # 判断标签名是否在白名单中
            if tag.name not in self.valid_tags:
                tag.hidden = True
                if tag.name not in ['html', 'body']:
                    tag.hidden = True
                    tag.clear()
                continue
            # 当前标签的所有属性白名单
            attr_rules = self.valid_tags[tag.name]
            keys = list(tag.attrs.keys())
            for key in keys:
                if key not in attr_rules:
                    del tag[key]

        return soup.decode()


xss_filter = XSSFilter()
