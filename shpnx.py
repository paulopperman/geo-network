import geopandas as gpd
import shapely as sh
import networkx as nx
import numpy as np

def get_graph_from_gdf(gdf, find_intersections=True, intersection_buffersize=0.00000000005):
    """
    Generate a networkx MultiDiGraph from a collection of linestrings in a GeoPandas GeoDataFrame
    :param gdf: The geodataframe containing linestrings
    :param find_intersections: detect intersections of linestrings (default True)
    :param intersection_buffersize: Set the tolerance around the linestrings to detect intersections
    :return:
    """
    # drop empty geometries
    gdf = gdf.drop(gdf[gdf.geometry.values == None].index)

   # add column for the subgraph of each linestring
    gdf['nodes'] = gdf.apply(lambda x: {}, axis=1)
    gdf['edges'] = np.empty((len(gdf), 0)).tolist()

    # initialize the main graph
    G = nx.MultiDiGraph()

    node_dict = {}

    # start a node counter
    next_node = 0

    # build the subgraphs for each line
    for m in range(0, len(gdf)):
        s = gdf.iloc[m]  # placeholder for geometry analysis
        pts = []
        # collect base nodes

        # FIXME: this multilinestring geometry check is a hack to overcome what appears to be a non-issue. need to figure something better to handle geometry types
        if gdf.iloc[m].geometry.geom_type == "MultiLineString":
            geom = list(gdf.iloc[m].geometry)
        else:
            geom = [gdf.iloc[m].geometry]
        for _ in geom:
            pts.extend(list(_.coords))
        for p in pts:
            point = sh.geometry.Point(p)
            dist = s.geometry.project(point)
            gdf.nodes.iloc[m][next_node] = {'point':point,'pos':dist}  # TODO: streamline with a placeholder graph so we're not selecting from gdf every time
            next_node = next_node+1
        if find_intersections:
            for n in range(m+1, len(gdf)):  # iterate through all the upcoming lines
                t = gdf.iloc[n]  # placeholder for geometry analysis

                if t.geometry.intersects(s.geometry.buffer(intersection_buffersize)):  # check for intersection or near-touching
                    overlap = t.geometry.intersection(s.geometry.buffer(intersection_buffersize))
                    end_buffer = t.geometry.length - (2 * intersection_buffersize)  # calculate the buffer zone around the end of the line

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
                        gdf.nodes.iloc[m][next_node] = {'point':int_point, 'pos':o_proj}
                        gdf.nodes.iloc[n][next_node] = {'point':int_point, 'pos':t.geometry.project(o_pt)}
                        next_node = next_node+1

        # build edge array of tuples
        subg = gpd.GeoDataFrame.from_dict(data=gdf.nodes.iloc[m],orient='index')  # load dict as geodataframe for processing
        ordered_points = list(subg.sort_values(by='pos', axis=0).index)  # get list of nodes sorted by position
        for r in range(0, len(ordered_points)-1):
            edge_length = subg.iloc[r]['point'].distance(subg.iloc[r+1]['point'])  # distance to the next point
            gdf.iloc[m].edges.append((ordered_points[r],ordered_points[r+1],{'length':edge_length}))

        for _ in gdf.nodes.iloc[m].keys():
            G.add_node(_, point=gdf.nodes.iloc[m].get(_)['point'])

        G.add_edges_from(gdf.edges.iloc[m])

    return G
