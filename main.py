#!/usr/bin/env python
# coding=utf-8


import requests
import re
import smtplib
import time
from apscheduler.scheduler import Scheduler
from collections import OrderedDict
from email.mime.text import MIMEText
from conf import *


PARAMS = OrderedDict([
        ('method', 'queryLeftTicket'),
        ('orderRequest.train_date', DATA),
        ('orderRequest.from_station_telecode', FROM),
        ('orderRequest.to_station_telecode' , TO),
        ('orderRequest.train_no', TRAIN_NO),
        ('trainPassType', 'QB'),
        ('trainClass', 'D#'),
        ('includeStudent', '00'),
        ('seatTypeAndNum', ''),
        ('orderRequest.start_time_str', '00:00--24:00'),
    ])

exit_flag = False

def send_massage(num):
    global exit_flag
    sub = u'%s到%s的%s车次剩余%s张票' % (FROM, TO, TRAIN_NO, num)
    content = u'如题'
    send_mail_address = SEND_MAIL_USER_NAME + "<" + SEND_MAIL_USER + "@" + SEND_MAIL_POSTFIX + ">"
    msg = MIMEText(content, 'html', 'utf-8')
    msg["Accept-Language"]="zh-CN"
    msg["Accept-Charset"]="ISO-8859-1, utf-8"
    msg['Subject'] = sub
    msg['From'] = send_mail_address
    msg['to'] = to_adress = "139SMSserver<" + RECEIVE_MAIL_USER + "@" + RECEIVE_MAIL_POSTFIX + ">"
    try:
        stp = smtplib.SMTP()
        stp.connect(SEND_MAIL_HOST)
        stp.login(SEND_MAIL_USER, SEND_MAIL_PASSWORD)
        stp.sendmail(send_mail_address, to_adress, msg.as_string())
        print "send message sucessfully..."
        exit_flag = True
    except Exception, e:
        print "fail to send message: "+ str(e)
    finally:
        stp.close()

def run_once():
    URL = 'http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do'
    source = requests.get(URL, params=PARAMS)
    res = re.findall(r"(\d+)(,--){7}", source.text)
    if res:
        send_massage(res[0][0])

def main():
    global exit_flag
    
    run_once()

    sched = Scheduler()
    sched.start()
    sched.add_interval_job(run_once, minutes=FREQUENCE_MINUTES)
    while True:
        if exit_flag:
            exit()
        time.sleep(10)

if __name__ == '__main__':
    main()
