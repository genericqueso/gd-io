from typing import Callable, Any
import typing, types
import re
from attributeData import obj_attr_map, col_attr_map, special_col_map, obj_attr_transform, col_attr_transform


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
                if re.match(r"^kA\d+$", key) != None:
                    # special case for (I think only) start pos
                    value = compress_type(value) != 0
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
        else:  # if no color found, return a default value
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
