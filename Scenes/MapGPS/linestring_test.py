from shapely.geometry import LineString

line1 = LineString([(0,0), (1,1), (2,2), (2,2)])
line2 = LineString([(-1,4), (0,4), (2,4), (3,4)])

if line1.crosses(line2):
    print("hi")