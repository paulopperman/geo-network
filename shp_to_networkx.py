import geopandas as gpd
import shapely as sh
import networkx as nx

file = "./test-geometry/test-geometry.shp"

buffersize = .00000000005  # set the buffer around the line to search for intersections.  should be < 1e-6

# get GeoDataFrame of linestrings
gdf = gpd.read_file(file)

# add column for the subgraph of each linestring
gdf['graph'] = gdf.apply(lambda x: {}, axis=1)

# initialize the main graph
G = nx.Graph()

# start a node counter
next_node = 0

# build the subgraphs for each line
for m in range(0, len(gdf)):
    s = gdf.iloc[m]  # placeholder for geometry analysis
    # collect base nodes
    pts = list(gdf.iloc[m].geometry.coords)
    for p in pts:
        gdf.graph.iloc[m][next_node] = sh.geometry.Point(p)  # TODO: streamline with a placeholder graph so we're not selecting from gdf every time
        next_node = next_node+1

    for n in range(m+1, len(gdf)):  # iterate through all the upcoming lines
        t = gdf.iloc[n]  # placeholder for geometry analysis

        if t.geometry.intersects(s.geometry.buffer(buffersize)):  # check for intersection or near-touching
            overlap = t.geometry.intersection(s.geometry.buffer(buffersize))
            end_buffer = t.geometry.length - (2*buffersize)  # calculate the buffer zone around the end of the line

            # handle geomoetry collections, and turn everything into list of geometry
            if overlap.geom_type == 'GeometryCollection':  # if multiple intersections were returned, make a list
                overlap = list(overlap)
            else:  # else convert to a single element list
                overlap = [overlap]

            # get a representative point for the geometry and add nodes to graphs
            for o in overlap:
                o_pt = o.representative_point()  # FIXME: this will result in some weird and close node placements if intersection is an endpoint (clean up big graph?)
                o_proj = s.geometry.project(o_pt)
                int_point = s.geometry.interpolate(o_proj)
                gdf.graph.iloc[m][next_node] = int_point
                gdf.graph.iloc[n][next_node] = int_point
                next_node = next_node+1

    # compute edge distances






# gdf.iloc[0].geometry.project(gdf.iloc[2].geometry.intersection(gdf.iloc[0].geometry))
# gdf.iloc[0].geometry.interpolate(gdf.iloc[0].geometry.project(gdf.iloc[2].geometry.intersection(gdf.iloc[0].geometry))_

