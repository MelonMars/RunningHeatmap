import gpxpy
import gpxpy.gpx
import folium
from geopy.distance import great_circle
import os

def is_close(pt1, pt2, tolerance=1):
    return great_circle(pt1, pt2).meters <= tolerance


points = []
for i, file in enumerate(os.listdir("GPX")):
    fPoints = []
    with open("GPX/"+file, "r") as gpxFile:
        gpx = gpxpy.parse(gpxFile)
        points.append([[point.latitude, point.longitude] for track in gpx.tracks for segment in track.segments for point in segment.points])


def contiguousOverlaps(points, tolerance=50):
    print("Contiguous Overlaps")
    cont_segs = []
    overIs = segmentIndex(points, tolerance)
    if not overIs:
        return cont_segs

    curr_seg = [points[overIs[0]]]
    for i in range(1, len(overIs)):
        if overIs[i] == overIs[i - 1] + 1:
            curr_seg.append(points[overIs[i]])
        else:
            cont_segs.append(curr_seg)
            curr_seg = [points[overIs[i]]]
    cont_segs.append(curr_seg)

    return cont_segs


def segmentIndex(points, tolerance=1):
    indices = []
    for i, pt in enumerate(points):
        if i == 0:
            continue
        if is_close(pt, points[i-1], tolerance):
            indices.append(i)
    return indices

tolerance = 1
flat_points = [point for sublist in points for point in sublist]
all_overlaps = []
for run in points:
    overlaps = []
    for i, pt in enumerate(points[0]):
        overlaps = []
        for other_run in points:
            if run == other_run:
                continue
            for pt in run:
                if any(is_close(pt, other_pt, tolerance) for other_pt in other_run):
                    overlaps.append(pt)

        cps = contiguousOverlaps(overlaps, tolerance)
        all_overlaps.append(cps)

overlapCnts = {}
for contiguous_parts in all_overlaps:
    for part in contiguous_parts:
        partT = tuple(part)
        if partT in overlapCnts:
            overlapCnts[partT] += 1
        else:
            overlapCnts[partT] = 1

sorted_overlaps = sorted(overlapCnts.items(), key=lambda x: x[1], reverse=True)

for segment, count in sorted_overlaps:
    print(f"Segment: {segment}, Count: {count}")
