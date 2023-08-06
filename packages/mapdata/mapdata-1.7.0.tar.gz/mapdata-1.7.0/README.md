
*mapdata.py* is a viewer for geographic coordinate data read from a CSV file.  Both a map and a data
table are displayed.  When a location is selected on the map, the same location is highlighted in the
table, and *vice-versa*.  Single or multiple selections may be enabled.

Coordinates should be in decimal degrees, in WGS84 (coordinate reference system [CRS] 4326), however,
coordinates in other CRSs can be converted to 4326.

The map display can be customized in several ways:

  * Different raster tile servers may be used for the basemap.  The default is
    OpenStreetMap.  Several alternatives are provided, and other tile servers
    can be specified in a configuration file.

  * Locations identified by coordinates in the data file may be designated by
    different types of markers and by different colors.  The default marker for
    locations, and the default marker used to flag selected locations can both be
    customized.  Symbols and colors to use for location markers can be specified
	in a configuration file and in the data file.  Different symbols and markers
	can be used for different selected locations.

  * Locations may be unlabeled or labeled with data values from the data file
    The label font, size, color, and location can all be customized.

The map can be exported to a Postscript, PNG, or JPEG file.  Using command-line options,
*mapdata* can be directed to load a data file and display location markers and then to
export the map to an image file, and quit.

Selected rows in the data table can be exported to a CSV file.


