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
            vpnName = "JustFreeVPN"
            if "win" in sys.platform:
                print("Disconnecting All VPN's")
                os.system("rasdial /disconnect")

                cmd = 'Add-VpnConnection '
                cmd += '-Name "'+vpnName+'" '
                cmd += '-ServerAddress "'+self.accountInfo['host']+'" '
                cmd += '-TunnelType "PPTP" '
                cmd += '-EncryptionLevel "Required" '
                cmd += '-SplitTunneling -AuthenticationMethod MsChapv2 -RememberCredential -Force -PassThru'

                if os.system("rasdial "+vpnName) == 623: os.system("powershell " + cmd)
                connectcmd = "rasdial "+ vpnName + ' "' + self.accountInfo['id'] + '" "' + self.accountInfo['pw']+'"'
                os.system(connectcmd)
                print("[+] JustFreeVPN connected!")
            if not "win" in sys.platform:
                print("This OS is Linux, not support")

        except Exception as e:
            print("connect error : ", e)

    def cleaner(self,  data):
        rs = self.reg.findall(data)
        self.accountInfo['id'] = "pptp"
        for x in rs:
            if x[0]: self.accountInfo.update({'host' : self.removeTag(x[0])})
            # if x[1]: self.accountInfo.update({'id': self.removeTag(x[1]).split(':')[1].strip()})
            if x[2]: self.accountInfo.update({'pw': self.removeTag(x[2]).split(':')[1].strip()})

    def removeTag(self, x):
        return re.sub(r'<b>|</b>|</li|>|<', '', x)

proc = OpenVPN()
proc.connect()

# reference
# https://www.tenforums.com/tutorials/90305-set-up-add-vpn-connection-windows-10-a.html
# https://docs.microsoft.com/en-us/powershell/module/vpnclient/set-vpnconnectiontriggerdnsconfiguration?view=win10-ps
