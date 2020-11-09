import pandas as pd  # provides interface for interacting with tabular data
import geopandas as gpd  # combines the capabilities of pandas and shapely for geospatial operations
from shapely.geometry import Point, Polygon, MultiPolygon  # for manipulating text data into geospatial shapes
from shapely import wkt  # stands for "well known text," allows for interchange across GIS programs
import rtree  # supports geospatial join
import os
import fnmatch
import matplotlib.pyplot as plt
import descartes
import numpy as np


def points_from_polygons(polygons, crs):
    '''
    Purpose: takes polygon geometry and converts into points that are saved as a new geometry in a new GeoDataFrame
    --------
    
    Inputs:
    ------
        - polygons : .geometry object (polygon or multipolygon)
        - crs : numeric field for type of coordinates to use in the new points object (options 4326, 3035, etc - see GeoPandas
                documentation for others)
    Returns:
    --------
        - points: new GeoDataFrame containing pairs of points from polygons
    '''
    points = []
    x = []
    y = []
    for mpoly in polygons:
        if isinstance(mpoly, MultiPolygon):
            polys = list(mpoly)
        else:
            polys = [mpoly]
        for polygon in polys:
            for point in polygon.exterior.coords:
                x.append(point[0])
                y.append(point[1])
            for interior in polygon.interiors:
                for point in interior.coords:
                    x.append(point[0])
                    y.append(point[1])
    points = gpd.GeoDataFrame(geometry = gpd.points_from_xy(x, y, crs =  crs))
    return points


def generate_grid(geom, width, height):
    '''
    Purpose: generate grid with equal-sized areas within bounds of a larger option 
    --------
    
    Inputs:
    ------
        - geom : .geometry object (polygon or multipolygon)
        - width : int, width of grid square or rectangle
        - height : int, height of grid square or rectangle
    Returns:
    --------
        - grid: new GeoDataFrame with grid polygons as .geometry (grid object will be a rectangle of grids between the 
                min, max x and y points in the geom input object
    '''
    xmin,ymin,xmax,ymax = geom.total_bounds
    cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), width))
    rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), height))
    rows.reverse()

    polygons = []
    for x in cols:
        for y in rows:
            polygons.append( Polygon([(x,y), (x+width, y), (x+width, y-height), (x, y-height)]) )

    grid = gpd.GeoDataFrame({'geometry':polygons})
    return grid
    
    
    