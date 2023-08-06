"""
Mesh information

Josselin Duchateau, IHU Liryc
Last updated 06/12/2021
"""
from dataclasses import dataclass
import numpy as np
from collections.abc import MutableMapping
from typing import List, Optional
from .utils import load_pv

# Colormaps for the default mesh maps
DEFAULT_COLORMAPS = {
    'unipolar': ('gist_rainbow', [1.5, 5]),
    'bipolar': ('gist_rainbow', [0.5, 1.5]),
    'lat': ('hsv', None),
    'groupid': ('tab20', None)
}


@dataclass
class MeshAttributes:
    """ Attributes of the mesh """
    MeshID: int
    MeshName: str
    NumVertex: int
    NumTriangle: int
    TopologyStatus: int
    MeshColor: List[float]
    Matrix: List[float]
    NumVertexColors: int
    ColorsIDs: Optional[List[int]] = None
    ColorsNames: Optional[List[str]] = None
    NumVertexInitial: int = None
    NumTriangleInitial: int = None
    NumVisibleGroups: int = None
    VisibleGroupsIDs: List[int] = None
    VisibleGroupsTypes: List[int] = None
    NumTransparentGroups: int = None
    TransparentGroupsIDs: List[int] = None
    TransparentGroupsTypes: List[int] = None


