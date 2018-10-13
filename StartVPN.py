import requests, re, os, sys, time, uuid, ping, subprocess
from bs4 import BeautifulSoup
from os import *
from pathlib import Path
#Thankyou for "https://freevpn.me"

#
#auther : ZED
# reference
# https://www.tenforums.com/tutorials/90305-set-up-add-vpn-connection-windows-10-a.html
# https://docs.microsoft.com/en-us/powershell/module/vpnclient/set-vpnconnectiontriggerdnsconfiguration?view=win10-ps

class OpenVPN:

    def __init__(self):
        self.account = {}
        self.homepages = []
        self.reg = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)|(Username:.+li)|(Password:.+li)')
        self.regUrl = re.compile(r'https?://(www.)?freevpn\..*\.?[a-zA-Z]$')
        self.getServerList()
        self.netChecker = ping.PING()

    def getServerList(self):
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
            try:
                rs = self.reg.search(str(x)).group().split(" ")
                if "Password" in rs[0] and self.account['pw'] == '': self.account.update({ 'pw' : rs[1].replace("</li", '') })
                elif self.account['host'] =='' and len(rs) == 1: self.account.update({'host': rs[0] })
            except:
                pass

    def disconnect(self, vpnName='', all=False):
        if "win" in sys.platform:
            if all:
                return system("rasdial /disconnect")
            else:
                return system("rasdial "+vpnName+" /disconnect")
        else:
            removeRouteCmd = "VPNI=`route -n | egrep -v UGH | grep UG | awk '{print $8}'` && "
            removeRouteCmd += "VPNGW=`route -n | grep $VPNI | head -n 1 | awk '{print $2}'` && "
            removeRouteCmd += "DI=`route -n | grep UGH | awk '{print $8}'` && "
            removeRouteCmd += "DGW=`route -n | grep $DI | head -n 1 | awk '{print $2}'` && "

            removeRouteCmd += "echo DI: $DI && "
            removeRouteCmd += "echo DGW: $DGW && "
            removeRouteCmd += "echo VPNI: $VPNI && "
            removeRouteCmd += "echo VPNGW: $VPNGW && "

            removeRouteCmd += "sudo route add default gw $DGW dev $DI && "
            removeRouteCmd += "sudo route del default gw $VPNGW dev $VPNI"

            system(removeRouteCmd)
        
    def removeVPN(self, vpnName=''):
        if "win" in sys.platform:
            cmd = 'Remove-VpnConnection '
            cmd += '-Force '+vpnName
            return system("powershell " + cmd)
        else:
            return system("killall pppd")
    def getPublicIP(self):
        rs = requests.get("http://www.findip.kr/where.php", verify=False)
        if rs.status_code != 200: raise ValueError
        soup = BeautifulSoup(rs.text, 'html.parser')
        for x in soup.find_all("input"):
            if x['id'] == "ip": return x['value']
    
    def connect(self, vpnName=''):
        try:
            # start windows
            system("echo off")
            for url in self.homepages:
                vpnName = vpnName if vpnName else str(uuid.uuid4()).split("-")[4]
                self.updateAccount(url)
                print("Disconnecting All VPN's")
                
                if "win" in sys.platform:
                    self.disconnect(all=True)
                    cmd = 'Add-VpnConnection '
                    cmd += '-Name "'+vpnName+'" '
                    cmd += '-ServerAddress "'+self.account['host']+'" '
                    cmd += '-TunnelType "PPTP" '
                    cmd += '-EncryptionLevel "Required" '
                    # cmd += '-SplitTunneling '
                    # cmd += '-Force '
                    cmd += '-RememberCredential ' # this option no get gateway from vpn server
                    cmd += '-AuthenticationMethod MsChapv2 '
                    cmd += '-PassThru'

                    checkVPN = system("rasdial " + vpnName)
                    if checkVPN == 623 or checkVPN ==0: system("powershell " + cmd)
                    connectcmd = "rasdial "+ vpnName + ' "' + self.account['id'] + '" "' + self.account['pw']+'"'
                    connectCode = system(connectcmd)

                    if connectCode == 807: self.removeVPN(vpnName); print("Re connectting... "); continue
                    elif proc.getPublicIP() == self.account['host']: print("connected!")
                    else: print("conneciton Failed")
                    try:
                        system("cls")
                        self.netChecker.run_th_ping("8.8.8.8")
                    except KeyboardInterrupt:
                        print("Start disconnectiong.....wait for")
                        self.disconnect()
                        self.removeVPN(vpnName)
                        print("Disconnected!! & Remove VPN")
                        sys.exit(0)
                    except Exception as e:
                        print("Error : ", e)
                        print("Start disconnectiong.....wait for")
                        self.disconnect()
                        self.removeVPN(vpnName)
                        print("Disconnected!! & Remove VPN")
                        sys.exit(0)
                    finally:
                        print("exit")
                        sys.exit(0)
                else:
                    # start linux
                    if self.prompt_sudo() != 0:
                        print("the user wasn't authenticated as a sudoer")
                        sys.exit(0)
                    else:
                        if not Path("/usr/sbin/pptpsetup").exists(): system("apt update && apt install pptp-linux && apt autoremove")
                        print("[+] Start connecting FreeVPN")
                        system("sudo pptpsetup --create {0} --server {1} --username pptp --password {2} --start --encrypt".format(vpnName, self.account['host'], self.account['pw']))
                        setRouteCmd = "DI=`route -n | egrep -v UGH | grep UG | awk '{print $8}'` && "
                        setRouteCmd += "DGW=`route -n | grep $DI | head -n 1 | awk '{print $2}'` && "
                        setRouteCmd += "VPNI=`route -n | egrep -v UGH | grep UH | awk '{print $8}'` && "
                        setRouteCmd += "VPNGW=`route -n | grep $VPNI | head -n 1 | awk '{print $1}'` && "

                        setRouteCmd += "echo DI: $DI && "
                        setRouteCmd += "echo DGW: $DGW && "
                        setRouteCmd += "echo VPNI: $VPNI && "
                        setRouteCmd += "echo VPNGW: $VPNGW && "

                        setRouteCmd += "sudo route add default gw $VPNGW  dev $VPNI && "
                        setRouteCmd += "sudo route del default gw $DGW dev $DI"
                        print("error code : ", )
                        if system(setRouteCmd) > 0: continue
                        try:
                            system("clear")
                            self.netChecker.run_th_ping("8.8.8.8")
                        except Exception as e:
                            print("Error : ", e)
                            print("Start disconnectiong.....wait for")
                            self.disconnect()
                            self.removeVPN(vpnName)
                            print("Disconnected!! & Remove VPN")
                            sys.exit(0)
                        finally:
                            print("Start disconnectiong.....wait for")
                            self.disconnect()
                            self.removeVPN(vpnName)
                            print("Disconnected!! & Remove VPN")
                            print("exit")
                            sys.exit(0)
        except Exception as e:
            print("connect error : ", e)
    
    # linux function area
    def prompt_sudo(self):
        ret = 0
        if geteuid() != 0:
            msg = "[sudo] password for %u:"
            ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
        return ret

if __name__ == '__main__':
    proc = OpenVPN()
    proc.connect()


