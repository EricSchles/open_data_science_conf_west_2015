import lxml.html
import requests
from unidecode import unidecode
import time
import random
import datetime
import json
import os
import pickle
from models import *
from text_classify import algorithms
from textblob import TextBlob
from tools import * #ParsePhoneNumber, ParseAddress
try:
    from app import db
except ImportError:
    from app import app
    from flask.ext.sqlalchemy import SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" #os.environ["DATABASE_URL"]
    db = SQLAlchemy(app)


phone_parser = ParsePhoneNumber()
addr_parser = ParseAddress()

#a web scraper, for local computation
#At present, this seems to work fine
class Scraper:
    def __init__(self,place=None,debug=False):
        if type(place) == type(str()):
            place = place.replace(",","").replace(".","").replace("-","")
        self.debug=debug
        if place:
            self.place = place
            self.base_urls = self.map_place(place)
        else:
            #consider getting rid of this
            self.base_urls = [
                "http://newyork.backpage.com/FemaleEscorts/",
                "http://newyork.backpage.com/BodyRubs/",
                "http://newyork.backpage.com/Strippers/",
                "http://newyork.backpage.com/Domination/",
                "http://newyork.backpage.com/TranssexualEscorts/",
                "http://newyork.backpage.com/MaleEscorts/",
                "http://newyork.backpage.com/Datelines/",
                "http://newyork.backpage.com/AdultJobs/"
            ]
            self.place = place

    def update_place(self,place):
        if type(place) == type(str()):
            place = place.replace(",","").replace(".","").replace("-","")
        self.base_urls = self.map_place(place)

    def update_investigation(self,urls):
        self.scrape(links=urls,scraping_ads=True)

    #ToDo, iterate to pages further back in time.
    #fine for now
    def generate_pages(self,url):
        urls = []
        endings = [
            "FemaleEscorts/",
            "BodyRubs/",
            "Strippers/",
            "Domination/",
            "TranssexualEscorts/",
            "MaleEscorts/",
            "Datelines/",
            "AdultJobs/"
        ]
        init_urls = []
        for ending in endings:
            init_urls.append(url+ending)
        for i in xrange(1,6):
            for url in init_urls:
                urls.append(url+"?page="+str(i))
        urls = init_urls + urls
        return urls
    
    #fine
    def map_place(self,place):
        #I believe this is lazy evaluation, otherwise, I'm kinda dumb...
        place = place.lower()
        places = {
            "alabama":self.generate_pages("http://alabama.backpage.com/"),
            "manhattan":self.generate_pages("http://manhattan.backpage.com/"),
            "new york":self.generate_pages("http://newyork.backpage.com/"),
            "new york city":self.generate_pages("http://manhattan.backpage.com/")+self.generate_pages("http://statenisland.backpage.com/")+self.generate_pages("http://queens.backpage.com/")+self.generate_pages("http://brooklyn.backpage.com/")+self.generate_pages("http://bronx.backpage.com/"),
            "buffalo":self.generate_pages("http://buffalo.backpage.com/"),
            "albany new york":self.generate_pages("http://albany.backpage.com/"),
            "binghamton":self.generate_pages("http://binghamton.backpage.com/"),
            "catskills":self.generate_pages("http://catskills.backpage.com/"),
            "chautauqua":self.generate_pages("http://chautauqua.backpage.com/"),
            "elmira":self.generate_pages("http://elmira.backpage.com/"),
            "fairfield":self.generate_pages("http://fairfield.backpage.com/"),
            "fingerlakes":self.generate_pages("http://fingerlakes.backpage.com/"),
            "glens falls":self.generate_pages("http://glensfalls.backpage.com/"),
            "hudson valley":self.generate_pages("http://hudsonvalley.backpage.com/"),
            "ithaca":self.generate_pages("http://ithaca.backpage.com/"),
            "long island":self.generate_pages("http://longisland.backpage.com/"),
            "oneonta":self.generate_pages("http://oneonta.backpage.com/"),
            "plattsburgh":self.generate_pages("http://plattsburgh.backpage.com/"),
            "potsdam":self.generate_pages("http://plattsburgh.backpage.com/"),
            "rochester":self.generate_pages("http://plattsburgh.backpage.com/"),
            "syracuse":self.generate_pages("http://plattsburgh.backpage.com/"),
            "twintiers":self.generate_pages("http://twintiers.backpage.com/"),
            "utica":self.generate_pages("http://utica.backpage.com/"),
            "watertown":self.generate_pages("http://watertown.backpage.com/"),
            "westchester":self.generate_pages("http://watertown.backpage.com/")
        }
        return places[place]
        
        
    def parse_lat_long(self,html):
        if self.debug:
            print "Processing address data and transforming it into latitude and longitude coordinates.."
        possible_locations = html.xpath('//div[@style="padding-left:2em;"]')
        potential_lat_longs = []
        for loc in possible_locations:
            if "Location" in loc.text_content():
                for possible in loc.text_content().split("Location:")[1].split(","):
                    if self.place:
                        potential_lat_longs.append(addr_parser.parse(possible,place=self.place))
                    else:
                        potential_lat_longs.append(addr_parser.parse(possible))
        lat_longs = [elem for elem in potential_lat_longs if elem != None]
        if self.debug: print "sending lat/long data to the database for further visualization and inquiry.."
        for lat_long in lat_longs:
            addr_log = AddressLogger(lat=lat_long.latitude,long=lat_long.longitude)
            db.session.add(addr_log)
            db.session.commit()
        return lat_longs

    def parse_basic_info(self,response,html,values):
        if self.debug:
            print "Processing advertisement contents and pulling out title, text body, timestamp information, and image links.."
        values = {}
        values["title"] = html.xpath("//div[@id='postingTitle']/a/h1")[0].text_content()
        values["link"] = unidecode(response.url)
        # Stub - add this with textRank - values["new_keywords"] = []
        try:
            values["images"] = html.xpath("//img/@src")
        except IndexError:
            values["images"] = "weird index error"
        pre_decode_text = html.xpath("//div[@class='postingBody']")[0].text_content().replace("\n","").replace("\r","")  
        values["text_body"] = pre_decode_text 
        #this appears to be broken
        try:
            values["posted_at"] = html.xpath("//div[class='adInfo']")[0].text_content().replace("\n"," ").replace("\r","")
        except IndexError:
            values["posted_at"] = datetime.datetime.min #not given - this is just a quick fix because datetime objects are required
        values["scraped_at"] = str(datetime.datetime.now())
        return values

    def parse_text_meta_data(self,html,values):
        if self.debug: print "Processing textual information - language, polarity, subjectivity.."
        body_blob = TextBlob(values["text_body"])
        title_blob = TextBlob(values["title"])
        values["language"] = body_blob.detect_language() #requires the internet - makes use of google translate api
        values["polarity"] = body_blob.polarity
        values["subjectivity"] = body_blob.sentiment[1]
        if values["language"] != "en" and not translator:
            values["translated_body"] = body_blob.translate(from_lang="es")
            values["translated_title"] = title_blob.translate(from_lang="es")
        else:
            values["translated_body"] = "none"
            values["translated_title"] = "none"
        return values
    
    def make_requests(self,links,scraping_ads):
        responses = []
        if scraping_ads:
            print 
            for link in links:
                r = requests.get(link)
                responses.append(r)
        else:
            for link in links:
                r = requests.get(link)
                text = unidecode(r.text)
                html = lxml.html.fromstring(text)
                links = html.xpath("//div[contains(@class,'cat')]/a/@href")
                for link in links:
                    try:
                        responses.append(requests.get(link))
                        print link
                    except requests.exceptions.ConnectionError:
                        print "hitting connection error"
                        continue
        if self.debug:
            print "Finished making requests.."
        return responses

    def scrape(self,links=[],scraping_ads=False):
        data = []
        if self.debug:
            print "Making requests to backpage.com.."
        responses = self.make_requests(links,scraping_ads)
        if self.debug:
            print "Processing responses.."
        for response in responses:
            values= {}
            text = response.text
            html = lxml.html.fromstring(text)
            #getting address information from html page            
            lat_longs = self.parse_lat_long(html)
            values.update(self.parse_basic_info(response,html,values))
            values.update(self.parse_text_meta_data(html,values))
            text_body = values["text_body"]
            title = values["title"]
            if self.debug: print "parsing out phone numbers..."
            values["phone_numbers"] = phone_parser.phone_number_parse(values)
            #is_trafficking is currently missing because it is being handled in investigate for some reason
            #this needs to be added to this method/made more readible
            if self.debug: print "storing phone numbers.."
            for p_number in values['phone_numbers']:
                ad_phone_number = PhoneNumberLogger(p_number)
                db.session.add(ad_phone_number)
                db.session.commit()
            data.append(values)
        return data
    
    #need to add TfIdf
    #need to merge investigate and scrape methods or split this up further in someway, but currently this is bad and confusing
    def investigate(self,case_number):
        data = self.scrape(links=self.base_urls,scraping_ads=True)
        training_data = [(elem, "trafficking") for elem in BackpageLogger.query.filter_by(is_trafficking=True).all()] 
        training_data += [(elem, "not trafficking") for elem in BackpageLogger.query.filter_by(is_trafficking=False).all()]
        trafficking_numbers = [elem.phone_number for elem in BackpageLogger.query.filter_by(is_trafficking=True).all()]
        cls = []
        cls.append(algorithms.svm(training_data))
        cls.append(algorithms.decision_tree(training_data))
        using_naive_bayes = len(training_data) > 50 #totally a hack, consider getting advice / changing this??
        if using_naive_bayes:
            nb = algorithms.naive_bayes(training_data)
        for datum in data:
            if datum["phone_number"] in trafficking_numbers:
                self.save([datum],case_number)
            if not using_naive_bayes:  
                for cl in cls:
                    if cl.classify(algorithms.preprocess(datum["text_body"])) == "trafficking":
                        self.save([datum],case_number)
            else:
                if nb.classify(datum["text_body"]) == 'trafficking':
                    self.save([datum],case_number)
        time.sleep(700) # wait ~ 12 minutes (consider changing this)
        self.investigate(case_number) #this is an infinite loop, which I am okay with.

    def save(self,data,case_number=''):
        if self.debug: "storing information in a database.."
        for values in data:
            bp_ad = BackpageLogger(
                case_number=case_number,
                text_body=values["text_body"],
                text_headline=values["title"],
                link=values['link'],
                photos=json.dumps(values['images']),
                language=values['language'],
                polarity=values['polarity'],
                translated_body=values['translated_body'],
                translated_title=values['translated_title'],
                subjectivity=values['subjectivity'],
                posted_at=values['posted_at'],
                phone_number=json.dumps(values['phone_numbers'])#this is gross and will be fixed at some point
            )
            db.session.add(bp_ad)
            db.session.commit()
        return data

    #should this method remain?
    def initial_scrape(self,links):
        if self.debug:
            print "Starting initial scrape.."
        scrape_data = self.scrape(links=links)
        saved_data = self.save(scrape_data)
        return saved_data == scrape_data

if __name__ == '__main__':
    scraper = Scraper(place="New York City",debug=True)
    print scraper.initial_scrape(links=["http://newyork.backpage.com/FemaleEscorts/"])
    
    
    
