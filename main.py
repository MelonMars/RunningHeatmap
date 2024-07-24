import gpxpy.gpx
import folium
import os
import math
from math import sqrt

def is_close(pt1, pt2, tolerance=1):
    R = 6371000
    lat1_rad = math.radians(pt1[0])
    lon1_rad = math.radians(pt1[1])
    lat2_rad = math.radians(pt2[0])
    lon2_rad = math.radians(pt2[1])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance <= tolerance

def distance(pt1, pt2):
    R = 6371000
    lat1_rad = math.radians(pt1[0])
    lon1_rad = math.radians(pt1[1])
    lat2_rad = math.radians(pt2[0])
    lon2_rad = math.radians(pt2[1])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        points.append([[point.latitude, point.longitude] for track in gpx.tracks for segment in track.segments for point in segment.points])

def find_closest_neighbors(pt, pts, threshold=15):
    distances = [(ept, distance(pt, ept)) for ept in pts]
    distances = sorted(distances, key=lambda x: x[1])
    closest = [pt for pt, dist in distances if dist <= threshold]
    return closest[:2]

def cluster_key(pt, factor=0.1):
    return (round(pt[0] / factor) * factor, round(pt[1] / factor) * factor)


pt_counts = {}
decimals = 5
clustering_factor = 0.00015
for run in points:
    for pt in run:
        rpt = cluster_key(pt, clustering_factor)
        if rpt not in pt_counts:
            pt_counts[rpt] = []
        closest_pts = find_closest_neighbors(rpt, pt_counts.keys())
        pt_counts[rpt].extend(closest_pts)

lines = set()
for pt, neighbors in pt_counts.items():
    for neighbor in neighbors:
        if (pt, neighbor) not in lines and (neighbor, pt) not in lines:
            lines.add((pt, neighbor))

maxCnt = max({pt: len(neighbors) for pt, neighbors in pt_counts.items()}.values())
if pt_counts:
    m = folium.Map(location=(list(pt_counts.keys())[0][0], list(pt_counts.keys())[0][1]), zoom_start=13)
    for pt1, pt2 in lines:
        normalized_value = min(max(len(pt_counts[pt1]), len(pt_counts[pt2])) / maxCnt, 1)
        red_intensity = int(normalized_value * 255)
        red_hex = f'{red_intensity:02X}'
        hex_color = f'#{red_hex}0000'
        folium.PolyLine([pt1, pt2], color=hex_color, weight=2.5, opacity=0.6).add_to(m)
    m.save("index.html")
else:
    print("No overlapping points found")
