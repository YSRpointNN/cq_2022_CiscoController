from PEGATRON_Controller import *
import time
from pathlib import Path


def online_find():
    with open('APBS.txt', 'r') as APBSfile:
        apbstxt = APBSfile.read()
    thisip = []
    for singlectl in bigload:
        thisip.extend([get[1] for get in singlectl.apinfo_table])
    fileline = re.findall('&.*?\n', apbstxt)
    for find in fileline:
        findbuff = re.findall(r'&(.*?)&(\d+.\d+.\d+.\d+)&(.*?)&(.*?)&.*?\n', find)[0]
        if findbuff[1] in thisip:
            pass
        else:
            buffer = list(findbuff)
            buffer.append(nowtime)
            WARNING_LOST.append(buffer)
    if len(thisip) > len(fileline) - len(WARNING_LOST):
        bsip = re.findall(r'.*&(\d+.\d+.\d+.\d+)&.*?\n', apbstxt)
        for singlectl in bigload:
            for ctlline in singlectl.apinfo_table:
                if ctlline[1] not in bsip:
                    ctlindex = bigload.index(singlectl)
                    ctlline.append(CONTROLLER_NAME[ctlindex])
                    new_onlineap.append(ctlline)
                    with open('APBS.txt', 'a') as APBSfile:
                        APBSfile.write('&' + '&'.join(ctlline) + '\n')
    else:
        pass
    return thisip


def log_control():
    logpath = Path.cwd() / 'logs'
    logname = [logi.name for logi in logpath.iterdir()]
    while len(logname) > 240:
        todel = logpath / (logname[0])
        logname.remove(logname[0])
        todel.unlink()
        print('Delete', todel)
    with open('logs/' + logname[-1], 'r') as lost_log:
        lost_log_txt = (re.findall('LOST:\n(.*)LOSTEND', lost_log.read(), re.S))[0]
        if len(lost_log_txt) > 15:
            lost_log_aps = re.findall(r'(.*?)\t(\d+.*?)\t(.*?)\t(.*?)\t(\d+-\d+-\d+ \d+:\d+:\d+)\n', lost_log_txt)
        else:
            lost_log_aps = []
        return lost_log_aps


def log_find(lastlost_ap):
    lastlost_ip = [ip[1] for ip in lastlost_ap]
    filename = time.strftime('logs/%Y%m%d-%H%M%S.txt', time.localtime())
    with open(filename, 'w') as logfile:
        logfile.write('LOST:\n')
        for buffer in WARNING_LOST:
            if buffer[1] in lastlost_ip:
                theindex = lastlost_ip.index(buffer[1])
                old_log_buffer = list(lastlost_ap[theindex])
                history_lostap.append(old_log_buffer)
                logfile.write('\t'.join(old_log_buffer) + '\n')
            else:
                new_lostap.append(buffer)
                logfile.write('\t'.join(buffer) + '\n')
        logfile.write('LOSTEND\n#\n')
        for lvlctl in bigload:
            logfile.write('Numb of AP: '+lvlctl.apsum+'\n')
            for lvlline in lvlctl.apinfo_table:
                for lvlone in lvlline:
                    logfile.write('\t'+lvlone)
                logfile.write('\n')


def find_goback():
    for backline in last_lostap:
        if backline[1] in this_onlin_ip:
            history_gobackap.append(list(backline))


def time_judg():
    hour = re.findall(r' (\d+):\d+:\d+', nowtime)[0]
    minutes = re.findall(r' \d+:(\d+):\d+', nowtime)[0]
    if hour == '08' and int(minutes) < 30:
        return True
    else:
        return False


def email_send(swout):
    if swout:
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header

        sender = 'email'
        to = ['email']
        cc = ['email']
        receivers = to + cc
        html_egg = html

        message = MIMEText(html_egg, 'html', 'utf-8')
        subject = 'test'
        message['Subject'] = Header(subject, 'utf-8')
        message['To'] = Header("email")
        message['Cc'] = Header("email")

        try:
            smtpobj = smtplib.SMTP('email.server')
            smtpobj.sendmail(sender, receivers, message.as_string())
            print("sucess")
        except smtplib.SMTPException:
            print("Error")
    else:
        pass


