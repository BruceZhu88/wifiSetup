import os
import re
import requests
import urllib.request
import json
import time
import subprocess

def connect_wifi(name):
    p = os.popen("netsh wlan connect name=\"%s\"" % name)
    content = p.read()
    print(content)
    #os.system("netsh wlan connect name=%s" % name)

def check_wifi(wifiName):
    p = os.popen("netsh wlan show interfaces")
    content = p.read()
    #print(content)
    try:
        wifiSSID = re.findall(u"SSID(.*)",content)[0].split(": ")[1]
        wifiState = re.findall(u"State(.*)",content)[0].split(": ")[1]
        if wifiSSID == wifiName:
            if wifiState == "connected":
                print("Wifi %s connected!"%wifiName)
                return True
        return False
    except:
        return False

def find_wifi(str):
    print("Finding wifi %s  ..."%str)
    p = subprocess.Popen("netsh wlan disconnect",shell=True)# win10 system cannot auto refresh wifi list, so disconnect it first
    p.wait()
    #p = os.popen("netsh wlan show networks") #netsh wlan show networks mode=bssid
    #content = p.read().decode("gbk", "ignore")

    p = subprocess.Popen("netsh wlan show networks",shell=True,stdout=subprocess.PIPE)
    content = p.stdout.read().decode()
    temp = re.findall(u"SSID.*",content)
    for i in temp:
        ssid = re.findall(u"SSID(.*)",i)[0].split(" : ")[1].replace("\r","")
        if ssid == str:
            print("Find [%s]"%str)
            return True
    return False

def urlRequests(url):
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

def get_data(url):
    try:
        data = urllib.request.urlopen(url, timeout = 8)
        text = data.read().decode("utf8")# note that Python3 does not read the html code as string
        data.close()
        return text
    except:
        return ''
        #print('Your device seems disconnected!\n')

#CA17 operation
def reset(destIP):
    print("Do factory reset for %s..."%destIP)
    url = "http://{ip}/api/setData?path=beo_LocalUI%3AfactoryResetRequest&roles=activate&value=%7B%22type%22%3A%22bool_%22%2C%22bool_%22%3Atrue%7D&"
    urlRequests(url.format(ip=destIP))



def scanWifi():
    url = "http://192.168.1.1/api/getRows?path=network%3Ascan_results&roles=title%2Cvalue&from=0&to=99&"

def getBeoweb():
    url = "http://192.168.1.1/api/getData?path=BeoWeb%3A%2Fnetwork&roles=value&"
    Beoweb = get_data(url)
    return Beoweb

def setupWifi(wifissid, pwd, encryption):
    print("Setup wifi ssid=%s key=%s"%(wifissid,pwd))

    Beoweb = getBeoweb()
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
    returnValue = requests.post(url)
    #print(returnValue.status_code)
    #urlRequests(url)
    return returnValue.status_code

def getInfo(ip):
    data = get_data("http://{ip}/index.fcgi".format(ip=ip))
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

    return info

def find_IP(model):
    p = subprocess.Popen("arp -a",shell=True,stdout=subprocess.PIPE)
    p.wait()
    try:
        content = p.stdout.read().decode()
        temp = re.findall(u".*dynamic",content)
        for i in temp:
            ip = i.replace(i[-29:],"").replace(" ","")
            if urlRequests("http://{ip}/index.fcgi".format(ip=ip)):
                info = getInfo(ip)
                #print(info)
                if (model in info["modelName"]) or (model in info["model"]) or (model in info["productName"]):
                    return ip
    except:
        print("arp error!!!")
        return ""

    return ""

if __name__=="__main__":

    TestWifi = "D-Link_DIR-850L_5GHz"
    TestWifiPwd = "9876543210."
    encryption = "wpa_psk"

    SN = "00094760"
    model = "M3" #CA17
    productName = "Beoplay M3_00094760"

    #hostName = "beoplay-{model}-{SN}.local".format(model=model, SN=SN)
    hostUrl = "http://{host}//index.fcgi"

    for cycle in range(1,2):
        print("This is the %d times "%cycle+"*"*60)
        while True:
            if find_wifi(productName):
                connect_wifi(productName)
                time.sleep(10)#Give wifi connect some time
                if check_wifi(productName):
                    break
            time.sleep(3)

        statusCode = setupWifi(TestWifi, TestWifiPwd, encryption)
        """
        if statusCode == 200:
            print("Wifi setup command has been sent!")
            if find_wifi(TestWifi):
                connect_wifi(TestWifi)
                time.sleep(10)#Give wifi connect some time
                if check_wifi(TestWifi):
                    for i in range(0,15):
                        ip = find_IP(model)
                        if ip != "":
                            break
                        time.sleep(3)
                        print("sleep 3 seconds")
                    if i!=14:
                        urlRequests(hostUrl.format(host=ip))
                        reset(ip)
                        time.sleep(20)
                else:
                    break
                    print("Cannot connect wifi %s"%TestWifi)
        """





