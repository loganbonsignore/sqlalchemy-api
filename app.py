from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

# Connecting to DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Defining tables as class objects
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating server connection
app = Flask(__name__)

def get_dates():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    session = Session(engine)
    max_date = session.query(func.max(Measurement.date)).first()[0].split("-")
    max_date_obj = dt.date(int(max_date[0]),int(max_date[1]),int(max_date[2]))
    start_date = max_date_obj - dt.timedelta(days=365)
    session.close()
    return start_date, max_date



# Establishing Routes
@app.route("/")
def index():
    return (
        "<strong>Available Routes:</strong><br/><br/>"
        "<figure>/api/v1.0/precipitation<br/><br/>"
        "/api/v1.0/stations<br/><br/>"
        "/api/v1.0/tobs<br/><br/>"
        "/api/v1.0/{*start_date}<br/><br/>"
        "/api/v1.0/{*start_date}/{*end_date}</figure><br/><br/>"
        "<strong>*All dates must be formatted as YYYY-MM-DD</strong>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    start_date, max_date = get_dates()
    # Querying date and precipitation data
    prcp = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date>=start_date) \
        .order_by(Measurement.date.desc()).all()
    session.close()
    prcp_dict = {date:prcp for date, prcp in prcp}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_list = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def obs_station():
    session = Session(engine)
    start_date, max_date = get_dates()

    observation_station = session.query(Station.id, Measurement.station, func.count(Measurement.tobs)) \
        .filter(Measurement.station==Station.station) \
        .group_by(Measurement.station) \
        .order_by(func.count(Measurement.tobs).desc()).first()

    obsv_station_temp = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.date>=start_date) \
        .filter(Measurement.station==observation_station[1]) \
        .order_by(Measurement.date.desc()).all()

    temps = [temp for date, temp in obsv_station_temp]
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def summary(start):
    session = Session(engine)
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).first()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).first()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).first()
    output = {
        "Max Temp":max_temp[0],
        "Min Temp":min_temp[0],
        "Avg Temp":avg_temp[0],
    }
    session.close()
    return jsonify(output)

@app.route("/api/v1.0/<start>/<end>")
def summary_stats(start, end):
    session = Session(engine)
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).first()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).first()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).first()
    output = {
        "Max Temp":max_temp[0],
        "Min Temp":min_temp[0],
        "Avg Temp":avg_temp[0],
    }
    session.close()
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)