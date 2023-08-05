"""Main module."""

import random
import string
import ipyleaflet
import ipywidgets as widgets
import pandas as pd
import geopandas as gpd
#import spopt
import os

#from spopt.locate import PMedian, simulated_geo_points

import xyzservices.providers as xyz

class Map(ipyleaflet.Map):
    """Class 'Map'
    """
    def __init__(self, center = [37.5, 127], zoom = 8, **kwargs):
        """Create a Map.

        Args:
            center (list, optional): A coordinate representing the center of the map. Defaults to `[37.5, 127]`
            zoom (int, optional): Zoom level. Defaults to 8
        """        
        if 'scroll_wheel_zoom' not in kwargs:
            kwargs['scroll_wheel_zoom'] = True
        super().__init__(center = center, zoom = zoom, **kwargs) # inherited from the parent, in this case, ipyleaflet
        
        if 'layers_control' not in kwargs:
            kwargs['layers_control'] = True
        
        if kwargs['layers_control']:
            self.add_layers_control()

        #self.add_states_dropdown()
        self.add_search_control()


    def add_states_dropdown(self, position = 'bottomright', **kwargs):
        """Add a dropdown widget to move to selected state to the map.

        Args:
            position (str, optional): Position of the widget. Defaults to 'bottomright'.
        """            
        states_list = [('Initial Location', self.center), 
            ('Alabama', [32.78, -86.83]), ('Alaska', [64.07, -152.28]), 
            ('Arizona', [34.27, -111.66]), ('Arkansas', [34.89, -92.44]),
            ('California', [37.18, -119.47]), ('Colorado', [39.00, -105.55]),
            ('Connecticut', [41.62, -72.73]), ('Delaware', [38.99, -75.51]),
            ('District of Columbia', [38.91, -77.01]), ('Florida', [28.63, -82.45]),
            ('Georgia', [32.64, -83.44]), ('Hawaii', [20.29, -156.37]),
            ('Idaho', [44.35, -114.61]), ('Illinois', [40.04, -89.20]),
            ('Indiana', [39.89, -86.28]), ('Iowa', [42.08, -93.50]),
            ('Kansas', [38.49, -98.38]), ('Kentucky', [37.53, -85.30]),
            ('Louisiana', [31.07, -92.00]), ('Maine', [45.37, -69.24]),
            ('Maryland', [39.06, -76.80]), ('Massachusetts', [42.26, -71.81]),
            ('Michigan', [44.35, -85.41]), ('Minnesota', [46.28, -94.31]),
            ('Mississippi', [32.74, -89.67]), 
            ('Montana', [47.05, -109.63]), ('Nebraska', [41.54, -99.80]),
            ('Nevada', [39.33, -116.63]), ('New Hampshire', [43.68, -71.58]),
            ('New Jersey', [40.19, -74.67]), ('New Mexico', [34.41, -106.11]),
            ('New York', [42.95, -75.53]), ('North Carolina', [35.56, -79.39]),
            ('North Dakota', [47.45, -100.47]), ('Ohio', [40.29, -82.79]),
            ('Oklahoma', [35.59, -97.49]), ('Oregon', [43.93, -120.56]),
            ('Pennsylvania', [40.88, -77.80]), ('Rhode Island', [41.68, -71.56]),
            ('South Carolina', [33.92, -80.90]), ('South Dakota', [44.44, -100.23]),
            ('Tennessee', [35.86, -86.35]), ('Texas', [31.48, -99.33]),
            ('Utah', [39.31, -111.67]), ('Vermont', [44.07, -72.67]),
            ('Virginia', [37.52, -78.85]), ('Washington', [47.38, -120.45]),
            ('West Virginia', [38.64, -80.62]), ('Wisconsin', [44.62, -89.99]),
            ('Wyoming', [43.00, -107.55])]
        states_dropdown = widgets.Dropdown(
            options = states_list,
            value = self.center,
            description = 'States',
            style = {'description_width': 'initial'}
        )

        states_control = ipyleaflet.WidgetControl(widget = states_dropdown, position = position)
        self.add(states_control)
        
        widgets.link((self, 'center'), (states_dropdown, 'value'))


    def add_base_dropdown(self, **kwargs):
        """Add a dropdown ipywidget that provides options for a basemap from xyz.services.
        """        
        output_widget = widgets.Output(layout={'border': '1px solid black'})
        output_widget.clear_output()
        basemap_ctrl = ipyleaflet.WidgetControl(widget=output_widget, position='bottomright')
        self.add_control(basemap_ctrl)

        dropdown = widgets.Dropdown(
            options = ["Topo", "ShadeRelief", "Gray"], 
            value=None,
            description='Basemap',
            )

        close_button = widgets.ToggleButton(
            value=True,
            tooltip="Open or close basemap selector",
            icon="desktop",
            button_style="primary",
            #layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )
        close_button
        
        h = widgets.VBox([close_button, dropdown])

        with output_widget:
            # if basemap_ctrl not in leaflet_map.controls:
            display(h)

        def change_basemap(change):
            if change["new"] == "Topo":
                self.add_basemap(basemap= "Esri.WorldTopoMap")
            if change["new"] == "ShadeRelief":
                self.add_basemap(basemap= "Esri.WorldShadedRelief")
            if change["new"] == "Gray":
                self.add_basemap(basemap= "Esri.WorldGrayCanvas")

        dropdown.observe(change_basemap, "value")

        def close_basemap(change):
            if change["new"] == True:
                output_widget.clear_output()
                with output_widget:
                    # if basemap_ctrl not in leaflet_map.controls:
                    display(h)
            else:
                output_widget.clear_output()
                with output_widget:
                    # if basemap_ctrl not in leaflet_map.controls:
                    display(close_button)

        close_button.observe(close_basemap, "value")


    def add_search_control(self, position = 'topleft', **kwargs):
        """Add a search control panel to the map.

        Args:
            position (str, optional): The location of the search control panel. Defaults to 'topleft'.
        """        
        if 'url' not in kwargs:
            kwargs['url'] = 'https://nominatim.openstreetmap.org/search?format=json&q={s}'
        
        search_control = ipyleaflet.SearchControl(position = position, **kwargs)
        self.add_control(search_control)


    def add_draw_control(self, position = 'topleft', **kwargs):
        """Add a draw control panel to the map.

        Args:
            position (str, optional): The location of the draw control panel. Defaults to 'topleft'.
        """        
        draw_control = ipyleaflet.DrawControl(position = position, **kwargs)
        self.add_control(draw_control)


    def add_layers_control(self, position = 'topright', **kwargs):
        """Add a layers control panel to the map.

        Args:
            position (str, optional): The location of the layers control panel. Defaults to 'topright'.
        """        
        layers_control = ipyleaflet.LayersControl(position = position, **kwargs)
        self.add_control(layers_control)


    def add_tile_layer(self, url, name, attribution = '', **kwargs):
        """Add a tile layer to the map.

        Args:
            url (str): xyz url of the tile layer.
            name (str): A name of the layer that would be displayed on the map.
            attribution (str, optional): A name of the attribution. Defaults to ''.
        """        
        tile_layer = ipyleaflet.TileLayer(
            url = url,
            name = name,
            attribution = attribution,
            **kwargs
        )
        self.add_layer(tile_layer)
    

    def add_basemap(self, url = xyz.Esri.WorldImagery.build_url(), basemap="Esri.WorldImagery", **kwargs):
        """Add a basemap from xyz.services

        Args:
            url (string, optional: URL to xyz.services map. Defaults to xyz.Esri.WorldImagery.build_url().
            basemap (str, optional): Name of the basemap on xyz.services. Defaults to "Esri.WorldImagery".

        Raises:
            ValueError: If basemap does not exist.
        """        
        try:
            basemap = eval(f"xyz.{basemap}")
            url = basemap.build_url()
            attribution = basemap.attribution
            b = self.add_tile_layer(url, name = basemap.name, attribution=attribution, **kwargs)
            return b

        except:
            raise ValueError(f"Basemap '{basemap}' not found.")


    def add_geojson(self, data, name = 'GeoJSON', **kwargs):
        """Add a geojson file to the map.

        Args:
            data (str): A name of the geojson file.
            name (str, optional): A layer name of the geojson file to be displayed on the map. Defaults to 'GeoJSON'.
        """        
        if isinstance(data, str):
            import json
            with open(data, 'r') as f:
                data = json.load(f)

        geojson = ipyleaflet.GeoJSON(data = data, name = name, **kwargs)
        self.add_layer(geojson)
    

    def add_shp(self, data, name = 'Shapefile', fit_bounds = True,  **kwargs):
        """Add a ESRI shape file to the map.

        Args:
            data (str): A name of the shape file.
            name (str, optional): A layer name of the shape file to be displayed on the map. Defaults to 'Shapefile'.
        """
        import geopandas as gpd
        gdf = gpd.read_file(data)

        # Access the geometry column
        geometry = gdf.geometry

        # Extract x and y coordinates
        x_coords = geometry.x
        y_coords = geometry.y

        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, name = name, **kwargs)

        # [[south, west], [north, east]]
        if fit_bounds:
            bbox = [[min(y_coords), min(x_coords)], [max(y_coords), max(x_coords)]]
            self.fit_bounds(bbox)


    def add_Weber(self, data, attribute, name = 'WeberPoint',  **kwargs):
        """Add the optimal location of the single-facility Weber problem on the map with the input shapefile.

        Args:
            data (GeoDataFrame): A geopandas GeoDataFrame. Must be a point file.
            attribute (str): A column name of the GeoDataFrame that contains the weight attribute 
            name (str, optional): A name of the weber ooint layer. Defaults to 'WeberPoint'.
        """        
        import geopandas as gpd
        gdf = gpd.read_file(data)
        r = weber(gdf, attribute)

        geojson = r.__geo_interface__
        self.add_geojson(geojson, name = name, **kwargs)


    def add_cmark(self, location, **kwargs):
        """Add a circle marker to the map.

        Args:
            location (tuple): XY coordinate of the marker.
        """        
        circle_marker = ipyleaflet.CircleMarker()
        circle_marker.location = location
        circle_marker.radius = 3
        circle_marker.color = "red"
        circle_marker.fill_color = "red"

        self.add_layer(circle_marker)


    def add_pmedian():
        print('')



    def add_raster(self, url, name = 'Raster', fit_bounds = True, **kwargs):
        """Add a raster file to the map.

        Args:
            url (str): An url of the raster image.
            name (str, optional): A layer name of the raster to be displayed on the map. Defaults to 'Raster'.
            fit_bounds (bool, optional): Move a display of the map to the raster image location. Defaults to True.
        """        
        import httpx

        titiler_endpoint = 'https://titiler.xyz'
        
        # get a bbox
        r = httpx.get(
            f"{titiler_endpoint}/cog/info",
            params = {
                "url": url,
            }
        ).json()

        bounds = r["bounds"]

        # get a url
        r = httpx.get(
            f"{titiler_endpoint}/cog/tilejson.json",
            params = {
                "url": url,
            }
        ).json()

        tile = r['tiles'][0]

        self.add_tile_layer(url = tile, name = name, **kwargs)

        if fit_bounds:
            bbox = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            self.fit_bounds(bbox)
        

    def add_vector(
        self,
        filename,
        layer_name = 'Vector data',
        **kwargs,
    ):
        """Add a vector layer to the map

        Args:
            filename (str): The name of the vector file.
            layer_name (str, optional): A layer name to be shown on the map. Defaults to 'Vector data'.
        """    
        import os
        if not filename.startswith('http'):
            filename = os.path.abspath(filename)
        else:
            filename = github_raw_url(filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.shp':
            self.add_shp(
                filename,
                layer_name
            )
        elif ext in ['.json', '.geojson']:
            self.add_geojson(
                filename,
                layer_name
            )
        else:
            geojson = vector_to_geojson(
                filename,
                bbox = bbox,
                mask = mask,
                rows = rows,
                epsg = '4326',
                **kwargs,
            )

            self.add_geojson(
                geojson,
                layer_name
            )


    def add_image(self, url, width, height, position = 'bottomright'):
        """Add an image file to the map.

        Args:
            url (str): An url of the image.
            width (float): width of the image to be displayed
            height (float): height of the image to be displayed
            position (_type_, optional): Position argument. Defaults to 'bottomright'.
        """        
        from ipyleaflet import WidgetControl
        import ipywidgets as widgets

        widget = widgets.HTML(value = f'<img src="{url}" width = "{width}" height = "{height}">')
        control = WidgetControl(widget = widget, position = position)
        self.add(control)


    def to_streamlit(self, width=None, height=600, scrolling=False, **kwargs):
        ####### just copied from leafmap
        """Renders map figure in a Streamlit app.
        Args:
            width (int, optional): Width of the map. Defaults to None.
            height (int, optional): Height of the map. Defaults to 600.
            responsive (bool, optional): Whether to make the map responsive. Defaults to True.
            scrolling (bool, optional): If True, show a scrollbar when the content is larger than the iframe. Otherwise, do not show a scrollbar. Defaults to False.
        Returns:
            streamlit.components: components.html object.
        """

        try:
            import streamlit.components.v1 as components

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


    def to_html(
        self,
        outfile=None,
        title="My Map",
        width="100%",
        height="880px",
        **kwargs,
    ):
        ####### just copied from leafmap
        """Saves the map as an HTML file.
        Args:
            outfile (str, optional): The output file path to the HTML file.
            title (str, optional): The title of the HTML file. Defaults to 'My Map'.
            width (str, optional): The width of the map in pixels or percentage. Defaults to '100%'.
            height (str, optional): The height of the map in pixels. Defaults to '880px'.
            add_layer_control (bool, optional): Whether to add the LayersControl. Defaults to True.
        """
        try:
            save = True
            if outfile is not None:
                if not outfile.endswith(".html"):
                    raise ValueError("The output file extension must be html.")
                outfile = os.path.abspath(outfile)
                out_dir = os.path.dirname(outfile)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
            else:
                outfile = os.path.abspath(generate_random_string(3) + ".html")
                save = False

            '''
            if add_layer_control and self.layer_control is None:
                layer_control = ipyleaflet.LayersControl(position="topright")
                self.layer_control = layer_control
                self.add(layer_control)
            '''
            
            before_width = self.layout.width
            before_height = self.layout.height

            if not isinstance(width, str):
                print("width must be a string.")
                return
            elif width.endswith("px") or width.endswith("%"):
                pass
            else:
                print("width must end with px or %")
                return

            if not isinstance(height, str):
                print("height must be a string.")
                return
            elif not height.endswith("px"):
                print("height must end with px")
                return

            self.layout.width = width
            self.layout.height = height

            self.save(outfile, title=title, **kwargs)

            self.layout.width = before_width
            self.layout.height = before_height

            if not save:
                out_html = ""
                with open(outfile) as f:
                    lines = f.readlines()
                    out_html = "".join(lines)
                os.remove(outfile)
                return out_html

        except Exception as e:
            raise Exception(e)

    # final exam Q2
    def add_points_from_csv(self, in_csv, x="longitude", y="latitude", layer_name="Marker cluster"):
        """Add point marker cluster to the map.

        Args:
            in_csv (str): csv file name
            x (str, optional): The column name that contains X coordinates. Defaults to "longitude".
            y (str, optional): The column name that contains Y coordinates. Defaults to "latitude".
            layer_name (str, optional): A layer name. Defaults to "Marker cluster".
        """        
        df = pd.read_csv(in_csv)

        Xls = df[x]
        Yls = df[y]

        ls = []
        for i in range(len(df)):
            marker = ipyleaflet.Marker(location = (Yls[i], Xls[i]))
            ls.append(marker)
        
        marker_cluster = ipyleaflet.MarkerCluster(markers = ls)
        self.add_layer(marker_cluster)


    '''
    # final exam Q3
    def add_select_mc(self, position = 'bottomright', **kwargs):
        import ipyfilechooser
        import os
        path = os.getcwd()
        output_widget = widgets.Output(layout={'border': '1px solid black'})
        output_widget.clear_output()
        selection = ipyfilechooser.FileChooser(path)
      
        button = widgets.ToggleButton(
            value=False,
            tooltip="Apply",
            icon="wrench"
        )

        v = widgets.VBox([selection, button])

        control = ipyleaflet.WidgetControl(widget = v, position = 'bottomright')
        self.add(control)

        def button_click(change):
            if change["new"]:
                try: 
                    self.add_points_from_csv(selection.selected)
                except Exception as e:
                    raise Exception(e)
                
        button.observe(button_click, "value")
    '''


# final exam Q1
def csv_to_shp(in_csv, out_shp, x="longitude", y="latitude", attribute = None):
    """Convert csv that contains longitude and latitude columns to a shapefile.

    Args:
        in_csv (str): csv file name
        out_shp (str): name of output file
        x (str, optional): The column name that contains X coordinates. Defaults to "longitude".
        y (str, optional): The column name that contains Y coordinates. Defaults to "latitude".
        attribute (str, optional): The column name that contains attribute. Defaults to None.
    """    
    df = pd.read_csv(in_csv)
    
    Xls = df[x]
    Yls = df[y]
    if attribute != None:
        att_ls = df[attribute]
        df_dict = {'Attribute': att_ls, 'XCoord': Xls, 'YCoord': Yls}
        gdf = gpd.GeoDataFrame(pd.DataFrame(df_dict), geometry = gpd.points_from_xy(Xls, Yls))
    else:
        gdf = gpd.GeoDataFrame(geometry = gpd.points_from_xy(Xls, Yls))
    gdf.to_file(out_shp)
    
def csv_to_geojson(in_csv, out_geojson, x="longitude", y="latitude", attribute = None):
    """Convert csv that contains longitude and latitude columns to a geojson file.

    Args:
        in_csv (str): csv file name
        out_geojson (str): name of output file
        x (str, optional): The column name that contains X coordinates. Defaults to "longitude".
        y (str, optional): The column name that contains Y coordinates. Defaults to "latitude".
        attribute (str, optional): The column name that contains attribute. Defaults to None.
    """  
    df = pd.read_csv(in_csv)
    
    Xls = df[x]
    Yls = df[y]
    if attribute != None:
        att_ls = df[attribute]
        df_dict = {'Attribute': att_ls, 'XCoord': Xls, 'YCoord': Yls}
        gdf = gpd.GeoDataFrame(pd.DataFrame(df_dict), geometry = gpd.points_from_xy(Xls, Yls))
    else:
        gdf = gpd.GeoDataFrame(geometry = gpd.points_from_xy(Xls, Yls))
    geojson = gdf.__geo_interface__
    gdf.to_file(out_geojson)






def distance_matrix(df):
    """Create an Euclidean distance matrix from a point shapefile.

    Args:
        df (GeoDataFrame): Input GDF file.

    Returns:
        numpy array: Created distance matrix.
    """
    mat = []
    for i in list(df.index):
        temp_ls = list(df['geometry'].distance(df['geometry'][i]))
        mat.append(temp_ls)
    mat = np.array(mat)
    mat = mat
    
    return mat


def weber(gdf, attribute):
    """Solve the single-facility Weber problem using a gradient descent algorithm.

    Args:
        gdf (GeoDataFrame): Input GDF file.
        attribute (str): Column name that contains the weight.
    Returns:
        GeoDataFrame: Result of the Weber problem.
    """    
    import geopandas as gpd
    import pandas as pd
    import numpy as np

    geometry = gdf.geometry
    x_coords = geometry.x
    y_coords = geometry.y

    w = np.array(gdf[attribute])
    xi = np.array(x_coords)
    yi = np.array(y_coords)

    # gradient descent for each decision var.s
    def gradX(X, Y, Z, w, xi, yi):
        gradXls = []
        for j in range(0, len(Z)):
            gradXj = 0
            for i in range(0, len(w)):
                gradXj = gradXj + Z[j][i] * w[i] * (X[j] - xi[i]) / (np.sqrt(np.power(xi[i] - X[j], 2) + np.power(yi[i] - Y[j], 2)))
            gradXls.append(gradXj)
        gradXj = 0
        for i in range(0, len(w)):
            gradXj = gradXj + w[i] * (X[-1] - xi[i]) / (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
            for j in range(0, len(Z)):
                gradXj = gradXj - Z[j][i] * w[i] * (X[-1] - xi[i]) / (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
        gradXls.append(gradXj)
        return np.array(gradXls)

    def gradY(X, Y, Z, w, xi, yi):
        gradYls = []
        for j in range(0, len(Z)):
            gradYj = 0
            for i in range(0, len(w)):
                gradYj = gradYj + Z[j][i] * w[i] * (Y[j] - yi[i]) / (np.sqrt(np.power(xi[i] - X[j], 2) + np.power(yi[i] - Y[j], 2)))
            gradYls.append(gradYj)
        gradYj = 0
        for i in range(0, len(w)):
            gradYj = gradYj + w[i] * (Y[-1] - yi[i]) / (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
            for j in range(0, len(Z)):
                gradYj = gradYj - Z[j][i] * w[i] * (Y[-1] - yi[i]) / (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
        gradYls.append(gradYj)
        return np.array(gradYls)

    def gradZ(X, Y, Z, w, xi, yi):
        gradZls = []
        for j in range(0, len(Z)):
            gradZtemp = []
            for i in range(0, len(w)):
                gradZi = w[i] * (np.sqrt(np.power(xi[i] - X[j], 2) + np.power(yi[i] - Y[j], 2))) - w[i] * (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
                gradZtemp.append(gradZi)
            gradZls.append(gradZtemp)
        return np.array(gradZls)

    # define objective function for the GD
    def obj(X, Y, Z, w, xi, yi):
        objective = 0
        for i in range(0, len(w)):
            for j in range(0, len(Z)):
                objective = objective + Z[j][i] * w[i] * (np.sqrt(np.power(xi[i] - X[j], 2) + np.power(yi[i] - Y[j], 2)))
                objective = objective - Z[j][i] * w[i] * (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
            objective = objective + w[i] * (np.sqrt(np.power(xi[i] - X[-1], 2) + np.power(yi[i] - Y[-1], 2)))
        return objective

    # initial variables
    Xg = np.array([sum(xi) / len(xi)])
    Yg = np.array([sum(yi) / len(yi)])
    Zg = []
    for j in range(0, 0):
        Zg.append(np.array([0.5] * len(w)))
    Zg = np.array(Zg)

    # gradient descent
    max_iter = 500
    step_size = 0.000001
    obj_val_ls = []

    for t in range(max_iter):
        obj_val = obj(Xg, Yg, Zg, w, xi, yi)
        obj_val_ls.append(obj_val)
        
        Xg = Xg - step_size * gradX(Xg, Yg, Zg, w, xi, yi)
        Yg = Yg - step_size * gradY(Xg, Yg, Zg, w, xi, yi)
    
    r = gpd.GeoDataFrame(geometry = gpd.points_from_xy(x = Xg, y = Yg))
    r['ObjVal'] = obj_val

    return r



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


def generate_lucky_number(length = 2):
    """Generates a random number of a given length.

    Args:
        length (int, optional): A length of the number. Defaults to 2.

    Returns:
        int: Generated random number.
    """    
    result_str = ''.join(random.choice(string.digits) for i in range(length))
    result_str = int(result_str)
    return result_str


def euclidean_dist(first_coord, second_coord):
    """Calculates an Euclidean distance between two coordinates.

    Args:
        first_coord (list): A coordinate of the first point. Should have 2 length. 
        second_coord (list): A coordinate of the second point. Should have 2 length. 

    Returns:
        int: Calculated Euclidean distance.
    """
    import math
    for coord in [first_coord, second_coord]:
        if not isinstance(coord, (list, tuple)) or len(coord) != 2:
            raise ValueError('The coordinates must be lists or tuples of length 2.')
        for element in coord:
            if not isinstance(element, (int, float)):
                raise ValueError('The elements of the coordinates must be integers or floats.')
                
    x_diff = first_coord[0] - second_coord[0]
    y_diff = first_coord[1] - second_coord[1]
    dist = math.sqrt(x_diff ** 2 + y_diff ** 2)
    return dist