# -----------------------------------start------------------------------------ #
CONTROLLER_NAME = ('SFIS.139', 'SFIS.138', 'SFIS.3', 'OA.21', 'OA.24', 'OA.26', 'OA.27', 'OA.30')
WARNING_LOST = []

Ctl139 = CiscoController('https://10.8.63.139/screens/spam/cell_list.html')
Ctl138 = CiscoController('https://10.8.63.138/screens/spam/cell_list.html')
Ctl3 = CiscoController('https://10.8.63.3/screens/spam/cell_list.html')
Ctl21 = CiscoController('https://172.30.36.21/screens/spam/cell_list.html')
Ctl24 = CiscoController('https://172.30.36.24/screens/spam/cell_list.html')
Ctl26 = CiscoController('https://172.30.36.26/screens/spam/cell_list.html')
Ctl27 = CiscoController('https://172.30.36.27/screens/spam/cell_list.html')
Ctl30 = CiscoController('https://172.30.36.30/screens/spam/cell_list.html')

# bigload = (Ctl139, Ctl138, Ctl3)
bigload = (Ctl139, Ctl138, Ctl3, Ctl21, Ctl24, Ctl26, Ctl27, Ctl30)
nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
new_onlineap = []
history_lostap = []         # 輸出歷史
history_gobackap = []
new_lostap = []

this_onlin_ip = online_find()
last_lostap = log_control()     # 真歷史
log_find(last_lostap)
find_goback()
Emailout = time_judg()

html_news = '''<font color="407a9f" size ="3" face="微軟正黑體">每日巡檢<br/></font>'''

history_table = '''<font color="407a9f" size ="3" face="微軟正黑體"><br/>無歷史掉綫</font>'''

if new_onlineap or new_lostap or history_gobackap:
    html_news = ''
    if new_lostap:
        html_news += '''<center><b><font size ="4" face="微軟正黑體"  color="red">---新消息:發現新掉綫---</font></b></center>
    <hr size="2px" color ="b03030">
    <table border="1" cellpadding="0" cellspacing="0" width="900">
        <tr>
            <th bgcolor="b03030" ><font color="white" size ="2" face="微軟正黑體">AP</font></th>
            <th bgcolor="b03030"><font color="white" size ="2" face="微軟正黑體">IP</font></th>
            <th bgcolor="b03030"><font color="white" size ="2" face="微軟正黑體">MAC</font></th>
            <th bgcolor="b03030"><font color="white" size ="2" face="微軟正黑體">型號</font></th>
            <th bgcolor="b03030"><font color="white" size ="2" face="微軟正黑體">掉綫時間</font></th>
        </tr>'''
        for var_to_html in new_lostap:
            htmltxt = '''<tr>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{name}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{ip}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{mac}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{model}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{time}</font></td>
        </tr>'''.format(name=var_to_html[0], ip=var_to_html[1], mac=var_to_html[3], model=[2], time={var_to_html[4]})
            html_news += htmltxt
        html_news += '''</table>
    <hr size="2px" color ="b03030">'''

    if new_onlineap:
        html_news += '''<center><b><font size ="4" face="微軟正黑體"  color="blue">---新消息:發現新上綫---</font></b></center>
    <hr size="2px" color ="3030b0">
    <table border="1" cellpadding="0" cellspacing="0" width="900">
        <tr>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">AP</font></th>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">IP</font></th>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">MAC</font></th>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">型號</font></th>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">上綫時間</font></th>
            <th bgcolor="3030b0"><font color="white" size ="2" face="微軟正黑體">當前所在控制器</font></th>
        </tr>'''
        for var_to_html in new_onlineap:
            htmltxt = '''<tr>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{name}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{ip}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{mac}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{model}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{onlinetime}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{ctl}</font></td>
        </tr>'''.format(name=var_to_html[0], ip=var_to_html[1], mac=var_to_html[3], model=var_to_html[2], onlinetime=nowtime, ctl='test')
            html_news += htmltxt
        html_news += '''</table>
    <hr size="2px" color ="3030b0">'''

    if history_gobackap:
        html_news += '''<center><b><font size ="4" face="微軟正黑體"  color="green">---新消息:原丟失AP已重新上綫---</font></b></center>
    <hr size="2px" color ="green">
    <table border="1" cellpadding="0" cellspacing="0" width="1200">
        <tr>
            <th bgcolor="green"><font color="white" size ="2" face="微軟正黑體">AP</font></th>
            <th bgcolor="green"><font color="white" size ="2" face="微軟正黑體">IP</font></th>
            <th bgcolor="green"><font color="white" size ="2" face="微軟正黑體">掉綫時間</font></th>
            <th bgcolor="green"><font color="white" size ="2" face="微軟正黑體">回歸時間</font></th>
        </tr>'''
        for var_to_html in history_gobackap:
            htmltxt = '''<tr>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{name}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{ip}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{losttime}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{onlinetime}</font></td>
        </tr>'''.format(name=var_to_html[0], ip=var_to_html[1], losttime=var_to_html[4], onlinetime=nowtime)
            html_news += htmltxt
        html_news += '''</table>
    <hr size="2px" color ="green">'''
    Emailout = True

