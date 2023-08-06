"""
Storage for points data

Josselin Duchateau, IHU liryc
Last update 06/12/2021
"""
from collections.abc import MutableMapping
from enum import IntEnum
from xml.etree import ElementTree as etree
from .utils import LazyClass, load_pv
from typing import Union, Iterator, Tuple, Optional, Any
import re
import numpy as np


class PointType(IntEnum):
    """ Enumeration of different point types """
    NORMAL = 0
    LOCATION_ONLY = 1
    SCAR = 2
    FLOATING = 3
    TRANSIENT_EVENT = 4


class SigReference:
    """ Signal reference """
    def __init__(self, id, ts, ref_ts_delay, lat_ts_delay, woi, uni, bi, uni_chan, bi_chan, ref_chan):
        self.id = id
        self.ts = ts  # PIU_START_TIME
        self.ref_ts_delay, self.lat_ts_delay = ref_ts_delay, lat_ts_delay # REF_ANNOTATION_TIME_DATA, MAP_ANNOTATION_LAT
        self.woi = woi  # MAP_ANNOTATION_WOI_FROM, MAP_ANNOTATION_WOI_TO
        self.uni, self.bi = uni, bi  # VOLTAGE_UNIPOLAR, VOLTAGE_BIPOLAR
        self.uni_chan, self.bi_chan, self.ref_chan = uni_chan, bi_chan, ref_chan
        # MAP_ELECTRODE1_INDEX # MAP_ANNOTATION_CHANNEL_INDEX, # REF_ANNOTATION_CHANNEL_INDEX

    def __repr__(self):
        ref_info = f' ref: {self.ref_chan}' if self.ref_chan else ''
        return f'<Signal Reference: @ts {self.ts}, channels: {self.uni_chan} | {self.bi_chan}{ref_info}>'


class LazySigRef(LazyClass, SigReference):
    """ Lazy loader for a signal reference """
    def __init__(self, data_source, filename):
        LazyClass.__init__(self)
        self._data_source = data_source
        self._filename = filename

    @property
    def _lazy(self):
        return ['id', 'ts', 'ref_ts_delay', 'lat_ts_delay', 'woi',
                'uni', 'bi', 'uni_chan', 'bi_chan', 'ref_chan']

    @property
    def filename(self):
        """ Filename to load when properties are accessed"""
        return self._filename

    def load(self):
        """ Load the target filename """
        with self._data_source.open(self._filename) as f:
            root = etree.parse(f).getroot()
            self.id = root.get('ID')
            # self.date = root.get('Date')
            # self.time = root.get('Time')

            # Annotations
            annotations = root.find('Annotations')
            self.ts = int(annotations.get('StartTime'))
            ref_ts_delay = int(annotations.get('Reference_Annotation'))
            self.ref_ts_delay = ref_ts_delay
            lat_ts_delay = int(annotations.get('Map_Annotation'))
            if lat_ts_delay - ref_ts_delay == - 10000:
                self.lat_ts_delay = np.nan
            else:
                self.lat_ts_delay = lat_ts_delay

            # WOI
            woi = root.find('WOI')
            self.woi = (int(woi.get("From")), int(woi.get("To")))

            # Voltages
            voltages = root.find('Voltages')
            self.uni = float(voltages.get("Unipolar"))
            self.bi = float(voltages.get("Bipolar"))

            # ECG datafile
            ecg = root.find('ECG')
            ecg_filename = ecg.get('FileName')

        # Read the headers of the ecg_filename
        with self._data_source.open(ecg_filename) as f:
            f.readline()  # Skip headers
            f.readline()
            mapping_chan_line = f.readline().decode('utf-8')
        mapping_chan = re.match(r'Unipolar Mapping Channel=(?P<uni>[\w-]+) '
                                r'Bipolar Mapping Channel=(?P<bi>[\w-]+)'
                                r'( Reference Channel=(?P<ref>[\w-]+))?', mapping_chan_line)

        uni_chan, bi_chan, ref_chan = mapping_chan['uni'], mapping_chan['bi'], mapping_chan['ref']
        self.uni_chan = uni_chan.replace('_', ' ')
        self.bi_chan = bi_chan.replace('_', ' ')
        self.ref_chan = ref_chan.replace('_', ' ')

        self._loaded = True

    def __repr__(self):
        if self._loaded:
            ref_info = f' ref: {self.ref_chan}' if self.ref_chan else ''
            return f'<Signal Reference: @ts {self.ts}, channels: {self.uni_chan} | {self.bi_chan}{ref_info}>'
        return '<Signal Reference (lazy load)>'


