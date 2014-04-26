# -*- coding:utf-8 -*-

def logException(e):
    import logging
    logger = logging.getLogger("weixin.wechat")
    logger.error("%s %s"%(type(e),e.args))


def logErrorinfo(err):
    import logging
    logger = logging.getLogger("weixin.wechat")
    logger.error(err)

if __name__=="__main__":
    #logException('e.log')
    try:
        1/'a'
    except Exception,e:
        print "%s ********* %s ********%s"%(type(e),e.args)




