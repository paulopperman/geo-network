import geopandas as gpd
import shapely as sh
import networkx as nx

file = "./test-geometry/test-geometry.shp"

buffersize = .00000000005  # set the buffer around the line to search for intersections.  should be < 1e-6

# get GeoDataFrame of linestrings
gdf = gpd.read_file(file)
intersections = gpd.GeoDataFrame(columns=['line1', 'line2','geometry'])  # geodataframe to store intersection points
points = []
G = nx.Graph()

# populate coordinate lists for each element
for i in range(0, len(gdf)):
    points.append(list(gdf.iloc[i].geometry.coords))  # append the linestring

# find intersection points
for m in range(0, len(gdf)):
    s = gdf.iloc[m]
    for n in range(m+1, len(gdf)):  # iterate through all the upcoming lines
        t = gdf.iloc[n]
        if t.geometry.intersects(s.geometry.buffer(buffersize)):  # check for intersection or near-touching
            overlap = t.geometry.intersection(s.geometry.buffer(buffersize)).centroid()  # this will return a line, so get the center
            where_on_s = s.geometry.project(overlap)  # find the distance along s where t intersects
            intersection = s.geometry.interpolate(where_on_s)  # get the point on s where the intersection is
            temp_gdf = gpd.GeoDataFrame([[m,n,intersection]],columns=['line1', 'line2','geometry'])  # build dataframe of intersection
            intersections = intersections.append(temp_gdf,ignore_index=True)  # append interection to intersection list

# if the intersection is not on a line, it will be an endpoint





# gdf.iloc[0].geometry.project(gdf.iloc[2].geometry.intersection(gdf.iloc[0].geometry))
# gdf.iloc[0].geometry.interpolate(gdf.iloc[0].geometry.project(gdf.iloc[2].geometry.intersection(gdf.iloc[0].geometry))_

