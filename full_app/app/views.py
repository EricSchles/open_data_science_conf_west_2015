from flask import render_template,redirect,request,url_for,g,flash
from app import app
import pickle
from crawler import Scraper
from multiprocessing import Process

#This basic server will send data to the leaflet frontend
from random import randint
import json 
from flaskext import uploads
import pandas as pd 
import os
from werkzeug import secure_filename
from glob import glob
from tools import Queue


scraper = Scraper()
queue = Queue()


@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

#Data Visualization Routes
#Map routes
UPLOAD_FOLDER = os.getcwd() + "/static/uploads"
ALLOWED_EXTENSIONS = set(['csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/gis_map/<filename>",methods=["GET","POST"])
@app.route("/gis_map",methods=["GET","POST"])
def gis_map(filename=None):
    datasets = [File.split("/")[-1] for File in glob("static/uploads/*")]
    if filename:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(full_path):
            return render_template("map.html",states=json.dumps(transform_csv(full_path)),datasets=datasets)
        return "fail"
    else:
        return render_template("map.html",states=json.dumps([{}]),datasets=datasets)

@app.route("/realtime",methods=["GET","POST"])
def realtime():
    return render_template("realtime.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/listing_of_datasets",methods=["GET","POST"])
def listing_of_datasets():
    if request.method == "POST":
        dataset = request.form.get("datasets")
    return redirect(url_for("gis_map")+dataset)

def transform_csv(filename):
    df = pd.DataFrame.from_csv(filename,index_col=False)
    json_data = df.to_json()
    data = []
    for row in df.iterrows():
        datum = {}
        tmp_dict = row[1].to_dict()
        print tmp_dict
        datum["geometry"] = {
            "type" : "Point",
            "coordinates":[tmp_dict["lat"],tmp_dict["long"]]
            }
        datum["type"] = "Feature"
        datum["properties"] = tmp_dict
        data.append(datum)
    return data

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for("index"))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

month_to_num = {
    "JAN":"01",
    "FEB":"02",
    "MAR":"03",
    "APR":"04",
    "MAY":"05",
    "JUN":"06",
    "JUL":"07",
    "AUG":"08",
    "SEP":"09",
    "SEPT":"09",
    "OCT":"10",
    "NOV":"11",
    "DEC":"12"
}

@app.route("/timeseries",methods=["GET","POST"])
def timeseries():
    df = pd.DataFrame().from_csv("homeless_data.csv")
    year = [str(elem) for elem in df["year"].tolist()]
    month = [month_to_num[elem] for elem in df["month"].tolist()]
    dates = ["01"+"-"+i+"-"+j for i,j in zip(month,year)]
    return render_template("timeseries.html",
                           adults_in_families=json.dumps(["adults_in_families"]+df["adults_in_families"].tolist()),
                           average_shelter_stays_for_families=json.dumps(["average_shelter_stays_for_families"]+df["average_shelter_stays_for_families"].tolist()),
                           children=json.dumps(["children"]+df["children"].tolist()),
                           single_adults=json.dumps(["single_adults"]+df["single_adults"].tolist()),
                           single_men=json.dumps(["single_men"]+df["single_men"].tolist()),
                           single_women=json.dumps(["single_women"]+df["single_women"].tolist()),
                           total_families=json.dumps(["total_families"]+df["total_families"].tolist()),
                           total_persons_in_families=json.dumps(["total_persons_in_families"]+df["total_persons_in_families"].tolist()),
                           total_population=json.dumps(["total_population"]+df["total_population"].tolist()),
                           dates=json.dumps(["dates"] +dates))

@app.route("/bar",methods=["GET","POST"])
def bar():
    return render_template("bar.html")

@app.route("/pie",methods=["GET","POST"])
def pie():
    return render_template("pie.html")

#Web Scraping Routes
@app.route("/webscraping",methods=["GET","POST"])
def webscraping():
    return render_template("webscraping.html")

@app.route("/run",methods=["GET","POST"])
def run():
    data = scraper.scrape(links=["http://www.backpage.com"])
    return redirect(url_for("webscraping"))

@app.route("/investigate",methods=["GET","POST"])
def investigator():
    if request.method == "POST":
        place = request.form.get("place")
        case_number = request.form.get("case_number")
        scraper.update_place(place)
        print case_number
        investigate = Process(target=scraper.investigate,args=(case_number,))
        investigate.daemon=True
        investigate.start()
        print "investigation started"
        queue.put(investigate)
    return redirect(url_for("webscraping"))

@app.route("/stop_investigation",methods=["GET","POST"])
def stop_investigation():
    #semantic bug here, fix this later (create a thread pool)
    investigate = queue.get()
    investigate.terminate()
    print "investigation terminated successfully"
    return redirect(url_for("webscraping"))

@app.route("/add",methods=["GET","POST"])
def add():
    return render_template("add.html")

@app.route("/add_data",methods=["GET","POST"])
def add_data():
    if request.method=="POST":
        investigation_type = request.form.get("investigation_type")
        url = request.form.get("url_list")
        urls = url.split(",")
        print scraper.initial_scrape(links=urls)
        scraper.update_investigation(urls)
    return redirect(url_for("webscraping"))


