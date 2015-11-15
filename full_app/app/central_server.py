from flask import Flask, render_template, request
import requests
import datetime
from flask.ext.sqlalchemy import SQLAlchemy
central_server_app = Flask(__name__)

central_server_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///investigations.db" #os.environ["DATABASE_URL"]
central_server_db = SQLAlchemy(central_server_app)

class InvestigationLogger(central_server_db.Model):
    __tablename__ = 'investigation_logger'
    id = central_server_db.Column(central_server_db.Integer, primary_key=True)
    investigation_id = central_server_db.Column(central_server_db.String(400))
    timestamp = central_server_db.Column(central_server_db.DateTime, default=datetime.datetime.now)
    
    def __init__(self,investigation_id):
        self.investigation_id = investigation_id 

    def __repr__(self):
        return '<investigation_id %r>' % self.investigation_id

@central_server_app.route("/<investigation_id>",methods=["GET","POST"])
def index(investigation_id):
    try:
        investigation_id = str(investigation_id)
        investigation_log = InvestigationLogger(investigation_id)
        central_server_db.session.add(investigation_log)
        central_server_db.session.commit()
        return "success"
    except:
        return "failure"

if __name__ == '__main__':
    central_server_app.run(
        host='0.0.0.0',
        port=5003
    )
