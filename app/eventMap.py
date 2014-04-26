# -*- coding:utf-8 -*-
from app.models import UserInfo, Curriculum
from app.tools.getCurriculum import getDayCourse, getNextCourse
from app.tools.getJwcInfor import getJwcInfor
from app.tools.getLibrary import getLibrary
from app.tools.getLost import getLost
from app.tools.getTime import getWeekDay
from app.tools.getTyxPc import getTyxPc
from app.tools.setCurriculum import setCurriculum
from app.tools.simisimi_api import simsimi, simsimi_back
from app.tools.post_msg import postMsg

_eventClickMap={	\
	'CurriculumToday':curriculumToday,\
	'CurriculumTomorrow':curriculumTomorrow,\
	'CurriculumNext':curriculumNext,\
	'Update':update,\
	'Library':library,\
	'TyxPc':tyxPc,\
	'Instruction':instruction,\
	'UpdateCurriculum':updateCurriculum,\
	'JwcInfo':jwcInfo,\
	'lost':lost,\
	'OpenChatWithUser':openChatWithUser,\
	'ExitChatWithUser':exitChatWithUser}

_eventTextMap={	\
	'今天课表':curriculumToday,\
	'教务信息':jwcInfo,\
	'下节课':curriculumNext,\
	'跑操':tyxPc,\
	'明天课表':curriculumTomorrow,\
	'借书信息':library,\
	'周一课表':dayCrouseMon,\
	'周二课表':dayCrouseThues,\
	'周三课表':dayCrouseWed,\
	'周四课表':dayCrouseThur,\
	'周五课表':dayCrouseFri,\
	'周六课表':dayCrouseSat,\
	'周日课表':dayCrouseSun,\
	'查看绑定信息':viewBindInfo,\
	'更新课表':updateCurriculum}

def eventClickMap(msg,user,fromUser,toUser):
	try:
		return _eventClickMap.get(msg)(user,fromUser,toUser)
	except KeyError:
		return ''

def eventTextMap(msg,user,fromUser,toUser):
	try:
		return _eventClickMap.get(msg)(user,fromUser,toUser)
	except KeyError:
		return "猴子请来的逗比出了点状况需要下线维护（好吧囧其实是我们的服务器出了点状况需要维护）"

def unbindedReturn(toUser):
	return '你还没有绑定一卡通哦，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUser

def curriculumToday(user,fromUser,toUser):
	if user:
		getDayCourse(user[0].openId, getWeekDay())
	else:
		return unbindedReturn(toUser)

def curriculumTomorrow(user,fromUser,toUser):
	if user:
		if getWeekDay() == 7:
			return getDayCourse(user[0].openId, 1)
		else:
			return getDayCourse(user[0].openId, getWeekDay() + 1)
	else:
		return unbindedReturn(toUser)

def curriculumNext(user,fromUser,toUser):
	if user:
		return getNextCourse(user[0].openId)
	else:
		return unbindedReturn(toUser)

def update(user,fromUser,toUser):
	if user:
		return u'当前绑定一卡通为：' + user[0].cardNumber + u'\n\n<a href="http://herald.seu.edu.cn/xchat/auth/'+ toUser + u'">点这里更新绑定信息</a>\n'
	else:
		return unbindedReturn(toUser)

def curriculumNext(user,fromUser,toUser):
	if user:
		return getNextCourse(user[0].openId)
	else:
		return unbindedReturn(toUser)
	
def library(user,fromUser,toUser):
	if user:
		if not (user[0].libUsername or user[0].libPwd):
			return '尚未绑定图书馆登陆信息，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUser
		else:
			infor = getLibrary(user[0].openId)
		if infor == 'error':
			return '绑定图书馆登陆信息有误，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里更新</a>' % toUser
		else:
			return infor
	else:
		return unbindedReturn(toUser)

