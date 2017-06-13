# -*- coding: utf-8 -*-

import configparser
import string

class getconfig(object):
    @classmethod  
    def confToDict(cls,configFile, d=""):
        cp = configparser.ConfigParser()
        cp.optionxform = str  # Keep the capital letter format
        cp.read(configFile)
        if not d:
            d=dict()
            for s in cp.sections():
                d[s] = dict()
                for i in cp.items(s):
                    d[s][i[0]]=i[1]
        return d

    @classmethod             
    def getTestConfig(cls,default):
        #print "getTestconfig  %s" % default
        d=dict()
        #d,section = confToDict(default, d)
        d=cls.confToDict(default, d)
        return d
    
    @classmethod  
    def getparameters(cls,filename):
        
        data = cls.getTestConfig(filename) 
        return data 


if __name__=='__main__':
    data = getconfig.getparameters('../config.ini')  
    print(data)
