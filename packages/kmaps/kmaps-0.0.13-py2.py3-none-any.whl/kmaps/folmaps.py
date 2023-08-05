"""Folium module."""

import random
import string
import folium
import os

class Map(folium.Map):
    """Class 'Map'.

    Args:
        folium (_type_): Map object from folium.
    """
    def __init__(self, location = [37.5, 127], zoom_start = 8, **kwargs): 
        """Create a Map.

        Args:
            location (list, optional): A coordinate representing the center of the map. Defaults to `[37.5, 127]`
            zoom_start (int, optional): Zoom level. Defaults to 8
        """            
        if 'scroll_wheel_zoom' not in kwargs:
            kwargs['scroll_wheel_zoom'] = True
        super().__init__(location = location, zoom_start = zoom_start, **kwargs) # inherited from the parent, in this case, ipyleaflet


    def add_layer(self, layer):
        """Adds a layer to the map.

        Args:
            layer (TileLayer): A TileLayer instance.
        """
        layer.add_to(self)


    def add_layer_control(self, **kwargs):
        """Add a layer control panel to the map.
        """        
        folium.LayerControl().add_to(self)


    def add_geojson(self, data, name = 'GeoJSON', **kwargs):
        """Add a geojson file to the map (folium version).

        Args:
            data (str): A name of the geojson file.
            name (str, optional): A layer name of the geojson file to be displayed on the map. Defaults to 'GeoJSON'.
        """     
        folium.GeoJson(data, name = name).add_to(self)
    
    def add_shp(self, data, name = 'Shapefile', **kwargs):
        """Add a ESRI shape file to the map (folium version).

        Args:
            data (str): A name of the shape file.
            name (str, optional): A layer name of the shape file to be displayed on the map. Defaults to 'Shapefile'.
        """
        import geopandas as gpd
        gdf = gpd.read_file(data)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, name = name, **kwargs)
    

    def add_tile_layer(self, url, name, attr = 'Tile', **kwargs):
        """Add a tile layer to the map.

        Args:
            url (str): xyz url of the tile layer.
            name (str): A name of the layer that would be displayed on the map.
            attr (str, optional): A name of the attribution. Defaults to 'Tile'.
        """        
        tile_layer = folium.TileLayer(
            tiles = url,
            name = name,
            attr = attr,
            **kwargs
        )

        self.add_child(tile_layer)


    def add_basemap(self, basemap = 'roadmap', **kwargs):
        """Add a base map to the map.

        Args:
            basemap (str): xyz url of the base map.

        Raises:
            ValueError: Error message will be raised if the url is not available.
        """
        
        import xyzservices.providers as xyz

        if basemap.lower() == 'roadmap':
            url = 'http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}'
            self.add_tile_layer(url, name = basemap, **kwargs)
        elif basemap.lower() == 'satellite':
            url = 'http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}'
            self.add_tile_layer(url, name = basemap, **kwargs)
        else:
            try:
                basemap = eval(f'xyz.{basemap}')
                url = basemap.build_url()
                attribution = basemap.attribution
                self.add_tile_layer(url, name = basemap, attr = attribution, **kwargs)
            except:
                raise ValueError(f'{basemap} is not found')


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


    def to_html(self, outfile=None, **kwargs):
        """Exports a map as an HTML file.

        Args:
            outfile (str, optional): File path to the output HTML. Defaults to None.

        Raises:
            ValueError: If it is an invalid HTML file.

        Returns:
            str: A string containing the HTML code.
        """

        if outfile is not None:
            if not outfile.endswith(".html"):
                raise ValueError("The output file extension must be html.")
            outfile = os.path.abspath(outfile)
            out_dir = os.path.dirname(outfile)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            self.save(outfile, **kwargs)
        else:
            outfile = os.path.abspath(generate_random_string(3) + ".html")
            self.save(outfile, **kwargs)
            out_html = ""
            with open(outfile) as f:
                lines = f.readlines()
                out_html = "".join(lines)
            os.remove(outfile)
            return out_html




def generate_random_string(length, upper = False, digit = False, punc = False):
    """Generates a random string of a given length.

    Args:
        length (int): A length of the string.
        upper (bool, optional): Whether you would like to contain upper case alphabets in your string pool or not. Defaults to False.
        digit (bool, optional): Whether you would like to contain digits in your string pool or not. Defaults to False.
        punc (bool, optional): Whether you would like to contain punctuations in your string pool or not. Defaults to False.

    Returns:
        str: Generated random string.
    """
    chars = string.ascii_lowercase
    if upper:
        chars += string.ascii_uppercase
    if digit:
        chars += string.digits
    if punc:
        chars += string.punctuation
    
    result_str = ''.join(random.choice(chars) for i in range(length))
    return result_str