class Mesh(MutableMapping):
    """ A class containing Carto FAM meshes and colormaps"""
    def __init__(self, vertices: np.ndarray = None, triangles: np.ndarray = None,
                 vertice_normals: np.ndarray = None, triangle_normals: np.ndarray = None,
                 attributes=None):
        self.v = vertices
        self.t = triangles
        self.vn = vertice_normals
        self.tn = triangle_normals

        self.attributes = attributes
        self._maps = {}

    @classmethod
    def from_file(cls, data_source, filename):
        """ Read a mesh from a file """
        if filename not in data_source.listdir():
            raise ValueError('Requested mesh not found in datasource.')

        def listify(value_string):
            """ Turn into a list"""
            item_list = value_string.strip().split()
            if not item_list:
                return None

            try:
                item_list = [int(item) for item in item_list]
            except ValueError:
                try:
                    item_list = [float(item) for item in item_list]
                except ValueError:
                    pass
            if len(item_list) == 1:
                return item_list[0]

            return item_list

        def read_attributes(_f):
            """ Read the attributes section """
            attributes = {}
            for _line in _f:
                _line = _line.decode('latin-1').rstrip()
                if not _line:
                    break
                if _line[0] == ';':
                    continue
                name, value = _line.split('=')
                attributes[name.strip()] = listify(value)
            return MeshAttributes(**attributes)

        def line_filter(_f):
            """ Filter line """
            got_data = False
            for _line in _f:
                if not _line.rstrip():
                    if got_data:
                        return
                    else:
                        continue
                if _line[0:1] == b';':
                    continue
                _line = _line.replace(b'=', b' ')
                got_data = True
                yield _line

        obj = cls()
        maps = None
        v_attributes = None
        with data_source.open(filename) as f:
            for line in f:
                line = line.rstrip()
                if line == b'[GeneralAttributes]':
                    obj.attributes = read_attributes(f)
                if line == b'[VerticesSection]':
                    vertices = np.loadtxt(line_filter(f))
                    obj.v = vertices[:, 1:4]
                    obj.vn = vertices[:, 4:7]
                    # obj._maps['vGroupID'] = vertices[:, 7]  # Vertex group info doesn't contain any data usually...
                if line == b'[TrianglesSection]':
                    triangles = np.loadtxt(line_filter(f))
                    obj.t = triangles[:, 1:4].astype(int)
                    obj.tn = triangles[:, 4:7]
                    group_id = -triangles[:, 7].astype(int)
                    group_id[group_id == 1000000] = -1
                    obj._maps['GroupID'] = group_id
                if line == b'[VerticesColorsSection]':
                    maps = np.loadtxt(line_filter(f))
                    maps[maps == -10000.] = np.nan
                if line == b'[VerticesAttributesSection]':
                    v_attributes = np.loadtxt(line_filter(f), dtype=int)
                    if len(v_attributes) == 0:
                        v_attributes = None

        if obj.attributes.ColorsNames is not None and maps is not None:
            for map, map_name in zip(maps.transpose()[1:], obj.attributes.ColorsNames):
                obj._maps[map_name] = map
        if v_attributes is not None:
            obj._maps['Scar'] = v_attributes.transpose()[1]
            obj._maps['EML'] = v_attributes.transpose()[2]
        return obj

    def interpolate_points(self, point_set, attribute: str, map_name: Optional[str] = None,
                           interpolate_nan: bool = False, **interpolation_options):
        """
        Create a new map on the mesh by interpolating points
        :param point_set: the point set from which the data must be interpolated
        :param attribute: the attribute to interpolate
        :param map_name: optional name of the map to create (defaults to the attribute name)
        :param interpolate_nan: interpolate NaN values or remove them before hand
        :param interpolation_options: interpolation options to pass to the interpolate function.
        These options include: radius, sharpness, strategy, null_value, n_points, etc.
        See the pyvista.DataSetFilters.interpolate documentation for details.
        """
        pv = load_pv()
        map_name = map_name or attribute

        # Get position and attribute arrays
        pos = point_set.position_array
        vals = point_set.attribute_array(attribute)

        # Filter NaN Values
        if not interpolate_nan:
            pos = pos[np.logical_not(np.isnan(vals))]
            vals = vals[np.logical_not(np.isnan(vals))]

        # Create pyvista version of the points/attributes data
        pts = pv.PolyData(pos)
        pts['val'] = vals

        # Get a pyvista version of our mesh, and interpolate the points to this mesh
        if not interpolation_options: # Default options if none are present
            interpolation_options = {'radius': 14, 'sharpness': 5, 'null_value': np.nan}
        pv_mesh = self.pv_mesh(cutouts=False)
        pv_mesh = pv_mesh.interpolate(pts, **interpolation_options)
        self[map_name] = pv_mesh['val']

    @property
    def num_v(self):
        """ Number of vertices """
        return len(self.v)

    @property
    def num_t(self):
        """ Number of triangles (simplexes) """
        return len(self.t)

    def __len__(self):
        return self._maps.__len__()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = list(self.keys())[item]
        return self._maps.__getitem__(item)

    def __delitem__(self, key):
        if isinstance(key, int):
            key = list(self.keys())[key]
        return self._maps.__delitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = list(self.keys())[key]
        if not isinstance(value, np.ndarray):
            _value = np.ndarray(value)
        else:
            _value = value
        _value.flatten()
        if len(value) != self.num_v | len(value) != self.num_t:
            raise ValueError('Input map has an invalid number of values')
        return self._maps.__setitem__(key, value)

    def __iter__(self):
        return self._maps.__iter__()

    def __repr__(self):
        return f'<Mesh ({self.num_v} x {self.num_t}), {len(self)} Maps>'

    def pv_mesh(self, cutouts=True, all_maps=False):
        """
        Get a pyvista mesh version of the current Mesh object.
        Requires a working installation of pyvista.
        :param cutouts: remove the cutouts
        :param all_maps: add all maps as scalar fields to the object
        :return:
        """
        pv = load_pv()
        if 'GroupID' in self:
            if cutouts:
                t = self.t[self['GroupID'] == 0]
            else:
                t = self.t[self['GroupID'] != -1]
        else:
            t = self.t

        poly_data = pv.PolyData(self.v, np.hstack((np.full((len(t), 1), 3, int), t)))
        if all_maps:
            for map_name, map_data in self.items():
                if len(map_data) == self.num_t and 'GroupID' in self:
                    if cutouts:
                        map_data = map_data[self['GroupID'] == 0]
                    else:
                        map_data = map_data[self['GroupID'] != -1]

                poly_data[map_name] = map_data

        return poly_data

    def plot(self, _map=None, cutouts=True):
        """ Plot the mesh
        :param _map: The map to plot (optional) - can be either a map name/index or a numpy array
        :param cutouts: remove cutouts (default is True) or display the full mesh
        :return:
        """
        pv = load_pv()
        poly_data = self.pv_mesh(cutouts)
        plotter = pv.Plotter()
        i = -1
        cmap, clim = None, None
        if _map is None:
            _map = np.zeros((self.num_v,))
        elif isinstance(_map, (str, int)):
            if isinstance(map, int):
                _map = list(self.keys())[_map]
            cmap, clim = DEFAULT_COLORMAPS.get(_map.lower(), (None, None))
            _map = self[_map]

        if len(_map) == self.num_t and 'GroupID' in self:
            if cutouts:
                _map = _map[self['GroupID'] == 0]
            else:
                _map = _map[self['GroupID'] != -1]

        curr_mesh = plotter.add_mesh(poly_data, scalars=_map, cmap=cmap, clim=clim)
        curr_text = plotter.add_text('')

        def change_map(increment):
            """ Callback function to change map """
            def plot_map():
                nonlocal i, curr_text, curr_mesh
                i = (i + increment + len(self)) % len(self)
                map_name = list(self.keys())[i]
                cmap, clim = DEFAULT_COLORMAPS.get(map_name.lower(), (None, None))
                plotter.remove_actor(curr_mesh)
                _map = self[i]

                if len(_map) == self.num_t and 'GroupID' in self:
                    if cutouts:
                        _map = _map[self['GroupID'] == 0]
                    else:
                        _map = _map[self['GroupID'] != -1]

                curr_mesh = plotter.add_mesh(poly_data, scalars=_map, cmap=cmap, clim=clim)
                plotter.remove_actor(curr_text)
                curr_text = plotter.add_text(map_name)
            return plot_map

        plotter.add_key_event('Left', change_map(-1))
        plotter.add_key_event('Right', change_map(1))
        plotter.show()
