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
import time
import ctypes
import logging
from utility.config import getconfig
from utility.logger import Logger
from utility.windowsWifi import windowsWifi
from utility.ASE import ASE
from utility.urlRequest import urlRequest
from utility.progressBar import ProgressBar

urlRequest = urlRequest()
progressBar = ProgressBar()
#*************************************************************
#Initialization

data = getconfig.getparameters('./config.ini')

TestWifi = data["config"]["TestWifi"]
TestWifiPwd = data["config"]["TestWifiPwd"]
encryption = data["config"]["encryption"]
deviceName = data["config"]["deviceName"]
TimeReset = data["config"]["TimeReset"]
#*************************************************************
def main():
    wifi = windowsWifi()
    ase = ASE()
    #hostName = "beoplay-{model}-{SN}.local".format(model=model, SN=SN)
    hostUrl = "http://{host}//index.fcgi"
    Logger.init_logger('project.log')

    for cycle in range(1,20):
        logging.log(logging.INFO, "This is the %d times "%cycle+"*"*60)
        while True:
            if wifi.find_wifi(deviceName):
                wifi.connect_wifi(deviceName)
                time.sleep(10)#Give wifi connect some time
                if wifi.check_wifi(deviceName):
                    break
            time.sleep(3)

        if ase.setupWifi(TestWifi, TestWifiPwd, encryption):
            logging.log(logging.INFO, "Wifi setup command has been sent!")
            if wifi.find_wifi(TestWifi):
                wifi.connect_wifi(TestWifi)
                time.sleep(10)#Give wifi connect some time
                if wifi.check_wifi(TestWifi):
                    for i in range(0,15):
                        ip = ase.find_IP(deviceName)
                        if ip != "":
                            break
                        time.sleep(3)
                    if i==14:
                        logging.log(logging.INFO, "Cannot find IP")
                        break
                    else:
                        if urlRequest.post(hostUrl.format(host=ip)):
                            ase.reset(ip)
                            logging.log(logging.INFO, "Waiting %ss..."%TimeReset)
                            progressBar.sleep(int(TimeReset))
                else:
                    logging.log(logging.INFO, "Cannot connect wifi %s"%TestWifi)
                    break

if __name__=="__main__":
    main()
