import gpxpy
import gpxpy.gpx
import folium
from geopy.distance import great_circle
import os
import numpy as np


def is_near(p1, p2, threshold=10):
    return [p1,p2] if great_circle((p1.latitude, p1.longitude), (p2.latitude, p2.longitude)).meters < threshold else [0, 0]


points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    fPoints.append(point)
    points.append(fPoints)

overlaps = []
