#Building Systems to Fight Slavery

__By__

__Eric__ __Schles__

##About Me

* Worked for Manhattan District Attorney's Human Trafficking Response Unit as Data Science Researcher
* Currently work for the United States Digital Service as a Data Scientist working on Veterans Affairs
* Still working as a researcher in Human Trafficking in my spare time 

##About my org

Hacking Against Slavery

[http://hackingagainstslavery.github.io/](http://hackingagainstslavery.github.io/)

##Problem Definition

Human Trafficking <=> Slavery

Today we'll be focusing on Sex Trafficking.

Sex trafficking happens a few ways:

1. A person is kidnapped and forced into sex slavery 
2. A person is mentally/physcially violated to such an extreme place, they submit to the will of the trafficker

A possible solution to 1 - Match missing persons pictures with pictures from sex marketplace websites such as backpage

Solving 2 is harder.  To understand how to stop problem 2, we must understand the approach a trafficker uses to break his victims:

1. The trafficker cuts off the victims social connections and emotional support center, refocusing this system souly on them ~ 3-7 months

2. Once the victim has no other or a very small social/emotional support center, the trafficker begins to physically beat the victim or rape them ~ once per month

3. Then the victim is moved into a small living quarters with other victims and made to compete for the traffickers attention and affection by making the trafficker money.  

4. The trafficker reinforces a pattern of control with a combination of violence, rape, and occasionally consential sex. ~ beats or rapes them once per month.  Trafficker says the victim will be beat or raped nearly constantly.  At this point the victim is trapped. 

Presently law enforcement attacks the problem by intervening when the victim is in stage 4.  Sometimes we are able to intervene sooner, but usually we are not.  

What we need is a system that understands the __contributing__ __factors__ that led to that person becoming a victim in the first place and understand the "basket" of policy choices they can employ to limit the amount of trafficking and to hit reasonable goals to reduce human trafficking supply.

The system I am building addresses this question - how do we build analyses that will aid the in combatting human trafficking, not just when a person has become a victim, but how do we stop them from becoming a victim?

##The system

In the current state the system performs automated investigations into human trafficking.  

So how does law enforcement decide what might be human trafficking?

Primarily it looks at cases involving violence and prostitution.  

[Demo of Web Scraper goes here]()

Web Scraping an ad -> Running an investigation

##Web Scraping

Web scraping is very simple - you grab content from a website and then process it locally, based on tags, selectors, and plain text.

###Grabbing content from the web

```
import requests

r = requests.get("https://hackingagainstslavery.github.io")
print r.text
```

###Processing html

If we wanted to pull all the links from a page we only need to get all the href links on the html page.  Using xpath we can do this in an extremely compact way.  I'm choosing to use the lxml library for this because it is very fast.

```
import requests
import lxml.html

r = requests.get("https://hackingagainstslavery.github.io")
html = lxml.html.fromstring(r.text)
print html.xpath("//a/@href")
```

Using these two simple pieces of code we can build a webscraper that will grab all the content that is publicly accessible from a domain, given just the base url.  

A very simple generalized webscraper:

```
import requests #sudo pip install requests 
import lxml.html #sudo pip install lxml.html
from unidecode import unidecode #sudo pip install unidecode

def links_grab(url):
    r = requests.get(url)
    html = lxml.html.fromstring(unidecode(r.text))
    return html.xpath("//a/@href") + [url] #ensures the url is stored in the final list

def crawl(base_url,start_depth=6):
    return crawler([base_url],base_url,start_depth)

def crawler(urls, base_url, depth):
    urls = list(set(urls))
    domain_name = base_url.split("//")[1].split("/")[0]
    url_list = []
    for url in urls:
        if domain_name in url:
            url_list += links_grab(url)
    print url_list
    url_list = list(set(url_list)) #dedup list
    url_list = [uri for uri in url_list if uri.startswith("http")]
    if depth > 1:
        url_list += crawler(url_list, base_url, depth-1)
    urls += url_list
    urls = list(set(urls))
    num_urls = len(urls)
    return url_list

if __name__ == '__main__':
    print crawl("https://hackingagainstslavery.github.io",6)
```

##GIS 

The Address parse in action:

```
>>> from tools import *
>>> parse_addr = ParseAddress()
>>> #Get Lat/Long from an exact address
>>> parse_addr.parse("9 Poplar Court, Great Neck, NY, 11024")
Location((40.8088205083, -73.7369217892, 0.0))
>>> #Get Lat/Long from an exact address in free text
>>> parse_addr.parse("Hello there my name is Eric and I live at 9 Poplar Court, Great Neck, NY, 11024")
Location((40.8088205083, -73.7369217892, 0.0))
>>> #Get a Lat/Long from Cross Streets
>>> parse_addr.parse("Hello there my name is Eric and I live at Middle Neck and Steam Boat, Great Neck, NY, 11024")
Location((40.8006567, -73.7284647, 0.0))
```

How this code works:

###Our imports
```
import usaddress
from streetaddress import StreetAddressFormatter
from nltk.tag.stanford import StanfordNERTagger as Tagger
from geopy.geocoders import GoogleV3,Nominatim
import nltk
import geopy
```

###Setting things up
```
addr_formatter = StreetAddressFormatter()
```

###PreProcessing Our data

usaddress is great!  It does a whole bunch of semantic analysis for free!  All we need to do is put in a string with an address and a bunch of other stuff.  As long as the address is well formatted (where well formatted is a relative term) usaddress will pick up what we need:

```
>>> import usaddress
>>> usaddress.parse("Hello there my name is Eric and I live at 9 Poplar Court, Great Neck, NY, 11024")
[(u'Hello', 'Recipient'), (u'there', 'Recipient'), (u'my', 'Recipient'), (u'name', 'Recipient'), (u'is', 'Recipient'), (u'Eric', 'Recipient'), (u'and', 'Recipient'), (u'I', 'Recipient'), (u'live', 'Recipient'), (u'at', 'Recipient'), (u'9', 'AddressNumber'), (u'Poplar', 'StreetName'), (u'Court,', 'StreetNamePostType'), (u'Great', 'PlaceName'), (u'Neck,', 'PlaceName'), (u'NY,', 'StateName'), (u'11024', 'ZipCode')]
```

Using this we should notice that almost everything is either a Recipient or a semantic label we care about.  Using this we can remove all the recipient and process the address information we care about, from the free text.

What if things are far less structured?  Another approach is to make use of nltk's named entity recognition tagger - from stanford.  

We can do the following to pull out an nouns that are locations using this tagger:

```
tagger = Tagger('/opt/stanford-ner-2014-08-27/classifiers/english.all.3class.distsim.crf.ser.gz','/opt/stanford-ner-2014-08-27/stanford-ner.jar')
possible_streets = []
for word,tag in tagger.tag(text.split()):
    if tag == 'LOCATION':
        possible_streets.append(word)
```

Assumming we have no named location information and usaddress fails we can still parse out nouns and let someone look for address information latter:

```
import nltk
parts = nltk.pos_tag(nltk.word_tokenize(text))
for part in parts:
    if any([part[1]==noun for noun in nouns]):
        possible_streets.append(part[0])
```

For this wee use a simple part of speech tagger to pull out all the nouns.

Putting this all together we get a very nice preprocessing engine that is great for pulling information out of free text:

```
def preprocess(self,text):
    nouns = ['NN','NNP','NNPS','NNS']
    if any([elem.isdigit() for elem in text.split(" ")]):
        addr = usaddress.parse(text)
        addr = [elem for elem in addr if elem[1] != 'Recipient']
        addr_dict = {}
        for value,key in addr:
            if key in addr_dict.keys():
                addr_dict[key] += " "+value
            else:
                addr_dict[key] = value
        return addr_dict,"complete"
    else:
        possible_streets = []
        for word,tag in tagger.tag(text.split()):
            if tag == 'LOCATION':
                possible_streets.append(word)
        parts = nltk.pos_tag(nltk.word_tokenize(text))
        for part in parts:
            if any([part[1]==noun for noun in nouns]):
                possible_streets.append(part[0])
        return possible_streets,"cross streets"
```

From here we simply need to send our addresses to a standard geo encoder - something that takes addresses and turns them into lat/long.

There are a lot of great choices and many of them are wrapped by geopy.  I personally love google's engine because it can handle cross streets.  Nominatim is the cheapest one - you don't even need an api key, but you will get rated limited by IP address.

Using either api is extremely easy:

```
g_coder = GoogleV3(google_key)
lat_long = g_coder.geocode(addr)

n_coder = Nominatim()
lat_long = n_coder.geocode(addr)
```

In order to use these great tools I've built a tiny ParseAddress Object.  Feel free to use it for your own projects.  But please note you should get a google api and save it to a file `google_api_key.pickle` - make sure you `dump` it with `pickle.dump`!

```
class ParseAddress:
    #If we are pulling this information from an excel document then we'll likely have the address information in an acceptable form
    #Otherwise we'll need to run the text through usaddress or streetaddress
    def __init__(self,from_api=False,from_excel=False):
        self.from_api = from_api
        self.from_excel = from_excel

    def pre_formatter(self,addr,dict_addr):
        if "StreetNamePostType" in dict_addr.keys():
            addr = addr.replace("St","Street")
            addr = addr.replace("St.","Street")
            addr = addr.replace("st","Street")
            addr = addr.replace("st.","street")
        return addr
        
    #The parse will get you a lat/long representation of the address, which exists somewhere in the passed in text.
    #It expects free form text or a complete address
    def parse(self,text,place="NYC"):
        dict_addr,addr_type = self.preprocess(text)
        google_key = pickle.load(open("google_api_key.pickle","r"))
        g_coder = GoogleV3(google_key)
        if addr_type == 'complete':
            combined_addr = []
            keys = ["AddressNumber","StreetName","StreetNamePostType","PlaceName","StateName","ZipCode"]
            for key in keys:
                try:
                    combined_addr += [dict_addr[key]]
                except KeyError:
                    continue
                addr = " ".join(combined_addr) 
            n_coder = Nominatim()
            addr = self.pre_formatter(addr,dict_addr)
            lat_long = n_coder.geocode(addr)
            if lat_long: #means the request succeeded
                return lat_long
            else:
                lat_long = g_coder.geocode(addr)
                return lat_long
            #If None, means no address was recovered.
        if addr_type == 'cross streets':
            #handle case where dict_addr is more than 2 nouns long
	    cross_addr = " and ".join(dict_addr) + place 
            try:
                lat_long = g_coder.geocode(cross_addr)
                return lat_long
            except geopy.geocoders.googlev3.GeocoderQueryError:
                return None
        
    def preprocess(self,text):
        nouns = ['NN','NNP','NNPS','NNS']
        if any([elem.isdigit() for elem in text.split(" ")]):
            addr = usaddress.parse(text)
            addr = [elem for elem in addr if elem[1] != 'Recipient']
            addr_dict = {}
            for value,key in addr:
                if key in addr_dict.keys():
                    addr_dict[key] += " "+value
                else:
                    addr_dict[key] = value
            return addr_dict,"complete"
        else:
            possible_streets = []
            for word,tag in tagger.tag(text.split()):
                if tag == 'LOCATION':
                    possible_streets.append(word)
            parts = nltk.pos_tag(nltk.word_tokenize(text))
            for part in parts:
                if any([part[1]==noun for noun in nouns]):
                    possible_streets.append(part[0])
            return possible_streets,"cross streets"
	 
        #addresses: http://stackoverflow.com/questions/11160192/how-to-parse-freeform-street-postal-address-out-of-text-and-into-components
        #To do: build general list from http://www.nyc.gov/html/dcp/html/bytes/dwnlion.shtml
        #And from https://gis.nyc.gov/gisdata/inventories/details.cfm?DSID=932
        
        #Here I need to add Part of Speech tagging and pull out all the nouns as possible street names.
        #Then I need to come up with a list of street names in NYC and run each noun through the list
        #From there I'll have all the street names
```

Now that we have all our addresses processed and saved we can visualize them easily:

First we create our map object:

`var map = L.map('map')`

Then we get a tileLayer for our pretty maps:

```
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6IjZjNmRjNzk3ZmE2MTcwOTEwMGY0MzU3YjUzOWFmNWZhIn0.Y8bhBaUMqFiPrDRW9hieoQ', {
maxZoom: 18,
attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
	'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
	'Imagery © <a href="http://mapbox.com">Mapbox</a>',
id: 'mapbox.streets'
}).addTo(map);
```

And then we add our markers:

```
for(var i = 0; i < json.length; i++) {
    var obj = json[i];
    L.marker([obj.lat,obj.long]).addTo(map);
    console.log(obj.id);
}
```

Putting this all together: (And stubbing out some data)

```
<html>
<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.css" />
<div id="map" style="width: 600px; height: 400px"></div>
<script>
var map = L.map('map').setView([40.7127, -74.0059], 13);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6IjZjNmRjNzk3ZmE2MTcwOTEwMGY0MzU3YjUzOWFmNWZhIn0.Y8bhBaUMqFiPrDRW9hieoQ', {
maxZoom: 18,
attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
	'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
	'Imagery © <a href="http://mapbox.com">Mapbox</a>',
id: 'mapbox.streets'
}).addTo(map);

L.marker([40.7127,-74.0059]).addTo(map).bindPopup("Scraped at 12:57am on 7/27/2014");
L.marker([40.7135,-74.0017]).addTo(map).bindPopup("Scraped at 2:24am on 7/28/2014");
L.marker([40.7107,-74.0011]).addTo(map).bindPopup("Scraped at 3pm on 7/28/2014");
L.marker([40.7155,-74.0078]).addTo(map).bindPopup("Scraped at 4pm on 7/26/2014");
</script>
</html>
```

[Map demo goes here]()


My goal for this system is to get it into every police department in the country, so they can automatically run human trafficking investigations and gather evidence as fast as possible.  And so that they can come up with leads for future cases, by comparing against current cases.

My second goal is to get this system to send me anonymous data, detailing how many human trafficking investigations are run and sending that number to a central server.  With the frequency of cases being processed, we can get a sense for the number of human trafficking cases in an area.  

This data set, combined with:
* Education Data:
	* years of schooling in a given area
	* grade point average from grade to grade in a given area
	* percentage of people with GED/high school diploma in a given area
	* percentage of people with college degree in a given area
	* percentage of people with a masters or other graduate degree in a given area
	* more goes here
* Homelessness Data:
	* number of homeless families
	* number of homeless single men
	* number of homeless single women
	* number of homeless male children
	* number of homeless female children
	* number of homeless families with one parent
	* total number of homeless people
* Legal Data:
	* Number of Human Trafficking laws currently in affect in an area
	* Number of Human Trafficking bills that are being considered for becoming law
* Housing Data:
	* Number of Housing Developments in an area
	* Number of Apt. Buildings in an area
	* Number of building violations in total in an area
* Social Welfare Data
	* Unclear what's out there
* Crime Data:
	* Unclear how to get this everywhere

In total will give us a sense of the possible contributing factors to human trafficking.  From there we will be able to do analysis of the most important contributing factors, by region, using something called impulse response.

To understand impulse response we must first review time series analysis, in particular Vector Autoregression Models (VAR for short).

If you don't know or don't remember time series analysis, please check out [this great introduction on MA and AR models](http://www.analyticsvidhya.com/blog/2015/03/introduction-auto-regression-moving-average-time-series/).

[Timeseries Demo]()

Check out: [statsmodels docs](http://statsmodels.sourceforge.net/devel/vector_ar.html) for more info

If you want to help you can:

[http://hackingagainstslavery.github.io](http://hackingagainstslavery.github.io)
