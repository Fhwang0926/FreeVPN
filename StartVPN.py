import requests, re, os, sys, time
from bs4 import BeautifulSoup
# freevpn

class OpenVPN:

    def __init__(self):
        self.accountInfo = {}
        self.data = []
        self.reg = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(Username:.+li)|(Password:.+li)')
        self.regUrl = re.compile(r'https?://(www.)?freevpn\..*\.?[a-zA-Z]$')
        self.homepages = []
        self.getHtml()
        pass

    def getHtml(self):    
        rs = requests.get("https://freevpn.me/accounts/", verify=False)
        if rs.status_code != 200: raise ValueError

        soup = BeautifulSoup(rs.text, 'html.parser')
        for x in soup.find_all('a'):
            try:
                rs = self.regUrl.search(x["href"]).group()
                if not "zip" in rs:
                    self.homepages.append(rs)
            except:
                pass
        for url in self.homepages:
            print("[+] checkVPN : ", url)
            rs = requests.get(url)
            if rs.status_code != 200: raise ValueError
            soup = BeautifulSoup(rs.text, 'html.parser')
            for x in soup.find_all('li'):
                if ":" in x: self.getAccountInfo(x)
            pass

    def connect(self, vpnName=''):
        try:
            self.vpnName = vpnName if vpnName else "JustFreeVPN"
            if "win" in sys.platform:
                print("Disconnecting All VPN's")
                os.system("rasdial /disconnect")

                cmd = 'Add-VpnConnection '
                cmd += '-Name "'+self.vpnName+'" '
                cmd += '-ServerAddress "'+self.accountInfo['host']+'" '
                cmd += '-TunnelType "PPTP" '
                cmd += '-EncryptionLevel "Required" '
                cmd += '-SplitTunneling '
                cmd += '-Force '
                # cmd += '-RememberCredential' # this option no get gateway from vpn server
                cmd += '-AuthenticationMethod MsChapv2 '
                cmd += '-PassThru'

                checkVPN = os.system("rasdial " + vpnName)
                if checkVPN == 623 or checkVPN ==0: os.system("powershell " + cmd)
                connectcmd = "rasdial "+ self.vpnName + ' "' + self.accountInfo['host'] + '" "' + self.accountInfo['pw']+'"'
                print(connectcmd)
                os.system(connectcmd)
                print("[+] JustFreeVPN connected!")
            if not "win" in sys.platform:
                print("This OS is Linux, not support")
            # try:
            #     while 1:    
            #         os.system("ping 8.8.8.8 -n 1")
            #         time.sleep(3)
            # except KeyboardInterrupt:
            #     self.disconnect()
            #     self.removeVPN()
        except Exception as e:
            print("connect error : ", e)

    def getAccountInfo(self,  data):
        rs = self.reg.findall(data)
        print(rs)
        self.accountInfo['id'] = "pptp"
        for x in rs:
            print(rs)
            if x[0]: self.accountInfo.update({'host' : self.removeTag(x[0])})
            # if x[1]: self.accountInfo.update({'id': self.removeTag(x[1]).split(':')[1].strip()})
            if x[2]: self.accountInfo.update({'pw': self.removeTag(x[2]).split(':')[1].strip()})
        print(self.accountInfo)

    def removeTag(self, x=''):
        return re.sub(r'<b>|</b>|</li|>|<', '', x)

    def disconnect(self, x=''):
        print("rasdial "+( x if x else self.vpnName)+" /disconnect");
        return os.system("rasdial "+( x if x else self.vpnName)+" /disconnect")

    def removeVPN(self, x=''):
        name = x if x else self.vpnName
        cmd = 'Remove-VpnConnection '
        cmd += '-Force '+name

        if os.system("rasdial "+name) == 623: return os.system("powershell " + cmd)
        return False
        pass

proc = OpenVPN()
# proc.connect()

# reference
# https://www.tenforums.com/tutorials/90305-set-up-add-vpn-connection-windows-10-a.html
# https://docs.microsoft.com/en-us/powershell/module/vpnclient/set-vpnconnectiontriggerdnsconfiguration?view=win10-ps
