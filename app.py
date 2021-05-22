import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/2015-07-01<br/>"
        f"/api/v1.0/start_end_date/2015-07-01/2016-07-01"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create dictionary
    prcp_all = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_all.append(prcp_dict)

    return jsonify(prcp_all)
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of stations"""
    results = session.query(Station.station).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d')
    year_ago = latest_date_dt.date() - dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == Station.station).\
    filter(Station.id == 7).all()
    temp_df=pd.DataFrame(temp)
    session.close()

    temp_list = list(np.ravel(temp_df['tobs']))

    return jsonify(temp_list)

@app.route("/api/v1.0/start_date/<start>")
def summary_temp_start(start):
    session = Session(engine)
    temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date>=start).all()

    session.close()
    temp_sum = list(np.ravel(temp))
    return jsonify(temp_sum)

@app.route("/api/v1.0/start_end_date/<start>/<end>")
def summary_temp_start_end(start, end):
    session = Session(engine)
    temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date>=start).\
    filter(Measurement.date<=end).all()

    session.close()
    temp_sum = list(np.ravel(temp))
    return jsonify(temp_sum)