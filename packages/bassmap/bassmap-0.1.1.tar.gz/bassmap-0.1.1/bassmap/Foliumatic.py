import requests
import zipfile
import io
import os
import json
import folium
import geopandas as gpd

import folium

class Foliumatic(folium.Map):
    
    def __init__(self):
        self.map = folium.Map()
        
    def __init__(self, lat=0, lon=0, zoom_start=2):
        self.map = folium.Map(location=[lat, lon], zoom_start=zoom_start)

    def add_tile_layers(self, tile_layers):
        for tile_name, tile_url in tile_layers.items():
            folium.TileLayer(tiles=tile_url, name=tile_name).add_to(self.map)

        folium.LayerControl().add_to(self.map)

        return self.map

    def add_basemap(self, basemap_name):
        """
        Adds a basemap to the map using a predefined URL template for XYZ tile services.
        
        Parameters:
        basemap_name (str): The name of the basemap to add.
        """
        basemap_urls = {
            'OpenStreetMap': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'Mapbox Satellite': 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=<your-access-token>',
            'Esri.WorldImagery': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'OpenTopoMap': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            'Esri.NatGeoWorldMap': 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            'CartoDB.Positron': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        }
        
        url_template = basemap_urls.get(basemap_name)
        
        if url_template is None:
            raise ValueError(f'Unknown basemap name: {basemap_name}')
        
        new_layer = folium.TileLayer(
            tiles=url_template,
            name=basemap_name,
            attr=' '.join([basemap_name, 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors']),
            overlay=True,
            control=True
        )
        self.add_child(new_layer)

    def add_shp(self, data, **kwargs):
        gdf = gpd.read_file(data)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)

    def add_geojson(self, geojson_data):
        """
        Adds a GeoJSON layer to the map.
        
        Parameters:
        geojson_data (str or dict): The GeoJSON file path, HTTP URL or dictionary to add to the map.
        """
        if isinstance(geojson_data, str):
            # Load GeoJSON from file or HTTP URL
            if geojson_data.startswith(('http://', 'https://')):
                response = requests.get(geojson_data)
                geojson_layer = folium.GeoJson(data=response.content.decode())
            else:
                with open(geojson_data, 'r') as f:
                    geojson_layer = folium.GeoJson(data=json.load(f))
        elif isinstance(geojson_data, dict):
            # Load GeoJSON from dictionary
            geojson_layer = folium.GeoJson(data=geojson_data)
        else:
            raise ValueError('Invalid input format. Must be GeoJSON file path, HTTP URL or dictionary.')
            
        geojson_layer.add_to(self)
    
    def __init__(self, **kwargs):
        """
        Initializes a new instance of the Foliumatic class, which inherits from the folium.Map class.

        Args:
            **kwargs: Keyword arguments that can be passed to the folium.Map constructor.
        """
        super().__init__(**kwargs)
        self.bounds = []

    def add_vector(self, vector_data):
        """
        Adds vector data to the map.

        The supported data types include file paths, URLs, GeoJSON dictionaries, and GeoDataFrames.

        Args:
            vector_data: The vector data to add to the map. Can be a file path, a URL, a GeoJSON dictionary, or a GeoDataFrame.

        Raises:
            ValueError: If the input data type is not supported or the shapefile is missing necessary files.
        """
        if isinstance(vector_data, str):
            # vector_data is a file path or a URL
            if vector_data.startswith('http'):
                # vector_data is a URL
                r = requests.get(vector_data)
                if zipfile.is_zipfile(io.BytesIO(r.content)):
                    # vector_data is a zipped shapefile
                    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                        filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending) ]
                        if not filenames:
                            raise ValueError("Zip file does not contain .shp file.")
                        if len(filenames) < 4:
                            raise ValueError("Zip file does not contain all necessary files for a shapefile (shp, dbf, shx, prj).")
                        # Read the shapefile using geopandas and convert it to GeoJSON
                        gdf = gpd.read_file(io.BytesIO(z.read(filenames[0])))
                        geojson = gdf.to_crs(epsg='4326').to_json()
                else:
                    # vector_data is a GeoJSON URL
                    geojson = requests.get(vector_data).json()
            else:
                # vector_data is a file path
                if zipfile.is_zipfile(vector_data):
                    # vector_data is a zipped shapefile
                    with zipfile.ZipFile(vector_data) as z:
                        filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending) ]
                        if not filenames:
                            raise ValueError("Zip file does not contain .shp file.")
                        if len(filenames) < 4:
                            raise ValueError("Zip file does not contain all necessary files for a shapefile (shp, dbf, shx, prj).")
                        # Read the shapefile using geopandas and convert it to GeoJSON
                        gdf = gpd.read_file(io.BytesIO(z.read(filenames[0])))
                        geojson = gdf.to_crs(epsg='4326').to_json()
                else:
                    # vector_data is a file path to a GeoJSON file or a shapefile
                    gdf = gpd.read_file(vector_data)
                    geojson = gdf.to_crs(epsg='4326').to_json()
        elif isinstance(vector_data, dict):
            # vector_data is a GeoJSON dictionary
            geojson = vector_data
        elif isinstance(vector_data, gpd.GeoDataFrame):
            # vector_data is a GeoDataFrame
            geojson = vector_data.to_crs(epsg='4326').to_json()
        else:
            raise ValueError("Invalid input data type. Supported data types include file paths, URLs, GeoJSON dictionaries, and GeoDataFrames.")

        folium.GeoJson(
            geojson,
            name="geojson"
        ).add_to(self)

        folium.LayerControl().add_to(self)