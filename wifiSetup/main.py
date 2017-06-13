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
import logging
from utility.config import getconfig
from utility.logger import Logger
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
#Initialization

data = getconfig.getparameters('./config.ini')  


TestWifi = data["config"]["TestWifi"] 
TestWifiPwd = data["config"]["TestWifiPwd"]
encryption = data["config"]["encryption"]
SN = data["config"]["SN"]
deviceName = data["config"]["deviceName"]


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
        logging.log(logging.INFO, content)
        #os.system("netsh wlan connect name=%s" % name)

    def check_wifi(self, wifiName):
        p = os.popen("netsh wlan show interfaces")
        content = p.read()
        #logging.log(logging.INFO, content)
        try:
            wifiSSID = re.findall(u"SSID(.*)",content)[0].split(": ")[1]
            wifiState = re.findall(u"%s(.*)"%self.wifiStateFind,content)[0].split(": ")[1]
            #logging.log(logging.INFO, wifiState)
            if wifiSSID == wifiName:
                if wifiState == self.wifiState:
                    logging.log(logging.INFO, "Wifi %s connected!"%wifiName)
                    return True
            return False
        except:
            return False

    def find_wifi(self, str):
        logging.log(logging.INFO, "Finding wifi %s  ..."%str)
        p = subprocess.Popen("netsh wlan disconnect",shell=True)# win10 system cannot auto refresh wifi list, so disconnect it first
        p.wait()
        #p = os.popen("netsh wlan show networks") #netsh wlan show networks mode=bssid
        #content = p.read().decode("gbk", "ignore")

        p = subprocess.Popen("netsh wlan show networks",shell=True,stdout=subprocess.PIPE)
        try:
            content = p.stdout.read().decode("GB2312") # byte decode to str, and GB2312 is avoid Chinese strings.
        except:

            content = p.stdout.read().decode("utf-8")
        temp = re.findall(u"SSID.*",content)
        for i in temp:
            ssid = re.findall(u"SSID(.*)",i)[0].split(" : ")[1].replace("\r","")
            if ssid == str:
                logging.log(logging.INFO, "Find [%s]"%str)
                return True
        return False

    def urlRequests(self, url):
        try:
            r = requests.get(url, allow_redirects = False)
            status = r.status_code
            #r.text
            if status == 200:
                logging.log(logging.INFO, 'Request to %s'%url)
                return True
            else:
                logging.log(logging.INFO, 'Cannot request to %s'%url)
                return False
        except:
            logging.log(logging.INFO, 'Cannot request to %s'%url)
            return False

    def url_open(self, url):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36")

            response = urllib.request.urlopen(url, timeout = 8)
            html = response.read().decode("utf8")# note that Python3 does not read the html code as string
            response.close()
            return html
        except:
            return ''
            #logging.log(logging.INFO, 'Your device seems disconnected!\n')

    #CA17 operation
    def reset(self, destIP):
        logging.log(logging.INFO, "Do factory reset for %s..."%destIP)
        url = "http://{ip}/api/setData?path=beo_LocalUI%3AfactoryResetRequest&roles=activate&value=%7B%22type%22%3A%22bool_%22%2C%22bool_%22%3Atrue%7D&"
        self.urlRequests(url.format(ip=destIP))

    def scanWifi(self):
        url = "http://192.168.1.1/api/getRows?path=network%3Ascan_results&roles=title%2Cvalue&from=0&to=99&"

    def getBeoweb(self):
        url = "http://192.168.1.1/api/getData?path=BeoWeb%3A%2Fnetwork&roles=value&"
        Beoweb = self.url_open(url)
        return Beoweb

    def setupWifi(self, wifissid, pwd, encryption):
        logging.log(logging.INFO, "Setup wifi ssid=%s key=%s"%(wifissid,pwd))

        Beoweb = self.getBeoweb()
        data = json.loads(Beoweb, encoding="utf-8")
        vendorSpecificData = data[0]["networkProfile"]["softApSettings"]["vendorSpecificData"]
        Beossid = data[0]["networkProfile"]["softApSettings"]["ssid"]
        dhcpRangeFrom = "192.168.1.20"
        apAddress = "192.168.1.1"
        '''
        data[0]["networkProfile"]["wireless"]["ip"] = ""
        data[0]["networkProfile"]["wireless"]["netmask"] = ""
        data[0]["networkProfile"]["wireless"]["gateway"] = ""
        data[0]["networkProfile"]["wireless"]["dns"] = ["",""]
        data[0]["networkProfile"]["wireless"]["ssid"] = "Astrill"
        data[0]["networkProfile"]["wireless"]["encryption"] = "wpa_psk"
        data[0]["networkProfile"]["wireless"]["key"] = "way2stars"

        data[0]["networkProfile"]["wired"]["ip"] = ""
        data[0]["networkProfile"]["wired"]["netmask"] = ""
        data[0]["networkProfile"]["wired"]["gateway"] = ""
        data[0]["networkProfile"]["wired"]["dns"] = ["",""]
        
        logging.log(logging.INFO, data, "\n\n\n")
        logging.log(logging.INFO, json.dumps(data, indent=2),'\n\n\n')
        value_encoded = urllib.parse.urlencode(data[0], encoding="utf-8")
        logging.log(logging.INFO, value_encoded)
        '''
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
            logging.log(logging.INFO, "Post %s error"%url)
            return ""
        #logging.log(logging.INFO, returnValue.status_code)
        #urlRequests(url)

    def getInfo(self,ip):
        data = self.url_open("http://{ip}/index.fcgi".format(ip=ip))
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

        deviceName = self.url_open("http://{ip}/api/getData?path=settings%3A%2FdeviceName&roles=value&".format(ip=ip))
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
                    #logging.log(logging.INFO, info)
                    if deviceName in info["deviceName"]:
                        logging.log(logging.INFO, "             ----Successfully!")
                        return ip
        except:
            logging.log(logging.INFO, "arp error!!!")
            return ""
        return ""


if __name__=="__main__":
    wifiSetup = wifiSetup()
    #hostName = "beoplay-{model}-{SN}.local".format(model=model, SN=SN)
    hostUrl = "http://{host}//index.fcgi"
    
    Logger.init_logger('project.log')

    for cycle in range(1,20):
        logging.log(logging.INFO, "This is the %d times "%cycle+"*"*60)
        while True:
            if wifiSetup.find_wifi(deviceName):
                wifiSetup.connect_wifi(deviceName)
                time.sleep(10)#Give wifi connect some time
                if wifiSetup.check_wifi(deviceName):
                    break
            time.sleep(3)

        statusCode = wifiSetup.setupWifi(TestWifi, TestWifiPwd, encryption)
        if statusCode == 200:
            logging.log(logging.INFO, "Wifi setup command has been sent!")
            if wifiSetup.find_wifi(TestWifi):
                wifiSetup.connect_wifi(TestWifi)
                time.sleep(10)#Give wifi connect some time
                if wifiSetup.check_wifi(TestWifi):
                    for i in range(0,15):
                        ip = wifiSetup.find_IP(deviceName)
                        if ip != "":
                            break
                        time.sleep(3)
                        logging.log(logging.INFO, "sleep 3 seconds")
                    if i==14:
                        logging.log(logging.INFO, "Cannot find IP")
                        break
                    else:
                        wifiSetup.urlRequests(hostUrl.format(host=ip))
                        wifiSetup.reset(ip)
                        time.sleep(30)
                else:
                    logging.log(logging.INFO, "Cannot connect wifi %s"%TestWifi)
                    break
