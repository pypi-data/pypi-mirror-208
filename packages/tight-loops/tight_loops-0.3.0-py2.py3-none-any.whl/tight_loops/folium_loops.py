import folium
import os
import geemap.foliumap as geemap



class Map(folium.Map):
    """A folium map."""
    def __init__(self, location=[45.5236, -122.6750], zoom_start=13, **kwargs):
       
        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True
        super().__init__(location=location, zoom_start=zoom_start, **kwargs)

    def add_tile_layer(self, url, name, attribution, **kwargs):
        """Adds a tile layer to the map."""
        tile_layer = folium.TileLayer(tiles=url, name=name, attr=attribution, **kwargs)
        tile_layer.add_to(self)
    
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
                self.add_tile_layer(url, name=basemap.name, attr=attribution, **kwargs)
            except:
                raise ValueError("Invalid basemap name.")
            
    def add_geojson(self, data, **kwargs):
        """Adds a GeoJSON layer to the map."""
        import json
        with open(data, "r") as f:
            data = json.load(f)
        geojson = folium.GeoJson(data=data, **kwargs)
        geojson.add_to(self)

    def add_shp(self, data, **kwargs):
        """Adds a Shapefile layer to the map."""
        import geopandas as gpd
        import json
        gdf = gpd.read_file(data)
        data = json.loads(gdf.to_json())
        geojson = folium.GeoJson(data=data, **kwargs)
        geojson.add_to(self)

    def add_layer_control(self):
        """Adds layer control to the map."""
        layer_ctrl = False
        for item in self.to_dict()["children"]:
            if item.startswith("layer_control"):
                layer_ctrl = True
                break
        if not layer_ctrl:
            folium.LayerControl().add_to(self)


    def to_html(self, filename=None, **kwargs):
        """Exports a map as an HTML file.

        Args:
            filename (str, optional): File path to the output HTML. Defaults to None.

        Raises:
            ValueError: If it is an invalid HTML file.

        Returns:
            str: A string containing the HTML code.
        """


        if filename is not None:
            if not filename.endswith(".html"):
                raise ValueError("The output file extension must be html.")
            filename = os.path.abspath(filename)
            out_dir = os.path.dirname(filename)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            self.save(filename, **kwargs)

    def to_streamlit(
        self,
        width=None,
        height=600,
        scrolling=False,
        add_layer_control=True,
        bidirectional=False,
        **kwargs,
    ):
        """Renders `folium.Figure` or `folium.Map` in a Streamlit app. This method is a static Streamlit Component, meaning, no information is passed back from Leaflet on browser interaction.

        Args:
            width (int, optional): Width of the map. Defaults to None.
            height (int, optional): Height of the map. Defaults to 600.
            scrolling (bool, optional): Whether to allow the map to scroll. Defaults to False.
            add_layer_control (bool, optional): Whether to add the layer control. Defaults to True.
            bidirectional (bool, optional): Whether to add bidirectional functionality to the map. The streamlit-folium package is required to use the bidirectional functionality. Defaults to False.

        Raises:
            ImportError: If streamlit is not installed.

        Returns:
            streamlit.components: components.html object.
        """

        try:
            import streamlit.components.v1 as components

            if add_layer_control:
                self.add_layer_control()

            if bidirectional:
                from streamlit_folium import st_folium

                output = st_folium(self, width=width, height=height)
                return output
            else:
                # if responsive:
                #     make_map_responsive = """
                #     <style>
                #     [title~="st.iframe"] { width: 100%}
                #     </style>
                #     """
                #     st.markdown(make_map_responsive, unsafe_allow_html=True)
                return components.html(
                    self.to_html(), width=width, height=height, scrolling=scrolling
                )

        except Exception as e:
            raise Exception(e)
