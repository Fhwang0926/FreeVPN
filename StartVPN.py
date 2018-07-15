import requests, re, os, sys
from bs4 import BeautifulSoup


class OpenVPN:

    def __init__(self):
        self.accountInfo = {}
        self.data = []
        self.reg = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(Username:.+li)|(Password:.+li)')
        self.getHtml()
        pass

    def getHtml(self):
        rs = requests.get("https://freevpn.me/accounts/")
        if rs.status_code != 200: raise ValueError
        soup = BeautifulSoup(rs.text, 'html.parser')
        for x in soup.find_all('li'):
            if ":" in str(x): self.cleaner(str(x))

    def connect(self):
        try:
            if "win" in sys.platform:
                print("Disconnecting All VPN's")
                os.system("rasdial /disconnect")
                connectcmd = "rasdial "+self.accountInfo['target']+" " + self.accountInfo['id'] + " " + self.accountInfo['pw']+" /phone:"+self.accountInfo['target']
                os.system(connectcmd)
        except Exception as e:
            print(e)

    def cleaner(self,  data):
        rs = self.reg.findall(data)
        for x in rs:
            if x[0]: self.accountInfo.update({'target' : self.removeTag(x[0])})
            if x[1]: self.accountInfo.update({'id': self.removeTag(x[1]).split(':')[1].strip()})
            if x[2]: self.accountInfo.update({'pw': self.removeTag(x[2]).split(':')[1].strip()})
        print(self.accountInfo)

    def removeTag(self, x):
        return re.sub(r'<b>|</b>|</li|>|<', '', x)

proc = OpenVPN()
proc.connect()

(Password:.+li)|(Username:/w+<li)|(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)

