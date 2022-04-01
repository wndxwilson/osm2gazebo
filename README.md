# osm2gazebo

This package converts the geospatial data from OpenStreetMap to a SDF world usable by gazebo

## 1 Setup
Install python dependencies
 ```
    pip install osmnx
    pip install networkx
    pip install numpy
```

## 2 Usage
```
usage: osm2gazebo.py [-h] [-f FILENAME] [-s SCALE]

Parameters for osm2gazebo

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Name of the files generated
  -s SCALE, --scale SCALE
                        Scale of the world generated

```

Generates 3 files for the multi-robot-sim
1. yaml file : containing information of the world generated
2. networkx gpickle file : node graph of the world generated
3. SDF file : information about the world for Gazebo

## Acknowledgements
The world generation is based on https://github.com/osrf/gazebo_osm