import osmnx as ox
import networkx as nx
import numpy as np
from sdfGenerator import GetSDF
from catmull_rom_spline import catmull_rom
import yaml
import argparse

# Get points in respect to x,y
def getPoints(coords,center):
    dist = ox.distance.great_circle_vec(coords[:,1], coords[:,0], center['lat'], center['lon'])
    bearing = np.radians(ox.bearing.calculate_bearing(coords[:,1], coords[:,0], center['lat'], center['lon']))
    points = np.array([[-r*np.sin(d),-r*np.cos(d)] for r,d in zip(dist,bearing)])*scale
    return points


# Params
scale = 0.10
road_width = 0.65
file_name = "osm2gazebo"

parser = argparse.ArgumentParser(description='Parameters for osm2gazebo')
parser.add_argument("-f", "--filename", type= str,help="Name of the files generated",
                    required=False)
parser.add_argument("-s", "--scale", type= float,help="Scale of the world generated",
                    required=False)
args = parser.parse_args()

if args.filename:
    file_name = args.filename
if args.scale:
    scale = args.scale

# Load osm map
G = ox.io.load_graphml('map_botanic.osm')
routes = ox.utils_graph.graph_to_gdfs(G, nodes=False)

# Get coords of all the nodes, lon lat
node_coords = np.array([[G.nodes[i]['x'],G.nodes[i]['y']] for i in G.nodes])

# Center point
center = {
    'lat' : np.median(node_coords[:,1]),
    'lon' : np.median(node_coords[:,0])
}


G_converted = nx.Graph()
for node in G.nodes():
    coords = [(G.nodes[node]['x'],G.nodes[node]['y'])]
    points = getPoints(np.array(coords),center)
    G_converted.add_node(node,x = points[0][0],y=points[0][1])


# Generate SDF file
sdfFile = GetSDF()
sdfFile.addSphericalCoords(center['lat'], center['lon'])
sdfFile.includeModel("sun")
sdfFile.includeModel("ground_plane")

print ('|')
print ('|-----------------------------------')
print ('| Number of Roads: ' + str(len(routes['geometry'])))
print ('|-----------------------------------')

i = 0
for index, route in zip(routes.index,routes['geometry']):
    road_name = "road_{}".format(i)
    sdfFile.addRoad(road_name)
    sdfFile.setRoadWidth(0.3, road_name)

    points = getPoints(np.array(route.coords),center)
    xData = points[:,0]
    yData = points[:,1]

    # Add edge to graph
    G_converted.add_edge(index[0],index[1],points=points)
    
    if len(xData) < 3:
        for j in np.arange(len(xData)):
            sdfFile.addRoadPoint([xData[j], yData[j], 0], road_name)

    else:
        x, y = catmull_rom(xData, yData, 10)

        for point in range(len(x)):
            sdfFile.addRoadPoint([x[point], y[point], 0], road_name)

    i += 1
print ('|')
print ('|-----------------------------------')
print ('| Generating the SDF world file...')
sdf_path = file_name+".sdf"
sdfFile.writeToFile(sdf_path)

print ('|')
print ('|-----------------------------------')
print ('| Generating the pickle world file...')
gpickle_path = file_name+".gpickle"
nx.write_gpickle(G_converted, gpickle_path)

print ('|')
print ('|-----------------------------------')
print ('| Generating the yaml file...')

yaml_data = {
    "sdf_file" : sdf_path,
    "gpickle_file" : gpickle_path,
    "scale" : scale,
    "center" : {'lat': float(center['lat']), 'lon':float(center['lon'])}
}

yaml_path = file_name+".yaml"
with open(yaml_path, 'w') as outfile:
    yaml.dump(yaml_data, outfile, default_flow_style=False)