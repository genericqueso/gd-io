import base64 as b64
from typing import Callable, Any
import typing, types
import objectAttributeTransformation as attr_delta
import re

# representing a singular attribute of a GD object (with designated type restrictions)
class gdAttribute:
    def __init__(self, name: str, type_: type) -> None:
        self.name = name
        self.type = type_


# representing an object in GD
class gdObject:
    ID = int(0)
    x = 0.0
    y = 0.0

    # create obj from a dictionary of object values
    def __init__(self, vals: dict[int | str, Any]) -> None:
        for key in vals:
            value = vals[key]

            if type(key) == str:
                if re.match(r'^kA\d+$', key) != None:
                    # special case for (I think only) start pos
                    value = (compress_type(value) != 0)
                else:
                    # if key is already set to a attribute name, convert it back to its numerical form for translation
                    if key in map(lambda entry: entry.name, obj_attr_map.values()):
                        key = next(filter(lambda attr_key: obj_attr_map[attr_key].name == key, obj_attr_map))
                    else:
                        raise Exception("Provided key name ({}) not found in list of permitted attributes".format(key))
            else: 
            # if a decode function exists in obj_attr_transform, decode the value accordingly
            # note: this should only be used on importing from a level string. 
            # when creating an object manually, don't use numerical keys; you might see undesirable behavior
                if compress_type(key) in obj_attr_transform:
                    value = obj_attr_transform[compress_type(key)]["decode"](vals[key])

            # if numerical key exists in obj_attr_map, convert it into its mapped name
            if compress_type(key) in obj_attr_map:
                setattr(
                    self,
                    obj_attr_map[compress_type(key)].name,
                    obj_attr_map[compress_type(key)].type(value),
                )
            else:
                setattr(self, str(key), value)
        assert set(["ID", "x", "y"]).issubset(self.__dict__)

    # for human readable printing
    def __str__(self) -> str:
        return "obj: { " + ", ".join(["{0}: {1}".format(key, str(getattr(self, key))) for key in self.__dict__]) + " }"

    # for printing into GD's internal format
    def compress(self) -> str:
        obj_attrs = []
        for key in self.__dict__:
            value = getattr(self, key)

            # if the name of an attribute exists in obj_attr_map, convert it back to its number counterpart
            # else leave as unchanged key val
            mapkey = next((mkey for mkey in obj_attr_map if obj_attr_map[mkey].name == key), key)
            if mapkey in obj_attr_map:
                if type(obj_attr_map[mapkey].type) == types.GenericAlias:
                    i = 0
                    aliased_type: types.GenericAlias = obj_attr_map[mapkey].type
                    try:
                        if aliased_type.__origin__ == tuple:
                            for i, indexed_type in enumerate(typing.get_args(aliased_type)):
                                assert type(value[i]) == indexed_type
                        elif aliased_type.__origin__ == list:
                            for i in range(len(value)):
                                assert type(value[i]) == typing.get_args(aliased_type)[0]
                    except AssertionError:
                        print(
                            "Warning: Index {2} of value was {3} did not match desired type ({4}) ({0} = {1})".format(
                                key, value, i, type(value[i]), typing.get_args(aliased_type)[i]
                            )
                        )
                else:
                    try:
                        assert type(value) == obj_attr_map[mapkey].type
                    except AssertionError:
                        print(
                            "Warning: Type of value was {2}, did not match desired type ({3}) ({0} = {1})".format(
                                key, value, type(value), obj_attr_map[mapkey].type
                            )
                        )

            if type(value) == bool:
                value = 1 if value else 0

            # if we decoded it above, encode it back again
            if mapkey in obj_attr_transform:
                value = obj_attr_transform[mapkey]["encode"](value)

            obj_attrs.append("{0},{1}".format(mapkey, value))
        return ",".join(obj_attrs)


