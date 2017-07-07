# -*- coding: utf-8 -*-
import json
import os
from functools import reduce
from config import appid, appsecret
import requests


def print_menu(menu_json):
    maxcount = reduce(lambda x, y: max(x, y), map(lambda x: len(x['sub_button']), menu_json))
    print('')
    for line in range(0, maxcount):
        linestr = ''
        for col in range(0, len(menu_json)):
            btns = menu_json[col]['sub_button']
            i = line - maxcount + len(btns)
            linestr += ' {0:12} \t'.format(btns[i]['name'].encode('utf-8') if i >= 0 else '')
        print(linestr)

    linestr = ''
    for col in range(0, len(menu_json)):
        linestr += '[{0:12}]\t'.format(menu_json[col]['name'].encode('utf-8'))
    print(linestr)
    print('')

if __name__ == '__main__':
    try:
        print('正在获取 Access Token: ')

        request = requests.get('https://api.weixin.qq.com/cgi-bin/token' +
                               '?grant_type=client_credential' +
                               '&appid=' + appid +
                               '&secret=' + appsecret)
        token = json.loads(request.content)
        if 'access_token' in token:
            token = token['access_token']
            print(token + '\n')

        else:
            print('获取 Token 失败')


#        request = requests.get('https://api.weixin.qq.com/cgi-bin/menu/get?access_token=' + token)
#        menu = json.loads(request.content)['menu']['button']
#        print(u'当前的菜单为: ')
#        print_menu(menu)
        print("ok")
        menu = json.loads(os.popen('cat menu.json').read(), encoding='utf-8')
        print(u'要改为的菜单为: ')
        print_menu(menu)

        raw_input('按回车确认上传菜单, Ctrl+C 取消:')
        request = requests.post('https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + token,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({'button': menu}, ensure_ascii=False).encode('utf-8'))

        if json.loads(request.content)['errcode'] == 0:
            print(u'菜单修改成功, 请刷新微信查看效果。')
        else:
            print(json.loads(request.content)['errmsg'])


    except Exception as e:
        print('操作失败, 请重试')
        print(e)
