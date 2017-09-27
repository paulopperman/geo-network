"""
Build networkx network out of geopandas linestrings (maybe extend to other geometries, like touching polygons?)
"""

import geopandas as gpd
import shapely as sh
import networkx as nx

file = "./test-geometry/test-geometry.shp"

# get GeoDataFrame of linestrings
gdf = gpd.read_file(file)

G = nx.Graph()  # initialize the graph
node_counter = 0  # global node id counter to ensure unique node names

# find the number of lines to iterate through
gdfsize = len(gdf)

buffersize = .00000000005  # set the buffer around the line to search for intersections.  should be < 1e-6

# iterate through the geometry column of each item in the gdf
for i in range(0,gdfsize):
    # Get the coordinates of the points in the linestring
    s = gdf.iloc[i].geometry
    s_buf = s.buffer(buffersize)  # get the geometry with a buffer for testing intersections

    # Populate the graph with the component points as nodes
    feature_len = len(list(s.geometry))  # find how many parts of the linestring there are
    f_iter = 0  # initialize a counter
    i_node_points = []  # initialize the point list for the nodes
    while f_iter < feature_len:  # loop through the parts
        segment_coords = list(s.geometry)[f_iter].coords
        seg_len = len(segment_coords)  # number of points
        seg_iter = 0  # initialize counter
        while seg_iter < seg_len:  # loop through the component points
            line_point = sh.geometry.Point(segment_coords[seg_iter])  # extract the point as a shapely object
            i_node_points.append(line_point)  # add the point to the collection

    for k in range(i+1,gdfsize):
        q = gdf.iloc[k].geometry
        if s_buf.intersects(q):  # only get geometry if there's an intersection
            p = s_buf.intersection(q).centroid  # intersection returns a very tiny line, so get the middle of it.
            i_node_points.append(p)  # add p to i's list of node coordinates




