# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime
import datetime as dt 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
# Base.prepare(engine, reflect=True)
Base.prepare(engine)

# Base.prepare(engine, autoload_with=engine)


# Save reference to the table
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        "<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        "<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        "<a href='/api/v1.0/2017-03-07'>/api/v1.0/start_date</a><br/>"
        "<a href='/api/v1.0/2017-03-07/2017-03-14'>/api/v1.0/start_date/end_date</a><br/>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the JSON representation of precipitation data for the last 12 months"""
    # Calculate the date one year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).\
        order_by(Measurement.date).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations for the previous year"""
    # Calculate the date one year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the temperature observations for the previous year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).\
        order_by(Measurement.date).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict[date] = tobs
        temperature_data.append(temperature_dict)

    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Parse start date into datetime object
    start_date = datetime.strptime(start, "%Y-%m-%d")



    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_stats = []
    for min_temp, avg_temp, max_temp in results:
        temperature_stats_dict = {
            "Minimum Temperature": min_temp,
            "Average Temperature": avg_temp,
            "Maximum Temperature": max_temp
        }
        temperature_stats.append(temperature_stats_dict)

    return jsonify(temperature_stats)


@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Parse start and end dates into datetime objects
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for the specified start-end range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_stats = []
    for min_temp, avg_temp, max_temp in results:
        temperature_stats_dict = {
            "Minimum Temperature": min_temp,
            "Average Temperature": avg_temp,
            "Maximum Temperature": max_temp
        }
        temperature_stats.append(temperature_stats_dict)

    return jsonify(temperature_stats)


if __name__ == '__main__':
    app.run(debug=True)