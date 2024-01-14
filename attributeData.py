import base64 as b64
import objectAttributeTransformation as attr_delta

# representing a singular attribute of a GD object (with designated type restrictions)
class gdAttribute:
    def __init__(self, name: str, type_: type) -> None:
        self.name = name
        self.type = type_

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