# Carto Reader
This package provides convenient tools for reading Carto (BiosenseWebster) files using python.

## Installing
```
pip install carto_reader
pip install carto_reader[viz]
```
The `viz` option adds support for signal and mesh visualization, using matplotlib and pyvista.

## Example usage
### Data import
```
from carto_reader.carto_data import Carto
carto = Carto('./path/to/archive.zip')
``` 

### Listing available maps
```
>>> list(carto)
['1-LA', '2-RA', '1-1-ReLA']
```
Access maps by their name or by index.
```
>>> carto[0]
<Map 1-LA: 2005 Points, 13559 x 27684 Mesh>
>>> carto['1-LA']
<Map 1-LA: 2005 Points, 13559 x 27684 Mesh>
```

### Getting mapping points
Access map points by id or by index.
```
>>> la_map = carto['1-LA']
>>> la_map.points[0]
<Point id='5' @ 25.6723, -66.265, 78.4703 - bi:0.573, uni:0.573, lat:-57>
>>> la_map.points['5']
```

Get a reference to the signal at a given point
```
>>> point = la_map.points[0]
>>> point.ref
<Signal Reference: @ts 2917695, channels: 20A 9 | 20A 9-10 ref: CS9-CS10>
```

### Signals
The signal references are lazy-loaded, meaning that the point and signal files headers are read and only when the reference object is accessed.

Signals are stored by blocks in the Carto object, so that continuous block may be recreated from individually captured points, and to avoid redundancy.

To easily get reference and mapping signals from a given point, you may use the following call: 
```
>>> carto.signal_from_point(point)
{'t': array([...]), 'uni': array([...]), 'bi': array([...]), 'ref': array([...])}
```

By default, a window of 1000ms of signal centered on the reference is returned. The interval of interest around this reference can be specified by inputing a slice as the second parameter of the function.

You can plot the signal using using the `carto.plot_point(point)` method, which requires matplotlib. 

You can also load all the signals in a case or in a given map using the `carto.add_signal_files()` method. 
Note that this may take some time as a high number of signal files need to be parsed.

Once signals are loaded, you can access them directly by channel using the `sig` attribute, which is a dictionary of channels:
```
>>> list(carto.sig)
['M1', 'M2', ..., 'aVR', 'aVF']
>>> carto.sig['aVF']
<Channel aVF: 553 s of signal in 67 parts over 798 s>
```

Signals can be accessed by timestamp sing slice notation. Parts of the signal which are not present in the file will be replaced by NaNs.
Individual points grabbed by the system usually store 2500ms of signal in a row.
```
>>> aVf = carto.sig['aVF']
>>> start = aVf.first_sample
>>> aVf[start:start + 2502]
array([0.048, 0.048, 0.045, ..., 0.051,   nan,   nan])
```
 

### Meshes
To get the mesh corresponding to the map, use the `mesh` attribute. The vertices are accessible using the `v` property and the triangles using the `t` property.
Maps corresponding to the mesh can be defined either for the vertices or for the triangles. They are accessible by name or by index.

```
>>> mesh = carto[0].mesh
>>> list(mesh)
['GroupID', 'Unipolar' ... , 'Scar', 'EML']
>>> mesh[0]
array([0, 7, 4, ..., 0, 0, 9])
>>> mesh['GroupID']
array([0, 7, 4, ..., 0, 0, 9])
```

To visualize a mesh and it's maps, you can call `mesh.plot()`. This method requires pyvista. You can install the dependencies required for signal or mesh plotting using the **viz** option upon install.
Use the right and left arrow keys to cycle through the available maps.

### Missing features
 - Importing from non-raw data Carto files
 - Importing the `study.xml` files (especially to get the projected point positions and point tag list)
