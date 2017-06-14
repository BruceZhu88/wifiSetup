#coding=utf-8
#
# Author: Bruce Zhu
#


import time
import re
import json
import subprocess
import logging

from utility.urlRequest import urlRequest

urlRequest = urlRequest()

class ASE():
    def __init__(self):
        pass

    def reset(self, destIP):
        logging.log(logging.INFO, "Doing factory reset for %s..."%destIP)
        url = "http://{ip}/api/setData?path=beo_LocalUI%3AfactoryResetRequest&roles=activate&value=%7B%22type%22%3A%22bool_%22%2C%22bool_%22%3Atrue%7D&"
        urlRequest.post(url.format(ip=destIP))

    def scanWifi(self):
        url = "http://192.168.1.1/api/getRows?path=network%3Ascan_results&roles=title%2Cvalue&from=0&to=99&"

    def setupWifi(self, wifissid, pwd, encryption):
        logging.log(logging.INFO, "Setup wifi ssid=%s key=%s"%(wifissid,pwd))

        Beoweb = urlRequest.get("http://192.168.1.1/api/getData?path=BeoWeb%3A%2Fnetwork&roles=value&")
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
            if urlRequest.post(url):
                return True
        except:
            logging.log(logging.INFO, "Post %s error"%url)
        return False
        #logging.log(logging.INFO, returnValue.status_code)

    def getInfo(self,ip):
        data = urlRequest.get("http://{ip}/index.fcgi".format(ip=ip))
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

        deviceName = urlRequest.get("http://{ip}/api/getData?path=settings%3A%2FdeviceName&roles=value&".format(ip=ip))
        deviceName = json.loads(deviceName, encoding="utf-8")
        info["deviceName"] = deviceName[0]["string_"]
        return info

    def find_IP(self, deviceName):
        #Judge sc query "Bonjour Service"
        logging.log(logging.INFO, "Finding IP...")
        p = subprocess.Popen("sc query \"Bonjour Service\"",shell=True,stdout=subprocess.PIPE)
        p.wait()
        content = p.stdout.read().decode("utf-8")
        STATE = re.findall(u"STATE.*", content)[0]
        if "STOPPED" in STATE:
            logging.log(logging.INFO, "Start Bonjour Service...(If failed, please run it as Administrater!)")
            p = subprocess.Popen("net start \"Bonjour Service\"",shell=True,stdout=subprocess.PIPE)
            p.wait()
            time.sleep(2)
        from utility.ase_finder import deviceScan
        logging.log(logging.INFO, "Device scanning...")
        deviceScan = deviceScan()
        deviceScan.scan()
        times = deviceScan.times_scan
        info = deviceScan.info
        if times != 0:
            for i in range(1,times+1):
                friendlyName = info["friendlyName_"+str(i)]
                if deviceName in friendlyName:
                    ip = info["ipaddr_"+str(i)]
                    logging.log(logging.INFO, "IP=%s             ----Successfully!"%ip)
                    return ip
        return ""
        """
        p = subprocess.Popen("arp -a",shell=True,stdout=subprocess.PIPE)
        p.wait()
        content = p.stdout.read().decode("GB2312")
        tmp = re.findall(u".*%s"%self.ipType,content)
        try:
            for i in tmp:
                ip = i.split(" ")[2]
                if urlRequest.post("http://{ip}/index.fcgi".format(ip=ip)):
                    info = self.getInfo(ip)
                    #logging.log(logging.INFO, info)
                    if deviceName in info["deviceName"]:
                        logging.log(logging.INFO, "             ----Successfully!")
                        return ip
        except:
            logging.log(logging.INFO, "arp error!!!")
            return ""
        return ""
        """