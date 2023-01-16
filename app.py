import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import session
from sqlalchemy import create_engine, func
import datetime as dt 
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    '''
    This is the initial page that will give the routes the user can go to
    '''
    return (
        f"<h1>Welcome to my climate app</h1><br/>" 
        f"<h2>This is the solution for #2 on the sqlalchemy-challenge</h2><br/>"
        f"<br/>"
        f"<h3>Available routes</h3><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2014-05-01  - please enter a date between <strong>2010-01-01  and 2017-08-23</strong> in that format<br/>"
        f"/api/v1.0/2014-05-01/2015-04-30 - please enter a <strong>start date and end date</strong> between <strong>2010-01-01 and 2017-08-23</strong> in that format "
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    '''
    This gives the precipitation in json format for date and precipitation in the last year
    '''
    
    
    lastdate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between(startdate,lastdate)).\
            all()
    
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    '''
    This will give a list of stations available to review
    '''
    session = session(engine)

    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    '''
    This will give the temperatures and dates for the alstyear for the station
    with the most observations
    '''
    session = session(engine)

    top_station = session.query(measurement.station).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.station).desc()).\
                    subquery()

    lastdate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    
    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.date.between(startdate,lastdate)).\
                filter(measurement.station.in_(top_station)).\
                all()
    session.close()