# representing a color in GD
class gdColor:
    ID = int(0)
    red = int(0)
    green = int(0)
    blue = int(0)

    def __init__(self, vals: dict[int | str, float]) -> None:
        # sorting dict
        if all(type(key) == int for key in vals.keys()):
            vals = dict(sorted(vals.items()))
        else:
            vals = dict(sorted(list(vals.items()), key=lambda item: str(item[0])))
        for key in vals:
            # if a decode function exists in col_attr_transform, decode the value accordingly
            value = vals[key]
            if compress_type(key) in col_attr_transform:
                value = col_attr_transform[compress_type(key)]["decode"](vals[key])
            # if numerical key exists in col_attr_map, convert it into its mapped name
            if compress_type(key) in col_attr_map:
                setattr(
                    self,
                    col_attr_map[compress_type(key)].name,
                    col_attr_map[compress_type(key)].type(value),
                )
            else:
                setattr(self, str(key), value)
        assert set([col_attr_map[i].name for i in [1, 2, 3, 6]]).issubset(self.__dict__)

    # for human readable printing
    def __str__(self) -> str:
        excludes = [
            str(key) for key in [8, 11, 12, 13, 15, 18]
        ]  # I have 0 clue what these attribute IDs represent; they seem like artifacts
        return (
            "col (ID {0})".format(self.ID if self.ID not in special_col_map else special_col_map[self.ID])
            + ": { "
            + ", ".join(
                [
                    "{0}: {1}".format(key, str(getattr(self, key)))
                    for key in self.__dict__
                    if key != "ID" and key not in excludes  # ignore anything in the excludes
                ]
            )
            + " }"
        )

    # for printing into GD's internal format
    def compress(self) -> str:
        col_attrs = []
        for key in self.__dict__:
            value = getattr(self, key)
            if type(value) == bool:
                value = 1 if value else 0

            # if the name of an attribute exists in col_attr_map, convert it back to its number counterpart
            # else leave as unchanged key val
            mapkey = next((mkey for mkey in col_attr_map if col_attr_map[mkey].name == key), key)

            # if we decoded it above, encode it back again
            if mapkey in col_attr_transform:
                value = col_attr_transform[mapkey]["encode"](value)

            col_attrs.append("{0}_{1}".format(mapkey, value))
        return "_".join(col_attrs)


# representing a level in GD as a collection of colors and objects
class gdLevel:
    def __init__(self, objs: list[gdObject], cols: list[gdColor], headers: str) -> None:
        self.objs = objs
        self.objs.sort(key=lambda obj: (getattr(obj, "x"), getattr(obj, "y"), getattr(obj, "ID")))
        self.cols = cols
        self.cols.sort(key=lambda col: col.ID)
        self.headers = headers

    # for human readable printing
    def __str__(self) -> str:
        return self.cols_printable() + "\n" + self.objs_printable()

    # for printing into GD's internal format
    def compress(self) -> str:
        return (
            "kS38,"
            + "".join([col.compress() + "|" for col in self.cols])
            + self.headers
            + "".join([obj.compress() + ";" for obj in self.objs])
        )

    # modifying all objects in place
    def map(self, func: Callable[[gdObject], None], filter: Callable[[gdObject], bool] = None):
        for obj in self.objs:
            if filter == None or (filter != None and filter(obj)):  # if filter is present and object passes filter
                func(obj)

    # returns a string of exclusively the objects within the level
    def objs_printable(self, filter: Callable[[gdObject], bool] = None) -> str:
        self.objs.sort(key=lambda obj: (getattr(obj, "x"), getattr(obj, "y"), getattr(obj, "ID")))
        return "\n".join([obj.__str__() for obj in self.objs if filter == None or filter(obj)])

    # returns a string of exclusively the colors within the level
    def cols_printable(self, filter: Callable[[gdColor], bool] = None) -> str:
        self.cols.sort(key=lambda col: col.ID)
        return "\n".join([col.__str__() for col in self.cols if filter == None or filter(col)])

    # returns the information for a specific color channel if available, else returns the default white
    def get_color_channel(self, val: int) -> gdColor:
        next_col = next(filter(lambda col: col.ID == val, self.cols), None)
        if next_col != None:
            return next_col
        else: # if no color found, return a default value
            return gdColor(
                {
                    "ID": val,
                    "red": 255,
                    "green": 255,
                    "blue": 255,
                    "player-color": -1,
                    "blending": False,
                    "opacity": 1,
                    8: 1,
                    11: 255,
                    12: 255,
                    13: 255,
                    15: 1,
                    18: 0,
                }
            )

# convert level string to level object
def extract_level(lvlstring: str) -> gdLevel:
    # converting objects part of string into objects list
    objs_as_string = lvlstring.split(";")[1:-1]
    objs = []
    for obj_str in objs_as_string:
        split_obj_str = obj_str.split(",")
        objs.append(
            gdObject(
                dict(
                    zip(
                        list(map(compress_type, split_obj_str[::2])),
                        split_obj_str[1::2],
                    )
                )
            )
        )
    objs.sort(key=lambda obj: (getattr(obj, "x"), getattr(obj, "y"), getattr(obj, "ID")))

    # converting colors part of string into color list
    cols_as_string = lvlstring[lvlstring.index("kS38,") + 5 : lvlstring.index(",kA13") - 1].split("|")
    cols = []
    for col_str in cols_as_string:
        split_col_str = col_str.split("_")
        cols.append(
            gdColor(
                dict(
                    zip(
                        list(map(compress_type, split_col_str[::2])),
                        split_col_str[1::2],
                    )
                )
            )
        )
    cols.sort(key=lambda col: col.ID)

    # preserving level headers
    headers = lvlstring[lvlstring.rfind("|") + 1 : lvlstring.find(";") + 1]

    return gdLevel(objs, cols, headers)


