from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from BeautifulSoup import BeautifulStoneSoup
import urllib2

class Agencies(webapp.RequestHandler):
    def get(self):
        lines = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList')
        soup = BeautifulStoneSoup(lines, selfClosingTags=['agency'])
        agencies = soup.findAll('agency')
        html = '<?xml version="1.0" encoding="utf-8" ?><body>'
        for agency in agencies:
            html += '<choice tag="' + agency['tag'] + '" title="' + agency['title'].replace("&", "and") + '">'
        html += '</body>'
        self.response.out.write(html)
        
class Lines(webapp.RequestHandler):
    def get(self, agency):
        lines = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=' + agency)
        soup = BeautifulStoneSoup(lines, selfClosingTags=['route'])
        lines = soup.findAll('route')
        html = '<?xml version="1.0" encoding="utf-8" ?><body>'
        for line in lines:
            html += '<choice tag="' + line['tag'] + '" title="' + line['title'].replace("&", "and") + '">'
        html += '</body>'
        self.response.out.write(html)
        
class Directions(webapp.RequestHandler):
    def get(self, agency, line):
        '''Return the directions for a line for an agency.'''
        directions = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
        soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
        directions = soup.findAll('direction')
        html = '<?xml version="1.0" encoding="utf-8" ?><body>'
        for direction in directions:
            html += '<choice tag="' + direction['tag'] + '" title="' + direction['title'].replace("&", "and") + '">'
        html += '</body>'
        self.response.out.write(html)

class Stops(webapp.RequestHandler):
    def get(self, agency, line, direction):
        directions = get_xml('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=' + agency + '&r=' + line)
        soup = BeautifulStoneSoup(directions, selfClosingTags=['stop'])
        stop_ids = soup.find('direction', tag=direction).findAll('stop')
        html = '<?xml version="1.0" encoding="utf-8" ?><body>'
        for stop_id in stop_ids:
            stop = soup.find('stop', tag=stop_id['tag'])
            html += '<choice tag="' + stop['tag'] + '" title="' + stop['title'].replace("&", "and") + '">'
        html += '</body>'
        self.response.out.write(html)

def get_xml(url):
    '''Go to url and returns the xml data.'''
    file = urllib2.urlopen(url)
    xml = file.read()
    file.close()
    return xml

def main():
    application = webapp.WSGIApplication([
            # main
           ('/agencies/', Agencies),
           ('/(.+)/lines/', Lines),
           ('/(.+)/(.+)/directions/', Directions),
           ('/(.+)/(.+)/(.+)/stops/', Stops),
         ],debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
