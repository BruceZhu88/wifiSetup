#coding=utf-8
#
# Author: Bruce Zhu
#

import subprocess
import ctypes
import logging
import os
import time
import re

class windowsWifi():
    def __init__(self):
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
        if system_language=="Chinese":
            self.wifiState = "已连接"
            self.wifiStateFind = "状态"
            self.ipType = "动态"
        elif system_language=="English":
            self.wifiState = "connected"
            self.wifiStateFind = "State"
            self.ipType = "dynamic"

    def connect_wifi(self, name):
        logging.log(logging.INFO, "Try to connect wifi --> %s"%name)
        p = os.popen("netsh wlan connect name=\"{name}\"".format(name=name))
        content = p.read()
        logging.log(logging.INFO, content)
        #os.system("netsh wlan connect name=%s" % name)

    def wifi_status(self):
        logging.log(logging.INFO, "Checking wifi status...")
        p = os.popen("netsh wlan show interfaces")
        content = p.read()
        return content

    def check_wifi(self, wifiName):
        content = self.wifi_status()
        #logging.log(logging.INFO, content)
        for i in range(0,3):
            try:
                wifiSSID = re.findall(u"SSID(.*)",content)[0].split(": ")[1]
                wifiState = re.findall(u"%s(.*)"%self.wifiStateFind,content)[0].split(": ")[1]
                #logging.log(logging.INFO, wifiState)
                if wifiSSID == wifiName:
                    if wifiState == self.wifiState:
                        logging.log(logging.INFO, "Wifi %s connected!"%wifiName)
                        return True
                logging.log(logging.INFO, "Wifi [%s] did not connected!"%wifiName)
            except Exception as e:
                logging.log(logging.ERROR, e)
            time.sleep(0.5)
        return False

    def find_wifi(self, str):
        logging.log(logging.INFO, "Finding wifi %s  ..."%str)
        p = subprocess.Popen("netsh wlan disconnect",shell=True)# win10 system cannot auto refresh wifi list, so disconnect it first
        p.wait()
        #p = os.popen("netsh wlan show networks") #netsh wlan show networks mode=bssid
        #content = p.read().decode("gbk", "ignore")

        p = subprocess.Popen("netsh wlan show networks | find \"%s\""%str,shell=True,stdout=subprocess.PIPE)
        try:
            content = p.stdout.read().decode("GB2312") # byte decode to str, and GB2312 is avoid Chinese strings.
        except:
            content = p.stdout.read().decode("utf-8")
        if content != "":
            logging.log(logging.INFO, "Find [%s]"%str)
            return True
        else:
            return False

if __name__=="__main__":
    wifi = windowsWifi()
    data = wifi.find_wifi("Beoplay M3_00094760")
    print(data)
