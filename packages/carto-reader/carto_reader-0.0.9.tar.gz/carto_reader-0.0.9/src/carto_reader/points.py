"""
Storage for points data

Josselin Duchateau, IHU liryc
Last update 06/12/2021
"""
from collections.abc import MutableMapping
from enum import IntEnum
from xml.etree import ElementTree as etree
from .utils import LazyClass
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


class Point:
    """ A class describing a point with annotations +/- signals """
    def __init__(self, id, x, y, z,
                 a=0., b=0., g=0.,
                 uni=0., bi=0.,
                 lat=np.nan, imp=0.,
                 type=0, tag=-1, cath_id=0,
                 sig_ref: LazySigRef = None):
        self.id = id
        self.x, self.y, self.z = x, y, z
        self.a, self.b, self.g = a, b, g
        self.uni, self.bi = uni, bi
        self.lat, self.imp = lat, imp
        self.type, self.tag, self.cath_id = PointType(type), tag, cath_id
        self._ref = sig_ref

    @classmethod
    def from_line(cls, line, point_tags=None):
        """ Create a point from a line in a .car file """
        components = line.split("\t")
        pt_id = components[2]
        cath_id = int(components[19])
        xyzabg = [float(i) for i in components[4:10]]
        unibi = [float(i) for i in components[10:12]]
        lat = int(components[12])
        if lat == -10000:
            lat = np.nan
        imp = float(components[13])
        pt_type = int(components[14])
        tag = point_tags(int(components[15])) if point_tags is not None else int(components[15])
        return cls(pt_id, *xyzabg, *unibi, lat, imp, pt_type, tag, cath_id)

    def __repr__(self):
        return f"<Point id='{self.id}' @ {self.x}, {self.y}, {self.z} - bi:{self.bi}, uni:{self.uni}, lat:{self.lat}>"

    @property
    def pos(self):
        """ Position getter """
        return [self.x, self.y, self.z]

    @pos.setter
    def pos(self, value):
        """ Position setter """
        self.x, self.y, self.z = value

    @property
    def angle(self):
        """ Angle getter """
        return [self.a, self.b, self.g]

    @angle.setter
    def angle(self, value):
        """ Angle setter """
        self.a, self.b, self.g = value

    @property
    def ref(self):
        """ Reference to the signal - getter """
        if not self._ref.loaded:
            self._ref.load()
        return self._ref

    @ref.setter
    def ref(self, value):
        """ Reference to the signal - setter """
        if not isinstance(value, SigReference):
            raise ValueError('Signal reference must be a reference object.')
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
        return f"<Map '{self.name}': {len(self._points)} points>"