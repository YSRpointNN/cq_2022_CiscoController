import requests
import re
import sys
from requests.packages import urllib3
urllib3.disable_warnings()


class CiscoController:
    def __init__(self, url):
        # https://10.8.63.139/screens/spam/cell_list.html
        self.apsum = 0
        self.apinfo_table = []
        print('Waiting for '+url+'to respond...')
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52'}
        try:
            session = requests.session()
            session.get(url, headers=head, verify=False)
        except requests.exceptions.ConnectionError:
            print('------ERROR: CONNECTION TIMEOUT!')
            input('Enter any key to exit\n')
            sys.exit()
        else:
            cookie_str = str(session.cookies)
            cookie = re.findall('Cookie (.*?) for', cookie_str)
            head['Authorization'] = '******************'
            head['Cookie'] = cookie[0]
            html = session.get(url, headers=head, verify=False)
            html_str = html.text
            if len(html_str) < 1024:
                print('NOT DATA FAIL!!!')
                input('Enter any key to exit\n')
                sys.exit()
            else:
                print(url + ': SUCCESS~')
            self.apsum = re.findall(r'Number of APs.*?VALUE="(\d*)">', html_str, re.S)[0]
            regroup = re.finditer('var indexVal =.*?oper_status"', html_str, re.S)
            for ThisCtl_reline in regroup:
                tableload = ThisCtl_reline.group()
                apinfo_line = re.findall('cell_name.*VALUE="(.*?)">', tableload)
                apinfo_line.extend(re.findall('rad_ipv6.*VALUE="(.*?)">', tableload))
                apinfo_line.extend(re.findall('cell_model.*VALUE="(.*?)">', tableload))
                apinfo_line.extend(re.findall('cell_mac.*VALUE="(.*?)">', tableload))
                apinfo_line.extend(re.findall('ap_uptime.*VALUE="(.*?)">', tableload))
                self.apinfo_table.append(apinfo_line)
            if self.apsum == '75':
                html = session.get(url+'?pgInd=2', headers=head, verify=False)
                html_str = html.text
                self.apsum = str(75+int(re.findall(r'Number of APs.*?VALUE="(\d*)">', html_str, re.S)[0]))
                regroup = re.finditer('var indexVal =.*?oper_status"', html_str, re.S)
                for ThisCtl_reline in regroup:
                    tableload = ThisCtl_reline.group()
                    apinfo_line = re.findall('cell_name.*VALUE="(.*?)">', tableload)
                    apinfo_line.extend(re.findall('rad_ipv6.*VALUE="(.*?)">', tableload))
                    apinfo_line.extend(re.findall('cell_model.*VALUE="(.*?)">', tableload))
                    apinfo_line.extend(re.findall('cell_mac.*VALUE="(.*?)">', tableload))
                    apinfo_line.extend(re.findall('ap_uptime.*VALUE="(.*?)">', tableload))
                    self.apinfo_table.append(apinfo_line)
            html.close()
            session.close()
        pass


class RuckusController:
    def __init__(self):
        # https://172.30.1.245:8443/wsg/api/public/v11_0/query/ap?
        # JSESSIONID=d1XpnwE1xx9qd3QXiZJ4COv6D36fIvrD
        # X-CSRF-Token: 063D29B6F36E8D13C6794C0918451D39
        # _dc: 1668166627747
        # Content-Length: 352
        pass