class Point(MutableMapping):
    """ A class describing a point with annotations +/- signals """

    def __init__(self, id: str, x: float, y: float, z: float, a: float = 0., b: float = 0., g: float = 0.,
                 cath_id: Optional[int] = None, sig_ref: Union[SigReference, LazySigRef] = None, **annotations):
        """
        Create an instance of a Point object.

        :param id: point id (string)
        :param x: x position (float)
        :param y: y position (float)
        :param z: z position (float)
        :param a: angle alpha (float)
        :param b: angle beta (float)
        :param g: angle gamma (float)
        :param cath_id: cathetr ID (integer)
        :param sig_ref: reference to signal (LazySigRef or SigReference object)
        :param annotations: annotations of this point (lat, voltages, etc.)
        """
        self.id = id
        self.cath_id = cath_id
        self.x, self.y, self.z = float(x), float(y), float(z)
        self.a, self.b, self.g = float(a), float(b), float(g)
        self._ref = sig_ref

        # Add the annotations to the point
        self._annotations = {}
        for annotation, value in annotations.items():
            self[annotation] = value

    @classmethod
    def from_line(cls, line, point_tags=None):
        """ Create a point from a line in a .car file
        :param line: line of text to parse in the car file
        :param point_tags: point tags from which to get tag information
        :return: the created point object
        """
        components = line.split("\t")
        pt_id = components[2]
        cath_id = int(components[19])
        xyzabg = [float(i) for i in components[4:10]]
        annotations = {
            'unipolar': float(components[10]),
            'bipolar': float(components[10]),
            'lat': int(components[12]),
            'impedance': float(components[13]),
            'point type': int(components[14]),
            'tag': point_tags(int(components[15])) if point_tags is not None else int(components[15])
        }
        if annotations['lat'] == -10000:
            annotations['lat'] = np.nan
        return cls(pt_id, *xyzabg, cath_id=cath_id, **annotations)

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise KeyError('Point-related data attributes are stored as strings')
        try:
            return self._annotations.__getitem__(item)
        except KeyError:
            return np.nan

    def __setitem__(self, key, value) -> None:
        if not isinstance(key, str):
            raise KeyError('Point-related data attributes are stored as strings')
        return self._annotations.__setitem__(key, value)

    def __delitem__(self, key) -> None:
        return self._annotations.__delitem__(key)

    def __len__(self) -> int:
        return self._annotations.__len__()

    def __iter__(self) -> Iterator:
        return self._annotations.__iter__()

    def __repr__(self) -> str:
        return f"<Point id='{self.id}' @ {self.x}, {self.y}, {self.z}>"

    def __copy__(self):
        """
        Create a copy of the point

        :return: New point with copied properties and annotations
        """
        point_copy = Point(self.id, self.x, self.y, self.z, self.a, self.b, self.g, self._ref)

        # Copy annotations
        for annotation, value in self.items():
            point_copy[annotation] = value

        return point_copy

    @property
    def pos(self) -> Tuple[float, float, float]:
        """ Position getter """
        return self.x, self.y, self.z

    @pos.setter
    def pos(self, value) -> None:
        """ Position setter """
        self.x, self.y, self.z = float(value[0]), float(value[1]), float(value[2])

    @property
    def angle(self) -> Tuple[float, float, float]:
        """ Angle getter """
        return self.a, self.b, self.g

    @angle.setter
    def angle(self, value) -> None:
        """ Angle setter """
        self.a, self.b, self.g = float(value[0]), float(value[1]), float(value[2])

    @property
    def ref(self):
        """ Reference to the signal - getter """
        if isinstance(self._ref, LazySigRef) and not self._ref.loaded:
            self._ref.load()
        return self._ref

    @ref.setter
    def ref(self, value):
        """ Reference to the signal - setter """
        if not isinstance(value, SigReference):
            raise ValueError('Signal reference must be a valid reference object.')
        self._ref = value


