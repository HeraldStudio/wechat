# -*- coding:utf-8 -*-
import redis
import calendar
from datetime import datetime
import simplejson as json
from ast import literal_eval


# Redis里的内容
# key           | description
# pairing_queue  | 所有的申请配对的用户，配对成功的要剔除出去
# user_id       | 已配对或在申请配对的用户的信息

# 默认存在数据库 0 以及 pairing_queue 这个key

Config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

# 转化从数据库获取到的空数据
def convertEmptyResult(result):
    if not result:
        return []
    else:
        return result

# 将用户剔除出申请配对队列
# 无返回，一般来说不会出现同步异常
def removeFrompairingQueue(user_id):
    db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
    pairing_user_list = literal_eval(convertEmptyResult(db.get('pairing_queue')))
    try:
        pairing_user_list.remove(user_id)
    except:
        pass
    db.set('pairing_queue', pairing_user_list)

# 用户申请进入聊天
# 线程会一直执行循环查询数据库以寻找配对的用户
# 配对成功后返回1（值得商榷）
# 出现同步的异常时删除用户的配对信息，并返回0（这里值得商榷）
def openChat(user_id):
    try:
        db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
        # 添加Key/Value，并加入配对队列
        value = {
            'status': 1,
            'target': ''
        }
        db.set(user_id, value)
        old_list = literal_eval(convertEmptyResult(db.get('pairing_queue')))
        old_list.append(user_id)
        db.set('pairing_queue', old_list)

        # 为该用户配对
        # 有一个潜在地同步问题。。
        while True:
            pairing_user_list = literal_eval(convertEmptyResult(db.get('pairing_queue')))
            for target in pairing_user_list:
                # 检查自己的状态
                self_value = literal_eval(convertEmptyResult(db.get(user_id)))
                if self_value and self_value['status'] == 1:  # 确实在申请配对
                    target_value = literal_eval(convertEmptyResult(db.get(target)))
                    if not target_value:  # 已经不存在了。。
                        removeFrompairingQueue(target)
                    elif target_value['status'] == 1:  # 对方也同样处于配对状态
                        # TODO：同步问题。假设两个用户会互相选择对方
                        # 此处暂时定为用户设置自己的target
                        self_value['status'] = 11
                        self_value['target'] = target
                        db.set(user_id, self_value) # 更新
                        removeFrompairingQueue(user_id) # 将自己移出申请配对队列
                        return 1
                else:
                    removeFrompairingQueue(user_id) # 有可能已配对成功或不继续配对了
    except:
        delChat(user_id)
        return 0

# 获取用户当前状态
# 数据库中有用户的记录则返回其状态，否则返回0
# 出现同步的异常时删除用户的配对信息，并返回0（这里值得商榷）
def getStatus(user_id):
    try:
        db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
        user_value = literal_eval(convertEmptyResult(db.get(user_id)))
        if not user_value:
            return 0
        else:
            return user_value.get('status', 0)
    except:
        delChat(user_id)
        return 0

# 获取用户的目标
# 如果目标存在（用户处于已配对状态）则返回目标的id，否则返回0
# 出现同步的异常时返回0
def getTarget(user_id):
    try:
        db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
        user_value = literal_eval(convertEmptyResult(db.get(user_id)))
        if not user_value or \
            (user_value['status'] != 11 and user_value['status'] != 12):
            return 0
        else:
            return user_value['target']     
    except:
        return 0

# 改变用户的状态
# 出现同步异常（无此用户记录），直接返回0
def changeStatus(user_id, new_status):
    try:
        db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
        user_value = literal_eval(convertEmptyResult(db.get(user_id)))
        if not user_value:
            return 0
        else:
            user_value['status'] = new_status
    except:
        return 0

# 删除用户的配对状态
# 删除会顺带删除与其配对的用户的状态
# 删除成功后会返回其原先的配对对象的id（用于提示，不确定可否实现）
# 出现同步异常时返回0
def delChat(user_id):
    try:
        db = redis.Redis(host = Config['host'], port = Config['port'], db = Config['db'])
        user_value = literal_eval(convertEmptyResult(db.get(user_id)))
        if not user_value:
            return 0
        else:
            target = user_value['target']
            db.delete(user_id)
            db.delete(target)
    except:
        return 0        