def tyxPc(user,fromUser,toUser):
	if user:
		if not user[0].pcPwd:
			return '尚未绑定跑操查询密码，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里绑定账号</a>' % toUser
		else:
			infor = getTyxPc(user[0].openId)
			if infor == 'error':
				infor = '绑定跑操查询密码有误，<a href="http://herald.seu.edu.cn/xchat/auth/%s">点这里更新</a>' % toUser
			return infor
	else:
		return unbindedReturn(toUser)
	
def instruction(user,fromUser,toUser):
	return '提供日常校园信息查询服务，点击相应标签或回复以下关键字会得到想要的结果:' \
			'\n跑操  今天课表  明天课表  下节课 周X课表 借书信息  更新课表' \
			'\n\n网络环境影响可能会导致信息延迟或丢失，如果接收不到信息请重试一下。' \
			'\n\n更多功能正在玩命开发中... \n注：目前扩展的调戏功能是猴子请来的逗比并非小猴真身。' \
			'\n\n此账号由东南大学先声网 (SEU Herald) 维护\n\n如果你有好的建议或者意见请发邮件或者短信给我，\n目前不接受任何形式的广告合作还请理解。' \
			'\nEmail: \nxindervella@gmail.com\nTel: \n132 2208 6228 熊海潇\n\n五一期间小猴将下线升级，带来的不便还请理解么么哒！'

def updateCurriculum(user,fromUser,toUser):
	if user:
		try:
			curriculum = Curriculum.objects.filter(openId=user[0].openId)
			curriculum.delete()
			setCurriculum(user[0].openId)
			return '更新成功'
		except:
			return '更新失败，请重试，如果仍然失败请发邮件给我，我会及时修改相关bug。'
	else:
		return unbindedReturn(toUser)
	
def jwcInfo(user,fromUser,toUser):
	return getJwcInfor()

def lost(user,fromUser,toUser):
	return getLost()

def openChatWithUser(user,fromUser,toUser):
	chatStatus = charwithuser.GetStatus(toUserName)
	if chatStatus ==0 :
		postMsg(toUserName,'正在为你寻找小伙伴哦~')
		charwithuser.OpenChat(toUserName)
		postMsg(toUserName,'已经为你找到了一位神秘的小伙伴,快和TA打个招呼吧!')
		return '^_^'
	elif chatStatus == 1:
		return '我们还在为你努力寻找中,不如先喝杯茶吧,不过你也可以点击退出取消配对哦.'
	elif chatStatus == 11:
		charwithuser.ChangeStatus(toUserName,12)
		return '我们已经为你找到小伙伴啦!什么?不能让你满意?30秒内再次点击配对我们会为你重新寻找小伙伴呢.'
	elif chatStatus == 12:
		charwithuser.DelChat(toUserName)
		charwithuser.OpenChat(toUserName)
		return '正在玩命为你重新寻找小伙伴哦~'
	else:
		return "好像,似乎出了一点点小错误,点击退出然后重新寻找小伙伴吧."

def ExitChatWithUser(user,fromUser,toUser):
	charwithuser.DelChat(toUserName)
	infor = '已经为你清除配对状态了哦~'


def dayCrouseMon(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 1)
	else:
		return unbindedReturn(toUser)

def dayCrouseThues(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 2)
	else:
		return unbindedReturn(toUser)

def dayCrouseWed(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 3)
	else:
		return unbindedReturn(toUser)

def dayCrouseThur(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 4)
	else:
		return unbindedReturn(toUser)

def dayCrouseFri(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 5)
	else:
		return unbindedReturn(toUser)

def dayCrouseSat(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 6)
	else:
		return unbindedReturn(toUser)

def dayCrouseSun(user,fromUser,toUser):
	if user:
		return getDayCourse(user[0].openId, 7)
	else:
		return unbindedReturn(toUser)

def viewBindInfo(user,fromUser,toUser):
	if user:
		return u'少年，你的绑定的一卡通是：' + user[0].cardNumber
	else:
		return unbindedReturn(toUser)