# mapping a numeric ID of an object to a named attribute with a specific type
# notes about naming convention:
# 1. if an attribute is used only by triggers, the first word is trigger
# 2. if an attribute is used by a particular trigger, the second word will name that trigger
obj_attr_map = {
    1: gdAttribute("ID", int),
    2: gdAttribute("x", float),
    3: gdAttribute("y", float),
    4: gdAttribute("flip-horizontal", bool),
    5: gdAttribute("flip-vertical", bool),
    6: gdAttribute("rotation", int),
    7: gdAttribute("trigger-color-red", int),
    8: gdAttribute("trigger-color-green", int),
    9: gdAttribute("trigger-color-blue", int),
    10: gdAttribute("trigger-time", float),
    11: gdAttribute("trigger-touch-enable", bool),
    15: gdAttribute("trigger-playercol-1", bool),
    16: gdAttribute("trigger-playercol-2", bool),
    17: gdAttribute("trigger-color-blending", bool),
    20: gdAttribute("editor-layer", int),
    21: gdAttribute("color", int),
    22: gdAttribute("color-secondary", int),
    23: gdAttribute("trigger-color-target", int),
    24: gdAttribute("z-layer", int),
    25: gdAttribute("z-layer-sub", int),
    28: gdAttribute("trigger-move-x", int),
    29: gdAttribute("trigger-move-y", int),
    30: gdAttribute("trigger-move-easing", int),
    31: gdAttribute("text", str),
    32: gdAttribute("scale", float),
    34: gdAttribute("group-parent", bool),
    35: gdAttribute("trigger-opacity", float),
    36: gdAttribute("trigger", bool),
    41: gdAttribute("hsv-enable", bool),
    43: gdAttribute("hsv", tuple[int, float, float, bool, bool]),
    45: gdAttribute("trigger-pulse-fade-in", float),
    46: gdAttribute("trigger-pulse-hold", float),
    47: gdAttribute("trigger-pulse-fade-out", float),
    48: gdAttribute("trigger-pulse-hsv-enable", bool),
    49: gdAttribute("trigger-hsv", tuple[int, float, float, bool, bool]),
    50: gdAttribute("trigger-copy-target", int),
    51: gdAttribute("trigger-group-target", int),
    52: gdAttribute("trigger-pulse-group-target", bool),
    54: gdAttribute("teleport-out", float),
    57: gdAttribute("groups", list[int]),
    62: gdAttribute("trigger-spawn-enable", bool),
    85: gdAttribute("trigger-move-easing-rate", float),
    86: gdAttribute("trigger-pulse-exclusive", bool),
    87: gdAttribute("trigger-spawn-multi-enable", bool),
    108: gdAttribute("link", int),
}

# mapping a numeric ID of a color to a named attribute with a specific type
col_attr_map = {
    1: gdAttribute("red", int),
    2: gdAttribute("green", int),
    3: gdAttribute("blue", int),
    4: gdAttribute("player-color", int),
    5: gdAttribute("blending", bool),
    6: gdAttribute("ID", int),
    7: gdAttribute("opacity", float),
    9: gdAttribute("copy-target", int),
    10: gdAttribute("copy-hsv", tuple[float, float, float, bool, bool]),
    17: gdAttribute("copy-opacity", bool),
}

# colors that represent unique attributes for the level (generally above 1000)
special_col_map = {
    1000: "BG",
    1001: "G1",
    1002: "LINE",
    1003: "3DL",
    1004: "OBJ",
    1005: "P1",
    1006: "P2",
    1007: "LBG",
    1009: "G2",
    1010: "BLACK",
    1011: "WHITE",
    1012: "LIGHTER",
}

# transformation for any object attributes that need additional processing
# decode is for transforming levelstring -> object, encode is for transforming object -> levelstring
obj_attr_transform = {
    31: {
        "decode": lambda string: b64.b64decode(string).decode(),
        "encode": lambda string: b64.b64encode(bytes(string, "utf-8")).decode(),
    },
    43: {
        "decode": lambda string: attr_delta.decode_hsv(string),
        "encode": lambda tuple_: attr_delta.encode_hsv(tuple_),
    },
    49: {
        "decode": lambda string: attr_delta.decode_hsv(string),
        "encode": lambda tuple_: attr_delta.encode_hsv(tuple_),
    },
    57: {
        "decode": lambda string: [int(num) for num in string.split(".")],
        "encode": lambda array: ".".join(map(lambda num: str(num), array)),
    },
}

# transformation for any color attributes that need additional processing
# decode is for transforming levelstring -> color, encode is for transforming color -> levelstring
col_attr_transform = {
    10: {"decode": lambda string: attr_delta.decode_hsv(string), "encode": lambda array: attr_delta.encode_hsv(array)},
}


# convert level object to level string
def compress_level(lvl: gdLevel) -> str:
    return lvl.compress()


# converts value to float if possible, then to integer if possible, otherwise string
def compress_type(val):
    if type(val) in [int, float, str]:
        try:
            float(val)
        except ValueError:
            return val
        else:
            if float(val).is_integer():
                return int(val)
            else:
                return float(val)
    else:
        return val
