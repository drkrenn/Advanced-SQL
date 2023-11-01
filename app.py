# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

Base.prepare(autoload_with = engine)

Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
session

# Find the most recent date in the data set.
datequery= session.query(func.max(measurement.date)).first()
datequery

# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Calculate the date one year from the last date in data set.
start_date = dt.date(2017,8,23)- dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
precipquery=session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).all()

# # Save the query results as a Pandas DataFrame. Explicitly set the column names
precip_df = pd.DataFrame(precipquery, columns=['date', 'prcp'])

# Sort the dataframe by date
precip_df= precip_df.sort_values('date')

# Use Pandas Plotting with Matplotlib to plot the data
precip_df.plot(x='date', y='prcp', rot=90)
plt.xlabel = ("Date")
plt.ylabl = ("Precipitation(in.)")

prcp_summary = precip_df['prcp'].describe()
prcp_summary

stationquery= session.query(station.station).count()
stationquery

# Design a query to find the most active stations (i.e. which stations have the most rows?)
# List the stations and their counts in descending order.
activecount = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(-func.count(measurement.station)).all()
activecount

maxtemp = session.query(func.max(measurement.tobs)).\
    filter(measurement.station == 'USC00519281').first()
maxtemp

mintemp = session.query(func.min(measurement.tobs)).\
    filter(measurement.station == 'USC00519281').all()
mintemp

avgtemp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.station == 'USC00519281').all()
avgtemp

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
tempquery=session.query(measurement.tobs, measurement.station, measurement.date).\
    filter(measurement.date >= start_date).all()

temp_df=pd.DataFrame(tempquery, columns=['temp', 'station', 'date'])
temp_df=temp_df.loc[temp_df["station"]== 'USC00519281']
temp_df

grouptemp = temp_df.groupby(["temp"])
grouptemp_df = grouptemp.count()
grouptemp_df

grouptemp_df['station'].plot(kind ='bar', xlabel='Temperature', ylabel='Frequency')

plt.show()

# Close Session
session.close()

#################################################
# Flask Setup
# #################################################
from flask import Flask, jsonify

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to my weather statistics page! <br/>"
        f"Twelve Months of Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Most Active Station Temperature Data: /api/v1.0/tobs<br/>"
        f"Temperature Stats Semi-reduced: /api/v1.0/start<br/>"
        f"Temperature Stats Fully-reduced: /api/v1.0/starttoend"
    )

precip = precip_df.to_dict()

@app.route("/api/v1.0/precipitation")
def precipitation():
    return jsonify(precip)

active_df = pd.DataFrame(activecount, columns=['station', 'count'])
active_df=active_df[['station']]
active = active_df.to_dict()

@app.route("/api/v1.0/stations")
def stations():
    return jsonify(active)


temp_df=temp_df[['temp','date']]

temp = temp_df.to_dict()

@app.route("/api/v1.0/tobs")
def temperature():
    return jsonify(temp)

maxtemp2 = session.query(func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).first()
maxtemp2

mintemp2 = session.query(func.min(measurement.tobs)).\
    filter(measurement.date >= start_date).all()
mintemp2

avgtemp2 = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
avgtemp2

@app.route("/api/v1.0/start")
def afterdata():
    return (
        f"Temperature Stats after 8/23/2016:<br/>"
        f"max temp="+str(maxtemp2)+"<br/>"
        f"min temp="+str(mintemp2)+"<br/>"
        f"avg temp="+str(avgtemp2)
    )

end_date = dt.date(2016,10,23)

maxtemp3 = session.query(func.max(measurement.tobs)).\
    filter(measurement.date >= start_date, measurement.date <=end_date).first()
maxtemp3

mintemp3 = session.query(func.min(measurement.tobs)).\
    filter(measurement.date >= start_date, measurement.date <=end_date).all()
mintemp3

avgtemp3 = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date, measurement.date <=end_date).all()
avgtemp3

@app.route("/api/v1.0/starttoend")
def betweendata():
    return (
        f"Temperature Stats between 8/23/2016 and 10/23/2016:<br/>"
        f"max temp="+str(maxtemp3)+"<br/>"
        f"min temp="+str(mintemp3)+"<br/>"
        f"avg temp="+str(avgtemp3)
    )

if __name__ == '__main__':
    app.run(debug=True)

