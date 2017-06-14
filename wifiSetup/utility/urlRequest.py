#coding=utf-8
#
# Author: Bruce Zhu
#

import requests
import logging

class urlRequest():
    def __init__(self):
        self.headers = {'content-type': 'application/json',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}

    def post(self, url, data=''):
        try:
            logging.log(logging.INFO, 'Requesting post to %s'%url)
            r = requests.post(url, data=data, headers=self.headers)
            r.raise_for_status() #status_code = r.status_code
        except requests.RequestException as e:
            logging.log(logging.ERROR, e)
        else:
            logging.log(logging.INFO, 'Request post ---------successfully!')
            return True
        return False

    def get(self, url):
        html = ''
        try:
            logging.log(logging.INFO, 'Request get to %s'%url)
            r = requests.get(url, headers=self.headers, timeout = 8)
            r.raise_for_status() #status_code = r.status_code
        except requests.RequestException as e:
            logging.log(logging.ERROR, e)
        else:
            html = r.text
        return html

if __name__=="__main__":
    urlRequest = urlRequest()
    url = "http://www.baidu.com"
    #data = urlRequest.get(url)
    url = "http://{ip}/api/setData?path=beo_LocalUI%3AfactoryResetRequest&roles=activate&value=%7B%22type%22%3A%22bool_%22%2C%22bool_%22%3Atrue%7D&"
    r = urlRequest.post("http://www.baidu.com")
    print(r)
    #print(data)