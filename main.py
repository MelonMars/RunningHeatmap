import branca
import geopy.distance
import gpxpy.gpx
import folium
import os
import math

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


points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        points.append([[point.latitude, point.longitude] for track in gpx.tracks for segment in track.segments for point in segment.points])

def calculate_centroid(cluster):
    latitudes = [p[0] for p in cluster['points']]
    longitudes = [p[1] for p in cluster['points']]
    return (sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes))


def find_cluster(pt, clusters, tolerance=2):
    for cluster in clusters:
        if any(is_close(pt, p, tolerance) for p in cluster['points']):
            return cluster
    return None

clusters = []
decimals = 5
for run in points:
    for pt in run:
        rpt = round(pt[0], decimals), round(pt[1], decimals)
        cluster = find_cluster(rpt, clusters, tolerance=5)
        if cluster:
            cluster['points'].append(rpt)
            cluster['size'] += 1
        else:
            clusters.append({'points': [rpt], 'size': 1})

def get_color(size, min_size, max_size):
    color_scale = branca.colormap.linear.YlOrRd_09.scale(min_size, max_size)
    return color_scale(size)

def find_nearest_centroid(centroid, other_centroids):
    min_distance = float('inf')
    nearest_centroid = None
    for other in other_centroids:
        distance = geopy.distance.distance(centroid, other).m
        if distance < min_distance:
            min_distance = distance
            nearest_centroid = other
    return nearest_centroid


centroids = [calculate_centroid(cluster) for cluster in clusters]
sizes = [cluster['size'] for cluster in clusters]
min_size, max_size = min(sizes), max(sizes)

m = folium.Map(location=(centroids[0][0], centroids[0][1]), zoom_start=13)

centroid_map = {}
for cluster in clusters:
    centroid = calculate_centroid(cluster)
    centroid_map[tuple(centroid)] = cluster['size']

all_centroids = list(centroid_map.keys())

connected = set()
for centroid in all_centroids:
    nearest_centroid = find_nearest_centroid(centroid, [c for c in all_centroids if c != centroid])
    if nearest_centroid and (nearest_centroid, centroid) not in connected and (centroid, nearest_centroid) not in connected:
        size1 = centroid_map[centroid]
        size2 = centroid_map[nearest_centroid]
        max_size = max(size1, size2)
        folium.PolyLine(
            locations=[centroid, nearest_centroid],
            color=get_color(max_size, min_size, max_size),
            weight=5,
            opacity=0.6
        ).add_to(m)
        connected.add((centroid, nearest_centroid))


m.save('index.html')