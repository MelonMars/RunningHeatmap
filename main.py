import gpxpy
import gpxpy.gpx
import folium
from geopy.distance import great_circle
import os
from itertools import combinations
from sklearn.cluster import DBSCAN

def is_close(pt1, pt2, tolerance=1):
    return great_circle(pt1, pt2).meters <= tolerance


points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        points.append([[point.latitude, point.longitude] for track in gpx.tracks for segment in track.segments for point in segment.points])

def findClosePt(pt, pts, tolerance=2):
    for ept in pts:
        if is_close(pt, ept, tolerance):
            return ept
    return None

ptCnts = {}
decimals = 5
for run in points:
    for pt in run:
        rpt = round(pt[0], decimals), round(pt[1], decimals)
        closePt = findClosePt(rpt, ptCnts.keys(), tolerance=2)
        if closePt:
            ptCnts[closePt] += 1
        else:
            ptCnts[rpt] = 1


overlaps = [pt for pt, count in ptCnts.items() if count > 1]
if overlaps:
    m = folium.Map(location=(overlaps[0][0], overlaps[0][1]), zoom_start=13)
    for pt, count in ptCnts.items():
        if count > 1:
            folium.CircleMarker(location=pt, radius=3, color='red', fill=True, fill_color='red', fill_opacity=0.6, popup=f"Count: {count}").add_to(m)
    m.save("index.html")
else:
    print("No overlapping points found")
m.save("index.html")
