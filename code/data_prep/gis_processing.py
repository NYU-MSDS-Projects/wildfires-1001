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