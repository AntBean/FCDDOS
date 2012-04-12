import urllib2,urllib,json
import django.utils.simplejson as simplejson
import os,sys
from uasparser import UASparser 
USER_AGENT_BROWSER_TYPES = ['Browser','Mobile Browser','Wap Browser']
USER_AGENT_REST_TYPES = ['Useragent Anonymizer','Robot','unknown','Other',
                      'Offline Browser','Email client','Library',
                      'Validator','Feed Reader','Multimedia Player']
API_URL = "http://www.useragentstring.com/?"
class UserAgentType:
    def __init__(self):
        self.uas_parser = UASparser('/home/natty/FCDDOS/UASparserCache') 
    def isBrowser(self,userAgent):
        if userAgent == '-':
            return True
        #print agentType
        result = self.uas_parser.parse(str(userAgent))
        agentType = result["typ"]
        #print agentType,":::",userAgent,"\n"
        if agentType in USER_AGENT_BROWSER_TYPES:
            return True
        else:
            return False
"""
class UserAgentType:
    def isBrowser(self,userAgentString):
        myParameters = { 'uas' : userAgentString, 'getJSON':'all'}
        URLEncoded = API_URL+urllib.urlencode(myParameters)
        response = None
        try:
            response = urllib2.urlopen(URLEncoded).next()
            print response
            print "\n"
            agentType = simplejson.loads(response)['agent_type']
            #print agentType
            if agentType in USER_AGENT_REST_TYPES:
                return False
            else:
                return True
        except:
            print "UserAgentType API Error: ",userAgentString
            raise
"""
"""
if __name__ == "__main__":
    ua = UserAgent()
    print ua.isBrowser("BinGet/1.00.A (http://www.bin-co.com/php/scripts/load/)")
"""


