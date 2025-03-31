from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import csv
import os
from datetime import datetime, timedelta
from typing import Any
from statistics import mean
from matplotlib.markers import MarkerStyle


GARMIN_MAGENTA = "#FD02FF"

@dataclass
class Stop:
    icao: str
    lat: float
    lon: float
    arrival: datetime
    departure: datetime

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ['lat', 'lon']:
            value = float(value)
        super(Stop, self).__setattr__(name, value)


def _initialize_map(m: Basemap) -> None:
    m.fillcontinents(color='#ffd78c',lake_color='#68BBE3')
    m.drawrivers(color='#68BBE3')
    m.drawmapboundary(fill_color='#68BBE3')
    m.drawcountries(linestyle='dotted')

times_en_route = []
fig = plt.figure()

with open(os.path.dirname(__file__)+'/flightlog.csv') as source:
    stops = [Stop(**x) for x in list(csv.DictReader(source))]

    for stop in stops:
        stop.lon = stop.lon if stop.lon < 0 else stop.lon - 360

    min_lon = min([x.lon for x in stops])
    min_lat = min([x.lat for x in stops])
    max_lon = max([x.lon for x in stops])
    max_lat = max([x.lat for x in stops])
    
    m = Basemap(
        llcrnrlon=min_lon-5.,
        llcrnrlat=min_lat-3.,
        urcrnrlon=max_lon+5.,
        urcrnrlat=max_lat+3.,
        resolution='h',
        projection='cyl',
        fix_aspect='C'
    )
    _initialize_map(m)

    ms = MarkerStyle("D").scaled(0.5, 0.5)

    for i,stop in enumerate(stops):
        m.scatter(
            x=[stop.lon],
            y=[stop.lat], 
            latlon=True, 
            marker=ms,
            color=GARMIN_MAGENTA, 
            label=[stop.icao]
        )
        plt.text(
            *m(stop.lon+0.2, stop.lat+0.2), 
            stop.icao, 
            zorder=99.9, 
            fontsize="xx-small",
            # fontweight="light",
            color="white",
            bbox=dict(facecolor='black', edgecolor=GARMIN_MAGENTA, pad=1.2)
        )
        if i == 0:
            continue
        last_stop = stops[i-1]
        m.plot(
            x=[last_stop.lon,stop.lon],
            y=[last_stop.lat,stop.lat], 
            color=GARMIN_MAGENTA, 
            latlon=True
        )
        times_en_route.append(datetime.fromisoformat(stop.arrival)-datetime.fromisoformat(last_stop.departure))
        # plt.text(*m(
        #     mean([last_stop.lon, stop.lon])+0.1, 
        #     mean([last_stop.lat, stop.lat])+0.1), 
        #     '{:02}:{:02}'.format(time_en_route.seconds//3600, (time_en_route.seconds//60)%60),
        #     backgroundcolor="#ff24ff",
        #     color="#ffffff",
        #     fontsize="xx-small")

print(sum([x.seconds for x in times_en_route]))

plt.show()
