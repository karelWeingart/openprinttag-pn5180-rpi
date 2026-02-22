""" Helpers for anything."""
import re
from PIL.ImageColor import colormap as PIL_COLORS
import math

_PIL_COLOR_NAME_TOKENS: list[str] = [
    "alice", "almond", "antique", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanched",
    "blue", "blush", "brick", "brown", "burly", "cadet", "chartreuse", "chiffon", "chocolate", "coral",
    "corn", "cream", "crimson", "cyan", "dark", "deep", "dew", "dim", "dodger", "drab", "fire", "floral",
    "flower", "forest", "fuchsia", "gainsboro", "ghost", "gold", "golden", "gray", "green", "grey", "honey",
    "hot", "indian", "indigo", "ivory", "khaki", "lace", "lavender", "lawn", "lemon", "light", "lime",
    "linen", "magenta", "maroon", "medium", "midnight", "mint", "misty", "moccasin", "navajo", "navy", "old",
    "olive", "orange", "orchid", "pale", "papaya", "peach", "peru", "pink", "plum", "powder", "puff",
    "purple", "rebecca", "red", "rod", "rose", "rosy", "royal", "saddle", "salmon", "sandy", "sea", "shell",
    "sienna", "silk", "silver", "sky", "slate", "smoke", "snow", "spring", "steel", "tan", "teal", "thistle",
    "tomato", "turquoise", "violet", "wheat", "whip", "white", "wood", "yellow",
]

_PIL_COLOR_NAME_TOKENS = sorted(_PIL_COLOR_NAME_TOKENS, key=len, reverse=True)

def _split_pillow_name(name: str) -> str:
    """ Parse Pillow color name into human-readable form. """
    _out: list[str] = []
    i = 0
    while i < len(name):
        for _token in _PIL_COLOR_NAME_TOKENS:
            if name.startswith(_token, i):
                _out.append(_token)
                i += len(_token)
                break
    if _out:
        return " ".join(_out)
    return name


def hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    """ Convert hex color to RGB tuple. """
    if not re.match(r"^#?[0-9a-fA-F]{6}$", hex_value):
        raise ValueError(f"Invalid hex color: {hex_value}")
    _raw_hex_value: str = hex_value.lstrip("#")
    return (
        int(_raw_hex_value[0:2], 16),
        int(_raw_hex_value[2:4], 16),
        int(_raw_hex_value[4:6], 16),
    )

def closest_color(hex_value: str) -> str:
    """ Find the closest human readable color for a given hex color. """
    try:
        _r, _g, _b = hex_to_rgb(hex_value)
    except ValueError:
        return hex_value
    _best_name: str = hex_value
    _best_dist = float("inf")

    for name, hx in PIL_COLORS.items():
        
        if isinstance(hx, str):
            _cr, _cg, _cb = hex_to_rgb(hx)
        else:
            _cr, _cg, _cb = hx

        _dist: float = math.dist((_r, _g, _b), (_cr, _cg, _cb))
        if _dist < _best_dist:
            _best_dist = _dist
            _best_name = name

    return _split_pillow_name(_best_name) if _best_name else hex_value
