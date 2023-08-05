"""Main module."""

import random
import ipyleaflet
import ipywidgets as widgets
from ipyleaflet import WidgetControl

class Map(ipyleaflet.Map):
    def __init__(self, center=(0,0), zoom=2, **kwargs) -> None:

        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True
        super().__init__(center=center, zoom=zoom, **kwargs)

        if "layers_control" not in kwargs:
            kwargs["layers_control"] = True

        if kwargs["layers_control"]:
            self.add_layers_control()

        if "fullscreen_control" not in kwargs:
            kwargs["fullscreen_control"] = True
        
        if kwargs["fullscreen_control"]:
            self.add_fullscreen_control()
        
        if "add_toolbar" not in kwargs:
            kwargs["add_toolbar"] = True

        if kwargs["add_toolbar"]:
            self.add_toolbar()

    
    def add_search_control(self, url = 'https://nominatim.openstreetmap.org/search?format=json&q={s}', position="topleft", **kwargs):
        """Adds a search control to the map."""
        search_control = ipyleaflet.SearchControl(url=url, position=position, **kwargs)
        self.add_control(search_control)
        return search_control
    
    def add_draw_control(self, **kwargs):
        """Adds a draw control to the map."""
        draw_control = ipyleaflet.DrawControl(**kwargs)
        draw_control.polyline =  {
            "shapeOptions": {
                "color": "#6bc2e5",
                "weight": 8,
                "opacity": 1.0
            }
        }
        draw_control.polygon = {
            "shapeOptions": {
                "fillColor": "#6be5c3",
                "color": "#6be5c3",
                "fillOpacity": 1.0
            },
            "drawError": {
                "color": "#dd253b",
                "message": "Oups!"
            },
            "allowIntersection": False
        }
        draw_control.circle = {
            "shapeOptions": {
                "fillColor": "#efed69",
                "color": "#efed69",
                "fillOpacity": 1.0
            }
        }
        draw_control.rectangle = {
            "shapeOptions": {
                "fillColor": "#fca45d",
                "color": "#fca45d",
                "fillOpacity": 1.0
            }
        }
        self.add_control(draw_control)
        return draw_control

    def add_layers_control(self, position= "topright", **kwargs):
        """Adds a layers control to the map."""
        layers_control = ipyleaflet.LayersControl(position=position, **kwargs)
        self.add_control(layers_control)
        return layers_control
    
    def add_fullscreen_control(self, **kwargs):
        """Adds a fullscreen control to the map."""
        fullscreen_control = ipyleaflet.FullScreenControl(**kwargs)
        self.add_control(fullscreen_control)
        return fullscreen_control
    
    def add_tile_layer(self, url, name, attribution, **kwargs):
        """Adds a tile layer to the map."""
        tile_layer = ipyleaflet.TileLayer(url=url, name=name, attribution=attribution, **kwargs)
        self.add_layer(tile_layer)
        return tile_layer
    
    def add_basemap(self, basemap, **kwargs):
        
        import xyzservices.providers as xyz

        if basemap.lower() == "roadmap":
            url = "http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}"
            self.add_tile_layer(url, name=basemap, attribution="Google")

        elif basemap.lower() == "satellite":
            url = "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            self.add_tile_layer(url, name=basemap, attribution="Google")

        else:
            try:
                basemap = eval(f"xyz.{basemap}")
                url = basemap.build_url()
                attribution = basemap.attribution
                self.add_tile_layer(url, name=basemap.name, attribution=attribution, **kwargs)
            except:
                raise ValueError("Invalid basemap name.")
            
    def add_geojson(self, data, **kwargs):
        """Adds a GeoJSON layer to the map."""
        import json

        if isinstance(data, str):
        
            with open(data, "r") as f:
                data = json.load(f)

        elif not isinstance(data, dict):
            raise ValueError("data must be a GeoJSON dictionary or a GeoJSON file path.")

        geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
        self.add_layer(geojson)
    
    # def add_shp(self, data, **kwargs):
    #     """Adds a Shapefile layer to the map."""
    #     import geopandas as gpd
    #     import json
    #     gdf = gpd.read_file(data)
    #     data = json.loads(gdf.to_json())
    #     geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
    #     self.add_layer(geojson)

    def add_shp(self, data, name='Shapefile', **kwargs):
        """Adds a Shapefile layer to the map.

        Args:
            data (str): The path to the Shapefile.
        """
        import geopandas as gpd

        gdf = gpd.read_file(data)
        
        if gdf.crs.to_epsg() != 4326:
            
            gdf = gdf.to_crs(epsg=4326)
            geojson = gdf.__geo_interface__
        
        else:
            geojson = gdf.__geo_interface__

        self.add_geojson(geojson, name=name, **kwargs)
    
    def add_vector(self, data, **kwargs):
        """Adds a vector layer to the map."""
        import geopandas as gpd
        import json
        gdf = gpd.read_file(data)
        data = json.loads(gdf.to_json())
        geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
        self.add_layer(geojson)
    
    def add_raster(self, url, name='Raster', fit_bounds=True, **kwargs):
        """Adds a raster layer to the map.

            Args:
                url (str): The URL of the raster.
                name (str): The name of the raster.
                fit_bounds (bool): Whether to fit the map bounds to the raster.
        """
        import httpx

        titiler_endpoint = "https://titiler.xyz" 

        r = httpx.get(
            f"{titiler_endpoint}/cog/info",
            params = {
                "url": url,
            }
        ).json()

        bounds = r["bounds"]

        r = httpx.get(
            f"{titiler_endpoint}/cog/tilejson.json",
            params = {
                "url": url,
            }
        ).json()

        tile = r["tiles"][0]

        self.add_tile_layer(url=tile, name=name, attribution="raster", **kwargs)

        if fit_bounds:
            bbox = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            self.fit_bounds(bbox)

    # def add_local_raster(self, filename, name='Local Raster', **kwargs):
    #     try:
    #         import localtilesserver
    #     except ImportError:
    #         raise ImportError("Please install localtilesserver: pip install localtilesserver")
        
    def opacity_slider(self, value=0.1, min=0, max=1, position="bottomright"):
        """Adds an opacity slider to the map.
        
        Args:   
            value (float): The initial value of the slider.
            min (float): The minimum value of the slider.
            max (float): The maximum value of the slider.
            position (str): The position of the slider.
        """
        
        slider = widgets.FloatSlider(value=value, min=min ,max=max)
        widgets.jslink((self.layers[1], 'opacity'), (slider, 'value'))
        control = WidgetControl(widget=slider, position=position)
        self.add_control(control)

    def add_image(self, url, width, height, position="bottomleft"):
        """Adds an image to the map.
        
        Args:
            url (str): The URL of the image.
            width (str): The width of the image.
            height (str): The height of the image.
            position (str): The position of the image.
        """

        widget = widgets.HTML(value=f"<img src={url} width='{width}' height='{height}'>")
        control = WidgetControl(widget=widget, position = position)
        self.add_control(control)

    def add_toolbar(self, position="topright"):
        

        widget_width = "250px"
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left

        toolbar_button = widgets.ToggleButton(
            value=False,
            tooltip="Toolbar",
            icon="wrench",
            layout=widgets.Layout(width="28px", height="28px", padding=padding),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )

        toolbar = widgets.HBox([toolbar_button])

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [toolbar_button, close_button]
            else:
                toolbar.children = [toolbar_button]
                
        toolbar_button.observe(toolbar_click, "value")

        def close_click(change):
            if change["new"]:
                toolbar_button.close()
                close_button.close()
                toolbar.close()
                
        close_button.observe(close_click, "value")

        rows = 2
        cols = 2
        grid = widgets.GridspecLayout(rows, cols, grid_gap="0px", layout=widgets.Layout(width="65px"))

        icons = ["folder-open", "map", "bluetooth", "area-chart"]

        for i in range(rows):
            for j in range(cols):
                grid[i, j] = widgets.Button(description="", button_style="primary", icon=icons[i*rows+j], 
                                            layout=widgets.Layout(width="28px", padding="0px"))
                
        toolbar = widgets.VBox([toolbar_button])

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
            else:
                toolbar.children = [toolbar_button]
                
        toolbar_button.observe(toolbar_click, "value")



        output = widgets.Output()
        output_ctrl = WidgetControl(widget=output, position="bottomright")
        self.add_control(output_ctrl)


        basemap = widgets.Dropdown(

            options = ["Satellite", "Roadmap"],
            value = None,
            description = "Basemap",
            style = {"description_width": "initial"},
            layout=widgets.Layout(width="250px")
        )
        
        
        basemap_ctrl = WidgetControl(widget=basemap, position="topright")

        def change_basemap(change):
            if change['new']:
                with output:
                    print(basemap.value)
                self.add_basemap(basemap.value)

        basemap.observe(change_basemap, names="value")

        def tool_click(b):
            with output:
                print(f"{b.icon} clicked")

                if b.icon == "map":
                    if basemap_ctrl not in self.controls:
                        self.add(basemap_ctrl)
        for i in range(rows):
            for j in range(cols):
                tool = grid[i, j]
                tool.on_click(tool_click)

        toolbar_ctrl = ipyleaflet.WidgetControl(widget=toolbar, position=position)

        self.add_control(toolbar_ctrl)

    def csv_to_shp(self, data, output):
        import pandas as pd
        import geopandas as gpd
        from shapely.geometry import Point

        df = pd.read_csv(data)

        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        gdf = gdf.set_crs(epsg=4326)
        gdf.to_file(output, driver='ESRI Shapefile')

        self.add_shp(output)
    

    def grouping_points(self, data):
        import pandas as pd
        from ipyleaflet import Marker, MarkerCluster
        import ipywidgets as widgets

        df = pd.read_csv(data)

        markers = []

        for index, row in df.iterrows():
            name = row['name']
            latitude = row['latitude']
            longitude = row['longitude']
            marker = Marker(location=(latitude, longitude))

            popup_content = widgets.HTML()
            popup_content.value = f"<b>Name:</b> {name}<br><b>Latitude:</b> {latitude}<br><b>Longitude:</b> {longitude}"
            marker.popup = popup_content

            markers.append(marker)


        marker_cluster = MarkerCluster()

        marker_cluster = MarkerCluster(markers=markers)

        self.add_layer(marker_cluster)

