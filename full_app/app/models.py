import datetime
try:
    from app import db
except ImportError:
    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" #os.environ["DATABASE_URL"]
    db = SQLAlchemy(app)

class IPLogger(db.Model):
    __tablename__ = 'ip_logger'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def __init__(self,ip_address):
        self.ip_address = ip_address 

    def __repr__(self):
        return '<ip_addr %r>' % self.ip_address

class PhoneNumberLogger(db.Model):
    __tablename__ = 'phone_number_logger'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def __init__(self,phone_number):
        self.phone_number = phone_number
    
    def __repr__(self):
        return '<phone_number %r>' % self.phone_number

class AddressLogger(db.Model):
    __tablename__ = 'address_logger'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float(0))
    long = db.Column(db.Float(0))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self,lat=0.0,long=0.0):
        self.lat = lat
        self.long = long
    def __repr(self):
        return '<lat_long %r>' % str(self.lat)+","+str(self.long)

class BackpageLogger(db.Model):
    __tablename__ = 'backpage_logger'
    id = db.Column(db.Integer, primary_key=True)
    text_body = db.Column(db.String(4000))
    text_headline = db.Column(db.String(4000))
    link = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    case_number = db.Column(db.String(10000))
    photos = db.Column(db.String(10000))
    language = db.Column(db.String(1000))
    polarity = db.Column(db.Float(0))
    translated_body=db.Column(db.String(10000))
    translated_title=db.Column(db.String(10000))
    subjectivity=db.Column(db.Float(0))
    posted_at = db.Column(db.DateTime) #ToDo: Fix this - currently scraper doesn't scrape posted at.
    is_trafficking = db.Column(db.Boolean(False))
    phone_number = db.Column(db.String(400))

    def __init__(self,text_body='',text_headline='',
                 link='',photos='',language='',polarity=0.0,translated_body='',
                 translated_title='',subjectivity=0.0,posted_at=datetime.datetime.now(),
                 is_trafficking=False,phone_number='',case_number=''):
        self.text_body = text_body
        self.text_headline = text_headline
        self.link = link
        self.photos = photos
        self.language = language
        self.polarity = polarity
        self.translated_body = translated_body
        self.translated_title = translated_title
        self.subjectivity = subjectivity
        self.posted_at = posted_at
        self.is_trafficking = is_trafficking
        self.phone_number = phone_number
        self.case_number = case_number
 
    def __repr__(self):
        return '<ad %r>' % self.text_headline 

class KeyWords(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(5000))
    
    def __init__(self,keyword):
        self.keyword = keyword

    def __repr__(self):
        return '<keyword %r>' % self.keyword
