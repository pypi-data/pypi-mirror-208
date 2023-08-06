from .model import *
from .segmentationReader import *
from .utils import *
import networkx as nx
from geojson import Point, LineString, Feature, FeatureCollection, dumps

class CrModel:

    def __init__(self):

        self.crossroad = None
        Junction._junctions = {}

    def computeModel(self, G, segmentation_file):
        #
        # Model completion
        #

        seg_crossroad = SegmentationReader(segmentation_file).getCrossroads()[0]

        # intersection center. Computed by mean coordinates, may use convex hull + centroid later
        crossroad_center = meanCoordinates(G, seg_crossroad.border_nodes)

        # crossroad nodes creation
        crossroad_inner_nodes = {}
        crossroad_border_nodes = {}
        crossroad_external_nodes = {}
        for node_id in seg_crossroad.inner_nodes:
            crossroad_inner_nodes[node_id] = createJunction(node_id, G.nodes[node_id])
        for node_id in seg_crossroad.border_nodes:
            crossroad_border_nodes[node_id] = createJunction(node_id, G.nodes[node_id])
        for branch in seg_crossroad.branches :
            for node_id in branch.border_nodes:
                if node_id not in (list(crossroad_inner_nodes.keys()) + list(crossroad_border_nodes.keys())):
                    crossroad_external_nodes[node_id] = createJunction(node_id, G.nodes[node_id])

        #crossroad edges creation
        crossroad_edges = {}
        for edge in seg_crossroad.edges_by_nodes:
            edge_id = "%s;%s"%(edge[0],edge[1])
            crossroad_edges[edge_id] = createWay(edge_id, edge, G)
        for branch in seg_crossroad.branches:
            for edge in branch.edges_by_nodes:
                edge_id = "%s;%s"%(edge[0],edge[1])
                crossroad_edges[edge_id] = createWay(edge_id, edge, G, seg_crossroad.border_nodes)    

        # Get border path of the intersection, then keep only the border nodes (the external nodes of the branches)
        border_path = getBorderPath(G, crossroad_inner_nodes, crossroad_border_nodes, crossroad_external_nodes, crossroad_edges)
        external_nodes = [junction.id for junction in crossroad_external_nodes.values()] #list(dict.fromkeys(filter(lambda node : node in  list(crossroad_external_nodes.keys()), border_path)))
        branch_edges = getBranchesEdges(border_path, seg_crossroad.branches, external_nodes)

        # create branches
        branches = {}
        for edge in branch_edges:
            if not edge["branch_id"] in branches:
                branches[edge["branch_id"]] = Branch(None, None, None, [])
            branch = branches[edge["branch_id"]]
            branch.ways.append(crossroad_edges[edge["edge_id"]])

        # add branches attributes
        min = None
        max = None
        for branch_id, branch in branches.items():
            nodes = []
            for way in branch.ways:
                if way.name != None : 
                    branch.street_name = [way.name.split(" ").pop(0).lower()," ".join(way.name.split(" ")[1:])]
                if way.junctions[0].id not in nodes : nodes.append(way.junctions[0].id)
                if way.junctions[1].id not in nodes : nodes.append(way.junctions[1].id)
            # compute branch bearing
            branch.angle = meanAngle(G, nodes, crossroad_center)
            if min is None: min,max = branch,branch
            if branch.angle < min.angle: min = branch
            if branch.angle > max.angle: max = branch

        # get the branch nearest to the north, then shift the branches list
        branches = list(branches.values())
        index = branches.index(max) if 360 - max.angle < min.angle else branches.index(min)
        branches = branches[index:] + branches[:index]

        # number branches according to their actuel order
        for i in range(len(branches)):
            branches[i].number = i + 1

        #
        # Sidewalks and islands generation
        #

        sidewalk_paths = getSidewalks(border_path, branches, external_nodes)

        # graph cleaning to remove edges that are not part of the crossroads
        G = cleanGraph(G, crossroad_edges)

        # Get sidewalks
        sidewalks = []
        for sidewalk_id, sidewalk_path in enumerate(sidewalk_paths):
            sidewalk = Sidewalk(sidewalk_id)
            sidewalks.append(sidewalk)
            for j, node in enumerate(sidewalk_path):
                if j < len(sidewalk_path)-1:
                    n1 = sidewalk_path[j]
                    n2 = sidewalk_path[j+1]
                    way = None
                    ids = ["%s;%s"%(n1,n2), "%s;%s"%(n2,n1)]
                    for id in ids:
                        if id in crossroad_edges:
                            way = crossroad_edges[id]
                    # if the way does not exist we create it (may not happen but sometimes it is)
                    if not way:
                        way = createWay("%s;%s"%(n1, n2), [n1,n2], G)
                        crossroad_edges[id] = way
                    # if the sidewalk goes in the same direction as the way, it's the left sidewalk. Otherwise it's the right one.
                    if way.junctions[0].id == n1:
                        way.sidewalks[0] = sidewalk
                    else:
                        way.sidewalks[1] = sidewalk
                    # add pedestrian nodes to the crosswalks in the way
                    for junction in way.junctions:
                        if "Crosswalk" in junction.type:
                            if sidewalk not in junction.pedestrian_nodes:
                                junction.pedestrian_nodes.append(sidewalk)

        # Get islands in the crossroads
        islands = []
        for island_id, island_path in enumerate(getIslands(G, branches, crossroad_border_nodes)):
            island_id += sidewalks[-1].id+1
            if not isPolygonClockwiseOrdered(island_path, G):
                island_path = list(reversed(island_path))
            # island is not closed by NetworkX, we close it
            island_path.append(island_path[0])
            island = Island(island_id)
            islands.append(island)
            for j, node in enumerate(island_path):
                if j < len(island_path)-1:
                    n1 = island_path[j]
                    n2 = island_path[j+1]
                    way = None
                    ids = ["%s;%s"%(n1,n2), "%s;%s"%(n2,n1)]
                    for id in ids:
                        if id in crossroad_edges:
                            way = crossroad_edges[id]
                    if way:
                        if way.junctions[0].id == n1:
                            way.islands[1] = island
                        else:
                            way.islands[0] = island
                        # add pedestrian nodes to the crosswalks in the way
                        for junction in way.junctions:
                            if "Crosswalk" in junction.type:
                                if island not in junction.pedestrian_nodes:
                                    junction.pedestrian_nodes.append(island)

        #
        # Crossings creation
        #

        crosswalks = Junction.getJunctions("Crosswalk")


        # if two crosswalks share the same pedestrian nodes, choose the nearest to the crossroads
        to_delete = []
        for c1 in crosswalks:
            for c2 in crosswalks:
                if c1 != c2:
                    if c1.pedestrian_nodes == c2.pedestrian_nodes or c1.pedestrian_nodes[::-1] == c2.pedestrian_nodes:
                        if c1.id in [n.id for n in crossroad_border_nodes.values()]:
                            to_delete.append(c2)
        for d in to_delete: crosswalks.remove(d)

        # create dual graph
        pG = nx.Graph()
        for crosswalk in crosswalks:
            pG.add_edge(
                "s%s"%crosswalk.pedestrian_nodes[0].id if isinstance(crosswalk.pedestrian_nodes[0], Sidewalk) else "i%s"%crosswalk.pedestrian_nodes[0].id, 
                "s%s"%crosswalk.pedestrian_nodes[1].id if isinstance(crosswalk.pedestrian_nodes[1], Sidewalk) else "i%s"%crosswalk.pedestrian_nodes[1].id, 
                crosswalk=crosswalk
            )

        # compute crossings
        crossings = {}
        for sidewalk_start in sidewalks:
            for sidewalk_end in list(set(sidewalks) - set([sidewalk_start])):
                try:
                    crossing = nx.shortest_path(pG, "s%s"%sidewalk_start.id, "s%s"%sidewalk_end.id)
                except: # this sidewalk can't be reached
                    continue
                crossing_id = ";".join(crossing)
                if crossing_id.count("s") <= 2: # we keep paths that don't go through other sidewalks
                    if crossing_id not in crossings.keys() and ";".join(crossing_id.split(";")[::-1]) not in crossings.keys():
                        crosswalk_list = [pG[crossing[i]][crossing[i+1]]["crosswalk"] for i in range(len(crossing)-1)]
                        crossings[crossing_id] = Crossing(crossing_id, crosswalk_list)

        # attach crossings to a branch
        for branch in branches:

            # Retrieve branch sidewalks
            branch_sidewalks = []
            for items in [way.sidewalks for way in branch.ways]:
                for sidewalk in items:
                    if sidewalk is not None and sidewalk not in branch_sidewalks:
                        branch_sidewalks.append(sidewalk)
            
            # Retrieve crossing sidewalks
            for crossing in crossings.values():
                crossing_sidewalks = []
                for crosswalk in crossing.crosswalks:
                    for pedestrian_node in crosswalk.pedestrian_nodes:
                        if isinstance(pedestrian_node, Sidewalk):
                            crossing_sidewalks.append(pedestrian_node)
                # If the branch and the crossing share the same sidewalks, it's the branch's corssing
                if branch_sidewalks == crossing_sidewalks or branch_sidewalks[::-1] == crossing_sidewalks:
                    branch.set_crossing(crossing)
                    break

        #
        # Crossroad creation
        #

        self.crossroad = Intersection(None, branches, crossroad_edges, {**crossroad_inner_nodes, **crossroad_border_nodes, **crossroad_external_nodes}, crossings, crossroad_center)

    #
    # Generate a JSON that bind generated descriptions to OSM nodes
    #
    # Dependencies : the non-concatenated description
    # Returns : the JSON as a string

    def getJSON(self):

        data = {
                "center" : self.crossroad.center,
                "branches" : {},
                "junctions" : {},
                "ways" : {},
                "pedestrian_nodes" : {},
        }

        # Ways handling
        for way_id in self.crossroad.ways:

            way = self.crossroad.ways[way_id]
            way_data = {
                "name" : way.name,
                "junctions" : [str(junction.id) for junction in way.junctions],
                "channels" : None,
                "sidewalks" : None,
                "islands" : None
            }
            
            # Channels handling
            channels = []
            for channel in way.channels:
                channels.append({
                    "type": channel.__class__.__name__,
                    "direction": channel.direction
                })
            way_data["channels"] = channels

            # Sidewalks handling
            sidewalks_ids = []
            for sidewalk in way.sidewalks:
                if sidewalk:
                    sidewalks_ids.append(str(sidewalk.id))
                    data["pedestrian_nodes"][sidewalk.id] = { "type" : "Sidewalk" }
                else:
                    sidewalks_ids.append(None)
            way_data["sidewalks"] = sidewalks_ids

            # Islands handling
            islands_ids = []
            for island in way.islands:
                if island:
                    islands_ids.append(str(island.id))
                    data["pedestrian_nodes"][island.id] = { "type" : "Island" }
                else:
                    islands_ids.append(None)
            way_data["islands"] = islands_ids

            data["ways"][way_id] = way_data

        # Junctions handling
        for junction_id in self.crossroad.junctions:

            junction = self.crossroad.junctions[junction_id]
            junction_data = {
                "x" : junction.x,
                "y" : junction.y,
                "type" : junction.type
            }

            # Attributes : cw_tactile_paving, pedestrian_nodes
            if "Crosswalk" in junction.type:

                # Tactile paving handling
                junction_data["cw_tactile_paving"] = junction.cw_tactile_paving

                # Pedestrian nodes handling
                junction_data["pedestrian_nodes"] = []
                for pedestrian_node in junction.pedestrian_nodes:
                    junction_data["pedestrian_nodes"].append(str(pedestrian_node.id))
                    data["pedestrian_nodes"][pedestrian_node.id] = { "type" : pedestrian_node.__class__.__name__ }

            # Attributes : ptl_sound
            if "Pedestrian_traffic_light" in junction.type:
                
                junction_data["ptl_sound"] = junction.ptl_sound

            # Attributes : tl_phase, tl_direction
            if "Traffic_light" in junction.type:
                
                junction_data["tl_phase"] = junction.tl_phase
                junction_data["tl_direction"] = junction.tl_direction

            data["junctions"][junction_id] = junction_data

        # Branches handling
        for branch in self.crossroad.branches:

            branch_data = {
                "angle" : branch.angle,
                "direction_name" : branch.direction_name,
                "street_name" : branch.street_name, 
                "ways" : [way.id for way in branch.ways],
                "crossing" : {
                    "crosswalks" : [str(crosswalk.id) for crosswalk in branch.crossing.crosswalks] if branch.crossing is not None else None
                }
            }

            data["branches"][branch.number] = branch_data

        return(json.dumps(data, ensure_ascii=False))

    def getGeoJSON(self):
        features = []

        # Crossroad general
        features.append(Feature(geometry=Point([self.crossroad.center["x"], self.crossroad.center["y"]]), properties={
            "id" : None,
            "type" : "crossroads"
        }))

        # Crossroad branch 
        branches_ways = []
        for branch in self.crossroad.branches:
            for way in branch.ways:
                n1 = way.junctions[0]
                n2 = way.junctions[1]
                features.append(Feature(geometry=LineString([(n1.x, n1.y), (n2.x, n2.y)]), properties={
                    "id" : str(branch.number),
                    "osm_node_ids" : [str(n1.id), str(n2.id)],
                    "osm_way_id" : str(way.osmid[0]),
                    "type" : "branch",
                    "name" : way.name,
                    "lanes" : [{"type" : channel.__class__.__name__, "direction" : channel.direction} for channel in way.channels],
                    "left_sidewalk" : str(way.sidewalks[0].id) if way.sidewalks[0] else None,
                    "right_sidewalk" : str(way.sidewalks[1].id) if way.sidewalks[1] else None,
                    "left_island" : str(way.islands[0].id) if way.islands[0] else None,
                    "right_island" : str(way.islands[1].id) if way.islands[1] else None
                }))
                branches_ways.append(way)
        
        # Crossroad ways
        for way in self.crossroad.ways.values():
            if way not in branches_ways:
                n1 = way.junctions[0]
                n2 = way.junctions[1]
                features.append(Feature(geometry=LineString([(n1.x, n1.y), (n2.x, n2.y)]), properties={
                    "id" : str(way.id),
                    "osm_node_ids" : [str(n1.id), str(n2.id)],
                    "osm_way_id" : str(way.osmid[0]),
                    "type" : "way",
                    "name" : way.name,
                    "lanes" : [{"type" : channel.__class__.__name__, "direction" : channel.direction} for channel in way.channels],
                    "left_sidewalk" : str(way.sidewalks[0].id) if way.sidewalks[0] else None,
                    "right_sidewalk" : str(way.sidewalks[1].id) if way.sidewalks[1] else None,
                    "left_island" : str(way.islands[0].id) if way.islands[0] else None,
                    "right_island" : str(way.islands[1].id) if way.islands[1] else None
                }))

        # Single crosswalks
        crosswalks = []
        for junction in self.crossroad.junctions.values():
            if "Crosswalk" in junction.type:
                crosswalks.append(junction)
        for crosswalk in crosswalks:
            features.append(Feature(geometry=Point([crosswalk.x, crosswalk.y]), properties={
                "id" : str(crosswalk.id),
                "osm_node_id" : str(crosswalk.id),
                "type" : "crosswalk",
                "tactile_paving" : crosswalk.cw_tactile_paving,
                "pedestrian_traffic_light" : "yes" if "Pedestrian_traffic_light" in crosswalk.type else "no",
                "pedestrian_traffic_light:sound" : crosswalk.ptl_sound if "Pedestrian_traffic_light" in crosswalk.type else "unknown"
            }))

        # Crossings 
        for branch in self.crossroad.branches:
            crossing = branch.crossing
            if crossing is None:
                continue
            crosswalks = crossing.crosswalks
            geom = None
            id = None
            if len(crosswalks) > 1:
                id = ";".join(map(str,[crosswalks[i].id for i in range(len(crosswalks))]))
                geom = LineString([(crosswalks[i].x, crosswalks[i].y) for i in range(len(crosswalks))])
            else:
                id = str(crosswalks[0].id)
                geom = Point([crosswalks[0].x, crosswalks[0].y])
            features.append(Feature(geometry=geom, properties={
                "id" : str(id),
                "osm_node_ids" : [str(crosswalk.id) for crosswalk in crosswalks],
                "type" : "crossing",
                "branch": branch.number
            }))

        return(dumps(FeatureCollection(features)))