def contour_tif_box(
    i,
    output,
    interval=200,
    base=0,
    smooth=9,
    tolerance=10,
    ):

    import os
    import whitebox

    wbt = whitebox.WhiteboxTools()

    i = os.path.abspath(i)
    output = os.path.abspath(output)

    wbt.contours_from_raster(i=i, output=output, interval=interval, base=base, smooth=smooth, tolerance=tolerance)

# ----------------------------------------------------------------GDAL Contour Function----------------------------------------------------------------
# from osgeo import gdal, ogr, osr
# import os

# def contour_tif(input_file, output_file="new_contours/output_contours.shp", contourInterval=200.0, contourBase=0.0, fixedLevelCount=[], useNoData=False, noDataValue=0, idField=0, elevField=1):

#     """
#     This function creates contour lines from a DEM file. The function uses the GDAL library to open the DEM file and
#     extract the elevation values. The function then uses the GDAL library to create a vector file containing the
#     contour lines. The function uses the OGR library to create the vector file and add the contour lines to it.

#     :param input_file: The input DEM file.
#     :param output_file: The output vector file containing the contour lines.
#     :param interval: The contour interval.
#     :param base: The base contour.
#     :param fixedLevels: A list of fixed contour levels.
#     :param useNoData: A boolean value indicating whether to use the NoData value.
#     :param useZ: A boolean value indicating whether to use the Z value.
#     :param idField: The field number for the ID field.
#     :param elevField: The field number for the elevation field.
#     """

