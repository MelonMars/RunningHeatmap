import gpxpy
import gpxpy.gpx
import folium
from geopy.distance import great_circle
import os
from itertools import product
from rtree import index


def is_near(p1, p2, threshold=0.001):
    return great_circle((p1[0], p1[1]), (p2[0], p2[1])) < threshold


points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    fPoints.append([point.latitude, point.longitude])
    points.append(fPoints)

overlaps = []
all_points = [p for sublist in points for p in sublist]
buffer_size = 0.00001
idx = index.Index()
for i, point in enumerate(all_points):
    idx.insert(i, (point[1] - buffer_size, point[0] - buffer_size, point[1] + buffer_size, point[0] + buffer_size))
for i, point in enumerate(all_points):
        possible_matches = list(idx.intersection((point[1] - buffer_size, point[0] - buffer_size, point[1] + buffer_size, point[0] + buffer_size)))
        if any(is_near(point, all_points[match]) for match in possible_matches):
            overlaps.append(point)


m = folium.Map(location=(overlaps[0][0], overlaps[0][1]))
folium.PolyLine(overlaps).add_to(m)
m.save("index.html")