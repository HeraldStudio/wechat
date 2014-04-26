# -*- coding:utf-8 -*-
from leaf.models import Leaf


def getLost():
    lost = Leaf.objects.filter(isFind=0)
    infor = u''
    for i in lost:
        infor += i.name + u'\n地点:' + i.contact + u'\n详情:\n' + i.info

        try:
            if i is lost[5]:
                break
            else:
                infor += u'\n\n'
        except:
            infor += u'\n\n'
    if infor[-2:] == u'\n\n':
        infor = infor[:-2]
    if infor[-2:] == u'\n\n':
        infor = infor[:-2]
    if not lost:
        infor = u'暂无'
    return infor
