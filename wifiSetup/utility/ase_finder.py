#coding=utf-8
#
# Editor: Bruce Zhu
#
import select
import socket
import logging
import sys
try:
	import utility.pybonjour as pybonjour
except Exception as e:
	print("ERROR: Please install pybonjour module")
	logging.log(logging.INFO, "ERROR: Please install pybonjour module")
	sys.exit(-1)

class deviceScan:
    def __init__(self):
        self.QUERY_TYPE = "_beo_settings._tcp"
        self.DNSSD_QUERY_TIMEOUT  = 5

        self.queried  = []
        self.resolved = []
        self.asetkNameReq = ""
        self.devName = ""
        self.friendlyName = ""
        self.ipaddr = ""
        self.times_scan = 0
        #self.temp = [0]*36
        self.info = {}
    #==============================================
    # Discovery Function
    #==============================================
    def resolve_callback(self,sdRef, flags, interfaceIndex, errorCode, fullname,
    					 hosttarget, port, txtRecord):

    	if errorCode != pybonjour.kDNSServiceErr_NoError:
    		return
    	#print(port)
    	#print(txtRecord)
    	record= txtRecord.split("=")
    	if record[0].find("DEVICE_TYPE")>=0:
    		self.devName= record[1]
    	else:
    		self.devName= "Unknown"

    	self.friendlyName= fullname.split(".")[0].replace("\\032"," ")

    	self.ipaddr = socket.gethostbyname(hosttarget)

    	if self.asetkNameReq=="" or self.friendlyName.find(self.asetkNameReq)>=0:
            #print('\n[%s / %s / %s ]'%(self.devName, self.friendlyName, self.ipaddr))
            '''
            for i in self.temp:# Avoid duplicate
            	if self.ipaddr == i:
            		return
            '''
            self.times_scan += 1
            self.info["ipaddr_"+str(self.times_scan)] = self.ipaddr
            self.info["devName_"+str(self.times_scan)] = self.devName
            self.info["friendlyName_"+str(self.times_scan)] = self.friendlyName

            #print(self.times_scan)

    def browse_callback(self,sdRef, flags, interfaceIndex, errorCode, serviceName,
    					regtype, replyDomain):

        if errorCode != pybonjour.kDNSServiceErr_NoError:
        	return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
        	#print('Service removed')
        	return
        #print '\nService added; resolving'
        resolve_sdRef = pybonjour.DNSServiceResolve(0,
        											interfaceIndex,
        											serviceName,
        											regtype,
        											replyDomain,
        											self.resolve_callback)

        try:
        	while not self.resolved:
        		ready = select.select([resolve_sdRef], [], [], self.DNSSD_QUERY_TIMEOUT)
        		if resolve_sdRef not in ready[0]:
        			#print 'Resolve timed out'
        			break
        		pybonjour.DNSServiceProcessResult(resolve_sdRef)
        	else:
        		self.resolved.pop()
        except Exception as e:
        	pass
        	#print e
        	#sys.exit(-1)
        finally:
        	resolve_sdRef.close()

    def scan(self):
        browse_sdRef = pybonjour.DNSServiceBrowse(regtype  = self.QUERY_TYPE,
        										  callBack = self.browse_callback)

        try:
            #time.sleep(0.5) #Wait bonjour response
            ready = select.select([browse_sdRef], [], [])
            if browse_sdRef in ready[0]:
            	pybonjour.DNSServiceProcessResult(browse_sdRef)
        except Exception as e:
            logging.log(logging.INFO, "Please install Bonjour Server!")
        	#print e
        	#sys.exit(-1)
        finally:
        	browse_sdRef.close()


if __name__ == '__main__':
    deviceScan = deviceScan()
    deviceScan.scan()
    print(deviceScan.info)