if history_lostap:
    history_table = '''<hr size="2px" color ="919100">
    <center><font color="919100" size ="4" face="微軟正黑體"><b>以下為歷史掉綫記錄</b></font></center>
    <table border="1" cellpadding="0" cellspacing="0" width="1200">
        <tr>
            <th bgcolor="919100"><font color="white" size ="2" face="微軟正黑體">AP</font></th>
            <th bgcolor="919100"><font color="white" size ="2" face="微軟正黑體">IP</font></th>
            <th bgcolor="919100"><font color="white" size ="2" face="微軟正黑體">MAC</font></th>
            <th bgcolor="919100"><font color="white" size ="2" face="微軟正黑體">型號</font></th>
            <th bgcolor="919100"><font color="white" size ="2" face="微軟正黑體">掉綫時間</font></th>
        </tr>'''
    for var_to_html in history_lostap:
        htmltxt = '''<tr>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{name}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{ip}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{mac}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{model}</font></td>
            <td align="center"><font size ="2" face="Bahnschrift Condensed">{losttime}</font></td>
        </tr>'''.format(name=var_to_html[0], ip=var_to_html[1], mac=var_to_html[3], model=var_to_html[2], losttime=var_to_html[4])
        history_table += htmltxt
    history_table += '''</table>'''

html_table = '''<table border="1" cellpadding="0" cellspacing="0" width="340">
        <tr>
            <th  bgcolor="407a9f"><font color="ffffff" size ="2" face="微軟正黑體">控制器IP</font></th>
            <th  bgcolor="407a9f"><font color="ffffff" size ="2" face="微軟正黑體">在綫數量</font></th>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">10.8.63.139</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c139}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">10.8.63.138</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c138}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">10.8.63.3</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c3}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">172.30.36.21</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c21}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">172.30.36.24</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c24}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">172.30.36.26</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c26}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">172.30.36.27</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c27}</font></td>
        </tr>
        <tr>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">172.30.36.30</font></td>
            <td align="center"><font color="407a9f" size ="2" face="Bahnschrift Condensed">{c30}</font></td>
        </tr>
    </table>
    <font color="407a9f" size ="3" face="微軟正黑體">總共:{sum}個</font>
'''.format(c139=Ctl139.apsum, c138=Ctl138.apsum, c3=Ctl3.apsum, c21=Ctl21.apsum, c24=Ctl24.apsum, c26=Ctl26.apsum,
           c27=Ctl27.apsum, c30=Ctl30.apsum, sum=len(this_onlin_ip))

html_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>test</title>
    <style type="text/css">
    h3.title {font-family: Microsoft YaHei; font-size:20px; color:#FFFFFF; background:#407a9f;padding:1cm 0cm 0cm 0cm;height:37pt}
    </style>
</head>
'''

html = '''{head}
<body background="">
    <h3 align="center" class="title">AP自動巡檢記錄</h3>
    {news}
    <font color="407a9f" size ="3" face="微軟正黑體">--更新時間:{time}<br/>以下為各控制器在綫數量</font>
    {table}
    {history}
    </body>
</html>
'''.format(head=html_head, news=html_news, table=html_table, history=history_table, time=nowtime)
email_send(Emailout)
