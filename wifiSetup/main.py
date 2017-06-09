#coding=utf-8
#
#
# Note: If your sample is first test on this PC,
# please manully connet it(Hotspot), and create a wifi(free) profile for it
# If you still have a problem, you can search key words "create win7 wifi
# profile" on Baidu, then you can go to CMD "netsh wlan show profiles" to
# check if it is successful
#
# Author: Bruce Zhu
#
import os
import re
import requests
import urllib.request
import json
import time
import subprocess
import ctypes


#*************************************************************
# Chinese: 0x804
# English: 0x409
dll_handle = ctypes.windll.kernel32
id = hex(dll_handle.GetSystemDefaultUILanguage())
if id=="0x804":
    system_language = "Chinese"
elif id=="0x409":
    system_language = "English"
else:
    system_language = ""

#*************************************************************
class wifiSetup():
    def __init__(self):
        if system_language=="Chinese":
            self.wifiState = "已连接"
            self.wifiStateFind = "状态"
            self.ipType = "动态"
        elif system_language=="English":
            self.wifiState = "connected"
            self.wifiStateFind = "State"
            self.ipType = "dynamic"

    def connect_wifi(self, name):
        p = os.popen("netsh wlan connect name=\"%s\"" % name)
        content = p.read()
        print(content)
        #os.system("netsh wlan connect name=%s" % name)

    def check_wifi(self, wifiName):
        p = os.popen("netsh wlan show interfaces")
        content = p.read()
        #print(content)
        try:
            wifiSSID = re.findall(u"SSID(.*)",content)[0].split(": ")[1]
            wifiState = re.findall(u"%s(.*)"%self.wifiStateFind,content)[0].split(": ")[1]
            print(wifiState)
            if wifiSSID == wifiName:
                if wifiState == self.wifiState:
                    print("Wifi %s connected!"%wifiName)
                    return True
            return False
        except:
            return False

    def find_wifi(self, str):
        print("Finding wifi %s  ..."%str)
        p = subprocess.Popen("netsh wlan disconnect",shell=True)# win10 system cannot auto refresh wifi list, so disconnect it first
        p.wait()
        #p = os.popen("netsh wlan show networks") #netsh wlan show networks mode=bssid
        #content = p.read().decode("gbk", "ignore")

        p = subprocess.Popen("netsh wlan show networks",shell=True,stdout=subprocess.PIPE)
        content = p.stdout.read().decode("GB2312") # byte decode to str, and GB2312 is avoid Chinese strings.

        temp = re.findall(u"SSID.*",content)
        for i in temp:
            ssid = re.findall(u"SSID(.*)",i)[0].split(" : ")[1].replace("\r","")
            if ssid == str:
                print("Find [%s]"%str)
                return True
        return False

    def urlRequests(self, url):
        try:
            r = requests.get(url, allow_redirects = False)
            status = r.status_code
            #r.text
            if status == 200:
                print('Request to %s'%url)
                return True
            else:
                print('Cannot request to %s'%url)
                return False
        except:
            print('Cannot request to %s'%url)
            return False

    def get_data(self, url):
        try:
            data = urllib.request.urlopen(url, timeout = 8)
            text = data.read().decode("utf8")# note that Python3 does not read the html code as string
            data.close()
            return text
        except:
            return ''
            #print('Your device seems disconnected!\n')

    #CA17 operation
    def reset(self, destIP):
        print("Do factory reset for %s..."%destIP)
        url = "http://{ip}/api/setData?path=beo_LocalUI%3AfactoryResetRequest&roles=activate&value=%7B%22type%22%3A%22bool_%22%2C%22bool_%22%3Atrue%7D&"
        self.urlRequests(url.format(ip=destIP))

    def scanWifi(self):
        url = "http://192.168.1.1/api/getRows?path=network%3Ascan_results&roles=title%2Cvalue&from=0&to=99&"

    def getBeoweb(self):
        url = "http://192.168.1.1/api/getData?path=BeoWeb%3A%2Fnetwork&roles=value&"
        Beoweb = self.get_data(url)
        return Beoweb

    def setupWifi(self, wifissid, pwd, encryption):
        print("Setup wifi ssid=%s key=%s"%(wifissid,pwd))

        Beoweb = self.getBeoweb()
        data = json.loads(Beoweb, encoding="utf-8")
        vendorSpecificData = data[0]["networkProfile"]["softApSettings"]["vendorSpecificData"]
        Beossid = data[0]["networkProfile"]["softApSettings"]["ssid"]
        dhcpRangeFrom = "192.168.1.20"
        apAddress = "192.168.1.1"

        value = "http://192.168.1.1/api/setData?path=BeoWeb%3A%2Fnetwork&roles=activate&value=%7B"
        networkProfile = "%22networkProfile%22%3A%7B"
        softApSettings1 = "%22softApSettings%22%3A%7B%22manualSwitch%22%3Atrue%2C%22apNetmask%22%3A%22255.255.255.0%22%2C%22dhcpNetmask%22%3A%22255.255.255.0%22%2C%22channel%22%3A1%2C%22targetType%22%3A%22automatic%22%2C%22dhcpRangeTo%22%3A%22192.168.1.200%22%2C%22vendorSpecificData%22%3A%22{vendorSpecificData}%22%2C".format(vendorSpecificData=vendorSpecificData)
        softApSettings2 = "%22ssid%22%3A%22{Beossid}%22%2C%22dhcpRangeFrom%22%3A%22{dhcpRangeFrom}%22%2C%22apAddress%22%3A%22{apAddress}%22%7D%2C".format(Beossid=Beossid, dhcpRangeFrom=dhcpRangeFrom, apAddress=apAddress)
        wireless = "%22wireless%22%3A%7B%22dhcp%22%3Atrue%2C%22ip%22%3A%22%22%2C%22netmask%22%3A%22%22%2C%22gateway%22%3A%22%22%2C%22dns%22%3A%5B%22%22%2C%22%22%5D%2C%22ssid%22%3A%22{ssid}%22%2C%22encryption%22%3A%22{encryption}%22%2C%22key%22%3A%22{key}%22%7D%2C".format(ssid=wifissid, encryption=encryption, key=pwd)
        wired = "%22wired%22%3A%7B%22dhcp%22%3Atrue%2C%22ip%22%3A%22%22%2C%22netmask%22%3A%22%22%2C%22gateway%22%3A%22%22%2C%22dns%22%3A%5B%22%22%2C%22%22%5D%7D%2C"
        profileType = "%22type%22%3A%22automatic%22%7D%2C"
        networkType = "%22type%22%3A%22networkProfile%22%7D&"

        url = value+networkProfile+softApSettings1+softApSettings2+wireless+wired+profileType+networkType
        try:
            returnValue = requests.post(url)
            return returnValue.status_code
        except:
            print("Post %s error"%url)
            return ""
        #print(returnValue.status_code)
        #urlRequests(url)


    def getInfo(self,ip):
        data = self.get_data("http://{ip}/index.fcgi".format(ip=ip))
        data = re.findall(u"dataJSON = .*",data)[0]
        data = data.replace(data[-2:],"")
        data = data.replace(data[:12],"")

        data = json.loads(data, encoding="utf-8")

        info = {}
        info["modelName"] = data["beoMachine"]["modelName"]
        info["model"] = data["beoMachine"]["model"]
        info["productName"] = data["beoMachine"]["setup"]["productName"]
        info["bootloaderVersion"] = data["beoMachine"]["fepVersions"]["bootloaderVersion"]
        info["appVersion"] = data["beoMachine"]["fepVersions"]["appVersion"]

        deviceName = self.get_data("http://{ip}/api/getData?path=settings%3A%2FdeviceName&roles=value&".format(ip=ip))
        deviceName = json.loads(deviceName, encoding="utf-8")
        info["deviceName"] = deviceName[0]["string_"]
        return info

    def find_IP(self, deviceName):
        p = subprocess.Popen("arp -a",shell=True,stdout=subprocess.PIPE)
        p.wait()
        content = p.stdout.read().decode("GB2312")
        tmp = re.findall(u".*%s"%self.ipType,content)
        try:
            for i in tmp:
                ip = i.split(" ")[2]
                if self.urlRequests("http://{ip}/index.fcgi".format(ip=ip)):
                    info = self.getInfo(ip)
                    #print(info)
                    if deviceName in info["deviceName"]:
                        print("             ----Successfully!")
                        return ip
        except:
            print("arp error!!!")
            return ""
        return ""


    def test(self):
        true = True 
        value = {"networkProfile":{"softApSettings":{"manualSwitch":true,"apNetmask":"255.255.255.0","dhcpNetmask":"255.255.255.0","channel":1,"targetType":"automatic","dhcpRangeTo":"192.168.1.200","vendorSpecificData":"dd4f00a040000706501e2d0093260002f003011342656f706c6179204d335f3030303934373630031853747265616d383030204576616c756174696f6e204b6974020e42616e67416e644f6c756673656e","ssid":"Beoplay M3_00094760","dhcpRangeFrom":"192.168.1.20","apAddress":"192.168.1.1"},"wireless":{"dhcp":true,"ip":"","netmask":"","gateway":"","dns":["",""],"ssid":"D-Link_DIR-850L_5GHz","encryption":"wpa_psk","key":"9876543210."},"wired":{"dhcp":true,"ip":"","netmask":"","gateway":"","dns":["",""]},"type":"automatic"},"type":"networkProfile"}

        value_encoded = urllib.parse.urlencode(value)
        print(value_encoded)

        url = "http://192.168.1.1/api/setData?path=BeoWeb%3A%2Fnetwork&roles=activate&value=%7B%22networkProfile%22%3A%7B%22softApSettings%22%3A%7B%22manualSwitch%22%3Atrue%2C%22apNetmask%22%3A%22255.255.255.0%22%2C%22dhcpNetmask%22%3A%22255.255.255.0%22%2C%22channel%22%3A1%2C%22targetType%22%3A%22automatic%22%2C%22dhcpRangeTo%22%3A%22192.168.1.200%22%2C%22vendorSpecificData%22%3A%22dd4f00a040000706501e2d0093260002f003011342656f706c6179204d335f3030303934373630031853747265616d383030204576616c756174696f6e204b6974020e42616e67416e644f6c756673656e%22%2C%22ssid%22%3A%22Beoplay+M3_00094760%22%2C%22dhcpRangeFrom%22%3A%22192.168.1.20%22%2C%22apAddress%22%3A%22192.168.1.1%22%7D%2C%22wireless%22%3A%7B%22dhcp%22%3Atrue%2C%22ip%22%3A%22%22%2C%22netmask%22%3A%22%22%2C%22gateway%22%3A%22%22%2C%22dns%22%3A%5B%22%22%2C%22%22%5D%2C%22ssid%22%3A%22D-Link_DIR-850L_5GHz%22%2C%22encryption%22%3A%22wpa_psk%22%2C%22key%22%3A%229876543210.%22%7D%2C%22wired%22%3A%7B%22dhcp%22%3Atrue%2C%22ip%22%3A%22%22%2C%22netmask%22%3A%22%22%2C%22gateway%22%3A%22%22%2C%22dns%22%3A%5B%22%22%2C%22%22%5D%7D%2C%22type%22%3A%22automatic%22%7D%2C%22type%22%3A%22networkProfile%22%7D&_nocache=1497005374399"

        print(urllib.parse.unquote(url))