class PointSet(MutableMapping):
    """ A point collection """
    def __init__(self, name, points:dict =None):
        self._name = name
        self._points = points if points else {}

    @classmethod
    def from_car_file(cls, data_source, filename, point_tags=None):
        """ Read point collection from .car file"""
        with data_source.open(filename) as car_file:
            line = car_file.readline().decode('utf-8')
            #header = re.match(r'VERSION_(?P<version>[\d_])+ (?P<map_name>[^\r\n]+)', line)
            #name = header['map_name']
            # version = header['version'].replace('_', '.')
            name = re.match(r'(?P<study>.*)_car\.txt', filename)['study']
            points = {}
            for line in car_file:
                pt = Point.from_line(line.decode('utf-8'), point_tags)
                pt.ref = LazySigRef(data_source, f'{name}_P{pt.id}_Point_Export.xml')
                points[pt.id] = pt
        return cls(name, points)

    @classmethod
    def from_db(cls, db_cursor, map_name):
        # TO DO: complete code
        """ Read point collection from database """
        query = f"SELECT MAP_IDX FROM MAPS_TABLE WHERE NAME={map_name}"
        db_cursor.execute(query)
        try:
            idx = next(db_cursor)[0]
        except StopIteration:
            raise ValueError('Could not find specified map in maps tables.')

        query = (f"SELECT ("
                 f"POINT_IDX, X_COORDINATE, Y_COORDINATE, Z_COORDINATE, "
                 f"ALPHA_COORDINATE, BETA_COORDINATE, GAMMA_COORDINATE, "
                 f"VOLTAGE_UNIPOLAR, VOLTAGE_BIPOLAR, "
                 f"MAP_ANNOTATION_LAT, IMPEDANCE,"
                 f"POINT_TYPE, TAG_TYPE, CATHETER_ID"
                 f") FROM POINTS_TABLE WHERE MAP_IDX={idx}")

        db_cursor.execute(query)
        points = {}
        for row in db_cursor:
            pt = Point(*row)
            points[pt.id] = pt
            # HERE WE NEED TO CREATE A REFERENCE TO THE BINARY DATA ?

        cls(map_name, points)

    @property
    def name(self):
        """ Name of the point collection """
        return self._name

    def duplicate(self, new_name: str = None):
        """
        Create a copy of the point set. Each individual point is copied as a new instance.

        :param new_name: New name for the copied set
        :return: A copy of the point set with duplicated points
        """
        new_name = new_name or self._name + ' - duplicate'
        duplicate = PointSet(new_name)

        for pt in self._points.values():
            pt_copy = pt.__copy__()
            duplicate[pt_copy.id] = pt_copy

        return duplicate

    def attribute_array(self, attribute) -> np.ndarray:
        """
        Return a numpy array of the requested attribute

        :param attribute: Attribute
        :return: Numpy array
        """
        return np.asarray([pt[attribute] for pt in self.values()])

    def project(self, mesh, threshold: Optional[float] = None) -> Any:
        """
        Project the point set to a given mesh.

        :param mesh: Carto mesh or pyvista mesh on which we should project the points. The points are projected to the
        nearest cell on this mesh.
        :param threshold: Optional threshold distance above which points should be discarded
        """
        # Duplicate points and get the position array
        duplicate = self.duplicate(self._name + '-Projected')
        point_positions = duplicate.position_array

        # Get a pyvista version of the mesh
        pv_mesh = mesh.pv_mesh(cutouts=False)

        # Project the points to the nearest cell, store the distance
        index, projections = pv_mesh.find_closest_cell(point_positions, True)
        distances = np.sqrt(np.sum((point_positions - projections) ** 2, 1))
        for pt, distance in zip(duplicate.values(), distances):
            pt['projection distance'] = distance

        # Filter points if necessary
        if threshold is not None:
            for pt_id, distance in zip(list(duplicate), distances):
                if distance > threshold:
                    del duplicate[pt_id]

        return duplicate

    @property
    def position_array(self):
        """
        Get a numpy array with all the point positions.

        :return:
        """
        return np.asarray([pt.pos for pt in self.values()])

    def __getitem__(self, item):
        if isinstance(item, int):
            item = list(self.keys())[item]
        return self._points.__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = list(self.keys())[key]
        if isinstance(key, str):
            if not key.isnumeric() or int(key) < 1:
                raise TypeError('Keys must be a string representation of a positive integer.')
        return self._points.__setitem__(key, value)

    def __delitem__(self, key):
        if isinstance(key, int):
            key = list(self.keys())[key]
        return self._points.__delitem__(key)

    def __len__(self):
        return self._points.__len__()

    def __iter__(self):
        return self._points.__iter__()

    def __repr__(self):
        return f"<Point Set '{self.name}': {len(self._points)} points>"