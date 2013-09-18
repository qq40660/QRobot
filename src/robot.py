# -*- coding: utf-8 -*-
import time
import random
from tools import login
from tools import greet
from tools import monitor
from tools import loadpic

def storeLog(log):
    f = open('log.txt', 'a')
    f.write(log)
    f.close()

#防止重复评论
def loadLastId(isPost = True):    
    f = open('lastid.txt', 'r')
    lastids = f.read().split()
    lastid = lastids[0]
    #如果是评论某条微博时艾特我的
    if not isPost:
        lastid = lastids[1] #那么就读取第二个数，即上次评论的id
    f.close()
    return int(lastid)

def storeLastId(lastid, isPost = True):
    f = open('lastid.txt', 'r')
    lastids = f.read().split()
    f.close()

    f = open('lastid.txt', 'w')
    if isPost:
        f.write(str(lastid) + " ")
        f.write(lastids[1])
    else:
        #如果是评论某条微博时艾特我的
        f.write(lastids[0] + " ")
        f.write(str(lastid))
    f.close()


def run():
    client = login.login()
    lastid = loadLastId()
    inter = 50 #检查间隔

   
    while True:
        try:
            inter += 1 #加1秒
            now = time.strftime('%M%S',time.localtime(time.time()))
            hour = time.strftime('%H',time.localtime(time.time()))

            #由于weibo API限制，不能发布自己可见微博，所以我设置了一个密友可见，密友就是我自己的另外一个账号，用来监控cpu温度和运行时间
            if now == '0430':
                print "sending a monitor weibo"
                monitor_info = monitor.monitor_cpu_temp()
                monitor_info += monitor.monitor_runtime()
                monitor_info += monitor.monitor_http()
                try:
                    client.statuses.update.post(status=monitor_info, visible = 2)
                except:
                    pass

                log = "Send a monitor weibo succesfully! 时分秒：%s%s \n" %(hour,now)
                print log
                storeLog(log)

            #发微
            if now == '4600' and hour in ['07', '12', '11', '17','18', '19','22','23']:
                print 'sending a normal weibo'
                monitor_info = ""
                if random.choice(range(2)):
                    monitor_info += monitor.monitor_cpu_temp()
                elif random.choice(range(2)):
                    monitor_info += monitor.monitor_http()
                else:
                    monitor_info += monitor.monitor_runtime()

                greeting = ""
                greeting += greet.hello(hour)
                myPic = loadpic.pic()
                
                if random.choice(range(2)):
                    content = '%s' %(greeting)
                else:
                    content = '%s%s' %(greeting, monitor_info)
                try:
                    #随机选择发图或者不发图,1/2可能性发图
                    if random.choice(range(2)):
                        client.statuses.update.post(status=content)
                    else:
                        client.statuses.upload.post(status=content, pic = myPic)                
                except Exception, e:
                    print e 

                myPic.close()
                
                log = "Send a normal weibo succesfully! 时分秒：%s%s \n" %(hour,now)
                print log
                storeLog(log)

                time.sleep(1)

            #对最新 @我 的进行回复,50s一次，包括评论原创微博，回复评论
            if inter > 50:
                try:                    
                    #对最新 @我 的原创微博进行评论#

                    #获取原创的最新微博的id
                    lastid = loadLastId()
                    mentions = client.statuses.mentions.get(since_id = lastid, filter_by_type = 1)
                    for weiboInfo in mentions['statuses']:
                        lastid = weiboInfo['id']
                        print lastid
                        storeLastId(lastid)

                        myComment = ""
                        if random.choice(range(2)):
                            myComment = greet.comment()
                        else:
                            location = weiboInfo['user']['location']
                            myComment = '~~' + greet.getLocationWeather(location.encode('utf-8')) #取得天气
                            

                        client.comments.create.post(id = lastid, comment = myComment)
                        log = 'send a comment successfully! 时分秒：%s%sid:%d comment:%s \n' %(hour, now, lastid, myComment)
                        print log
                        storeLog(log)

                    #对最新 @我 的评论进行回复#
                    lastCommentid = loadLastId(False)
                    mentions = client.comments.mentions.get(since_id = lastCommentid)
                    for weiboInfo in mentions['comments']:
                        lastCommentid = weiboInfo['id'] #评论的id
                        lastPostId = weiboInfo['status']['id'] #微博的id
                        print "评论的id：%d 微博的id：%d" % (lastCommentid,lastPostId)
                        storeLastId(lastCommentid, False)

                        myComment = greet.comment()                       

                        client.comments.reply.post(id = lastPostId, cid = lastCommentid, comment = myComment)
                        log = 'replay a comment successfully! 时分秒：%s%s id:%d comment:%s \n' %(hour, now, lastid, myComment)
                        print log
                        storeLog(log)

                except Exception, e:
                    print e

                inter = 0




            time.sleep(1)#while循环每次间隔一秒



        except Exception, e:
            print e
            



if __name__=="__main__":
    run()