if __name__=="__main__":
    wifiSetup = wifiSetup()

    TestWifi = "D-Link_DIR-850L_5GHz"
    TestWifiPwd = "9876543210."
    encryption = "wpa_psk"

    SN = "00094760"
    model = "M3" #CA17
    productName = "Beoplay M3_00094760"

    #hostName = "beoplay-{model}-{SN}.local".format(model=model, SN=SN)
    hostUrl = "http://{host}//index.fcgi"


    '''

    for cycle in range(1,20):
        print("This is the %d times "%cycle+"*"*60)
        while True:
            if wifiSetup.find_wifi(productName):
                wifiSetup.connect_wifi(productName)
                time.sleep(10)#Give wifi connect some time
                if wifiSetup.check_wifi(productName):
                    break
            time.sleep(3)

        statusCode = wifiSetup.setupWifi(TestWifi, TestWifiPwd, encryption)
        if statusCode == 200:
            print("Wifi setup command has been sent!")
            if wifiSetup.find_wifi(TestWifi):
                wifiSetup.connect_wifi(TestWifi)
                time.sleep(10)#Give wifi connect some time
                if wifiSetup.check_wifi(TestWifi):
                    for i in range(0,15):
                        ip = wifiSetup.find_IP(productName)
                        if ip != "":
                            break
                        time.sleep(3)
                        print("sleep 3 seconds")
                    if i==14:
                        print("Cannot find IP")
                        break
                    else:
                        wifiSetup.urlRequests(hostUrl.format(host=ip))
                        wifiSetup.reset(ip)
                        time.sleep(30)
                else:
                    print("Cannot connect wifi %s"%TestWifi)
                    break
    '''


    wifiSetup.test()
