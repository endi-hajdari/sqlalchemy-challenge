# Importing all the dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt 

# Setting up the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting the existing database into a new model
Base = automap_base()

# Reflecting the tables
Base.prepare(autoload_with=engine)

# Saving the reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


# Flask Setup
app = Flask(__name__)

# Displaying all of the routes that are avaiable 
@app.route("/")

def home():
    print('Server recevied request for home page')
    return (
        f"<h1>Welcome! This is the home page of my climate application.</h1><br/>" 
        f"<h3>Available Routes:</h3><br/>"
        f"/api/v1.0/precipitation:<br/>"
        f"/api/v1.0/stations:<br/>"
        f"/api/v1.0/tobs:<br/>"
        f"/api/v1.0/2014-05-01  - please enter a date between <strong>2010-01-01  and 2017-08-23</strong> using the yyyy-mm-dd format <br/>"
        f"/api/v1.0/2014-05-01/2015-04-30 - please enter a <strong>start date and end date</strong> between <strong>2010-01-01 and 2017-08-23</strong> using the yyyy-mm-dd format"
    )

# Route that diplays the precipitation data for the previous year
@app.route("/api/v1.0/precipitation")
def precipitation():
    lastdate = session.query(func.max(measurement.date)).\
                    scalar()
    dt_lastdate= dt.datetime.strptime(lastdate,"%Y-%m-%d").date()
    dt_startdate = dt_lastdate - dt.timedelta(days=365)
    startdate = dt_startdate.strftime("%Y-%m-%d")
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between(startdate,lastdate)).\
            all()
    
    session.close()

# Route that diplays the station data
@app.route("/api/v1.0/stations")
def stations():
    session = session(engine)

    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# Route that diplays the temperature observed data for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
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