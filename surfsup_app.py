# Import the dependencies.
import numpy as np
import datetime as dt
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Access the SQLite database.
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect database tables into ORM classes.
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save a reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to the database.
session = Session(engine)

# Define the Flask app.
app = Flask(__name__)


# Database Setup
#################################################
# reflect an existing database into a new model

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - List of stations from the dataset<br/>"
        f"/api/v1.0/tobs - Temperature observations for the previous year<br/>"
        f"/api/v1.0/temp/start/end - Min, Max, and Avg temperature for a given range<br/>"
        f"/api/v1.o/<start>/<end> -Temperature stats for a given range"
    )

#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    from datetime import datetime
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(station_list))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)
    temperature = session.query(Measurement.data, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= one_year_ago).all()
    session.close()
    temperatures = list(np.ravel(temperature))
    return jsonify(temperatures=temperatures)

@app.route("/api/v1.0/temp/<start>/<end>")
def start_temp(start):
    session = Session(engine)
    temperature = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    return jsonify(temperature)

@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_temp(start, end):
    session = Session(engine)
    temperature = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(temperature)

#################################################
# Flask Setup
#################################################
if __name__ == "__main__":
    app.run(debug=True)