#     # Open the DEM file using the GDAL library
#     input_file = 'Smokies_DEM.tif'
#     ds = gdal.Open(input_file)

#     # Get the geotransform information from the DEM
#     transform = ds.GetGeoTransform()

#     # Define the output file format and options
#     driver = ogr.GetDriverByName('ESRI Shapefile')
#     output_file = output_file
#     output_dir = os.path.dirname(output_file)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     output_ds = driver.CreateDataSource(output_file)

#     # Create the output layer and add a field for elevation values
#     contour_layer = output_ds.CreateLayer('contours', srs=osr.SpatialReference().CloneGeogCS())
#     contour_field = ogr.FieldDefn('elev', ogr.OFTReal)
#     contour_layer.CreateField(contour_field)


#     band = ds.GetRasterBand(1)
#     gdal.ContourGenerate(
#         band, 
#         contourInterval=contourInterval, 
#         contourBase=contourBase, 
#         fixedLevelCount=fixedLevelCount, 
#         useNoData=useNoData, 
#         noDataValue=noDataValue,
#         dstLayer=contour_layer, 
#         idField=idField, 
#         elevField=elevField
#         )
    
#     # Clean up the resources
#     ds = None
#     output_ds = None

    

def generate_random_string(length=15):
    """Generates a random string."""
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length)])
