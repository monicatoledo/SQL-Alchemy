import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app= Flask(__name__)

# Flask Routes

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"follow by a start date on the form /2014-02-15/<br/>" 
        f"choose a range start date / end date should be yyyy-mm-dd / yyyy-mm-dd format<br/>"
        f"(Available dates range 2010-01-01 to 2017-08-23)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year"""
    precip_query = [Measurement.date, Measurement.tobs]
    results = session.query(*precip_query).\
        filter(Measurement.date >= "2016-08-23").\
        order_by(Measurement.date).all()
    precip_dict=[]
    for result in results:
        precip={}
        precip["date"]= result[0]
        precip["temperature"]=result[1]
        precip_dict.append(precip)
    return jsonify(precip_dict)

@app.route("/api/v1.0/station")
def station():
    """Return a JSON list of stations from the dataset"""
    results = session.query(Station.name, Station.station).all()
    # stations=[results]
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    precip = [Measurement.date, Measurement.tobs]
    results = session.query(*precip).\
        filter(Measurement.date >= "2016-08-23").\
        order_by(Measurement.date).all()
    #precip_lastyear=[results]
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    temp_query= [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    temp_results=session.query(*temp_query).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()
    temp_list=[]
    for result in temp_results:
        temps={}
        temps["Start Date"]= start
        temps["Min Temperature"]= float(result[0])
        temps["Max Temperature"]= float(result[1])
        temps["Average Temperature"]= float(result[2])
        temp_list.append(temps)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def range_dates(start,end):
    """calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    temp_range= [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    range_results=session.query(*temp_range).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        all()
    range_list=[]
    for result in range_results:
        temperature={}
        temperature["Start Date"]= start
        temperature["End Date"]= end
        temperature["Min Temperature"]= float(result[0])
        temperature["Max Temperature"]= float(result[1])
        temperature["Average Temperature"]= float(result[2])
        range_list.append(temperature)
    return jsonify(range_list)

if __name__ == '__main__':
    app.run(debug=True)