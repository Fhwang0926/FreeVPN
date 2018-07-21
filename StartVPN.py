import requests, re, os, sys, time, uuid
from bs4 import BeautifulSoup
# freevpn

class OpenVPN:

    def __init__(self):
        self.account = {}
        self.homepages = []
        self.reg = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(Username:.+li)|(Password:.+li)')
        # self.reg = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(:<\/b>.+<)|(:<\/b>.+<)')
        self.regUrl = re.compile(r'https?://(www.)?freevpn\..*\.?[a-zA-Z]$')
        self.getServerList()
        self.log = []

        pass

    def getServerList(self):
        rs = requests.get("https://freevpn.se/accounts/", verify=False)
        if rs.status_code != 200: raise ValueError

        soup = BeautifulSoup(rs.text, 'html.parser')
        for x in soup.find_all('a'):
            try:
                rs = self.regUrl.search(x["href"]).group()
                if not "zip" in rs:
                    self.homepages.append(rs)
            except:
                pass


    def updateAccount(self, url=''):
        self.account['host'] = ''
        self.account['pw'] = ''
        if url == '': print("ServerList error : is null"); return
        print("[+] checkVPN : ", url)
        rs = requests.get(url+"/accounts/", verify=False)
        if rs.status_code != 200: raise ValueError
        soup = BeautifulSoup(rs.text, 'html.parser')
        self.account['id'] = "pptp"
        for x in soup.find_all('li'):
            if len(self.account.keys()) == 3: return
            try:
                rs = self.reg.search(str(x)).group().split(' ')
                if len(rs) > 1:
                    if "Password" in rs[0]: self.account.update({ 'pw' : rs[1].replace("</li", '') })
                else:
                    if self.account['host'] =='': self.account.update({'host': rs[0] })
            except:
                pass
            return

    def connect(self, vpnName=''):
        try:
            for url in self.homepages:
                vpnName = vpnName if vpnName else str(uuid.uuid4()).split("-")[4]
                self.updateAccount(url)
                print("Disconnecting All VPN's")
                if "win" in sys.platform:

                    os.system("rasdial /disconnect")

                    cmd = 'Add-VpnConnection '
                    cmd += '-Name "'+vpnName+'" '
                    cmd += '-ServerAddress "'+self.account['host']+'" '
                    cmd += '-TunnelType "PPTP" '
                    cmd += '-EncryptionLevel "Required" '
                    cmd += '-SplitTunneling '
                    cmd += '-Force '
                    # cmd += '-RememberCredential' # this option no get gateway from vpn server
                    cmd += '-AuthenticationMethod MsChapv2 '
                    cmd += '-PassThru'

                    checkVPN = os.system("rasdial " + vpnName)
                    if checkVPN == 623 or checkVPN ==0: os.system("powershell " + cmd)
                    connectcmd = "rasdial "+ vpnName + ' "' + self.account['id'] + '" "' + self.account['pw']+'"'
                    self.log.append(url+" | "+self.account['host']+" | "+connectcmd)
                    print(url, "|", self.account['host'], " | ", connectcmd)
                    if os.system(connectcmd) == 807: self.removeVPN(vpnName); print("Re connectting... "); continue
                    print("connected!")
                    # try:python3 s
                if not "win" in sys.platform:
                    print("This OS is Linux, not support")

        except Exception as e:
            print("connect error : ", e)

    def disconnect(self, x=''):
        print("rasdial "+( x if x else self.vpnName)+" /disconnect");
        return os.system("rasdial "+( x if x else self.vpnName)+" /disconnect")

    def removeVPN(self, x=''):
        name = x if x else self.vpnName
        cmd = 'Remove-VpnConnection '
        cmd += '-Force '+name
        print(os.system("powershell " + cmd))
        # if os.system("rasdial "+name) == 623: return
        return False
        pass
    def showlog(self):
        for x in self.log:
            print(x)
proc = OpenVPN()
proc.connect()
proc.showlog()
# reference
# https://www.tenforums.com/tutorials/90305-set-up-add-vpn-connection-windows-10-a.html
# https://docs.microsoft.com/en-us/powershell/module/vpnclient/set-vpnconnectiontriggerdnsconfiguration?view=win10-ps
