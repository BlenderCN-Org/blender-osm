"""
This file is part of blender-osm (OpenStreetMap importer for Blender).
Copyright (C) 2014-2018 Vladimir Elistratov
prokitektura+support@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Code to generate dict with CSS colors from a tuple like

colors = (
    ("aliceblue", "#F0F8FF"),
    ...
    ("yellowgreen", "#9ACD32")
)

for c in colors:
    v = list(map(lambda component: component/255, bytes.fromhex(c[1][1:])))
    print("    \"{0}\": ({1:g}, {2:g}, {3:g}),".format(c[0],round(v[0],3), round(v[1],3), round(v[2],3)))
"""

colors = {
    "aliceblue": (0.941, 0.973, 1.),
    "antiquewhite": (0.98, 0.922, 0.843),
    "aqua": (0., 1., 1.),
    "aquamarine": (0.498, 1., 0.831),
    "azure": (0.941, 1., 1.),
    "beige": (0.961, 0.961, 0.863),
    "bisque": (1., 0.894, 0.769),
    "black": (0., 0., 0.),
    "blanchedalmond": (1., 0.922, 0.804),
    "blue": (0., 0., 1.),
    "blueviolet": (0.541, 0.169, 0.886),
    "brown": (0.647, 0.165, 0.165),
    "burlywood": (0.871, 0.722, 0.529),
    "cadetblue": (0.373, 0.62, 0.627),
    "chartreuse": (0.498, 1., 0.),
    "chocolate": (0.824, 0.412, 0.118),
    "coral": (1., 0.498, 0.314),
    "cornflowerblue": (0.392, 0.584, 0.929),
    "cornsilk": (1., 0.973, 0.863),
    "crimson": (0.863, 0.078, 0.235),
    "cyan": (0., 1., 1.),
    "darkblue": (0., 0., 0.545),
    "darkcyan": (0., 0.545, 0.545),
    "darkgoldenrod": (0.722, 0.525, 0.043),
    "darkgray": (0.663, 0.663, 0.663),
    "darkgreen": (0., 0.392, 0.),
    "darkgrey": (0.663, 0.663, 0.663),
    "darkkhaki": (0.741, 0.718, 0.42),
    "darkmagenta": (0.545, 0., 0.545),
    "darkolivegreen": (0.333, 0.42, 0.184),
    "darkorange": (1., 0.549, 0.),
    "darkorchid": (0.6, 0.196, 0.8),
    "darkred": (0.545, 0., 0.),
    "darksalmon": (0.914, 0.588, 0.478),
    "darkseagreen": (0.561, 0.737, 0.561),
    "darkslateblue": (0.282, 0.239, 0.545),
    "darkslategray": (0.184, 0.31, 0.31),
    "darkslategrey": (0.184, 0.31, 0.31),
    "darkturquoise": (0., 0.808, 0.82),
    "darkviolet": (0.58, 0., 0.827),
    "deeppink": (1., 0.078, 0.576),
    "deepskyblue": (0., 0.749, 1.),
    "dimgray": (0.412, 0.412, 0.412),
    "dimgrey": (0.412, 0.412, 0.412),
    "dodgerblue": (0.118, 0.565, 1.),
    "firebrick": (0.698, 0.133, 0.133),
    "floralwhite": (1., 0.98, 0.941),
    "forestgreen": (0.133, 0.545, 0.133),
    "fuchsia": (1., 0., 1.),
    "gainsboro": (0.863, 0.863, 0.863),
    "ghostwhite": (0.973, 0.973, 1.),
    "gold": (1., 0.843, 0.),
    "goldenrod": (0.855, 0.647, 0.125),
    "gray": (0.502, 0.502, 0.502),
    "green": (0., 0.502, 0.),
    "greenyellow": (0.678, 1., 0.184),
    "grey": (0.502, 0.502, 0.502),
    "honeydew": (0.941, 1., 0.941),
    "hotpink": (1., 0.412, 0.706),
    "indianred": (0.804, 0.361, 0.361),
    "indigo": (0.294, 0., 0.51),
    "ivory": (1., 1., 0.941),
    "khaki": (0.941, 0.902, 0.549),
    "lavender": (0.902, 0.902, 0.98),
    "lavenderblush": (1., 0.941, 0.961),
    "lawngreen": (0.486, 0.988, 0.),
    "lemonchiffon": (1., 0.98, 0.804),
    "lightblue": (0.678, 0.847, 0.902),
    "lightcoral": (0.941, 0.502, 0.502),
    "lightcyan": (0.878, 1., 1.),
    "lightgoldenrodyellow": (0.98, 0.98, 0.824),
    "lightgray": (0.827, 0.827, 0.827),
    "lightgreen": (0.565, 0.933, 0.565),
    "lightgrey": (0.827, 0.827, 0.827),
    "lightpink": (1., 0.714, 0.757),
    "lightsalmon": (1., 0.627, 0.478),
    "lightseagreen": (0.125, 0.698, 0.667),
    "lightskyblue": (0.529, 0.808, 0.98),
    "lightslategray": (0.467, 0.533, 0.6),
    "lightslategrey": (0.467, 0.533, 0.6),
    "lightsteelblue": (0.69, 0.769, 0.871),
    "lightyellow": (1., 1., 0.878),
    "lime": (0., 1., 0.),
    "limegreen": (0.196, 0.804, 0.196),
    "linen": (0.98, 0.941, 0.902),
    "magenta": (1., 0., 1.),
    "maroon": (0.502, 0., 0.),
    "mediumaquamarine": (0.4, 0.804, 0.667),
    "mediumblue": (0., 0., 0.804),
    "mediumorchid": (0.729, 0.333, 0.827),
    "mediumpurple": (0.576, 0.439, 0.859),
    "mediumseagreen": (0.235, 0.702, 0.443),
    "mediumslateblue": (0.482, 0.408, 0.933),
    "mediumspringgreen": (0., 0.98, 0.604),
    "mediumturquoise": (0.282, 0.82, 0.8),
    "mediumvioletred": (0.78, 0.082, 0.522),
    "midnightblue": (0.098, 0.098, 0.439),
    "mintcream": (0.961, 1., 0.98),
    "mistyrose": (1., 0.894, 0.882),
    "moccasin": (1., 0.894, 0.71),
    "navajowhite": (1., 0.871, 0.678),
    "navy": (0., 0., 0.502),
    "oldlace": (0.992, 0.961, 0.902),
    "olive": (0.502, 0.502, 0.),
    "olivedrab": (0.42, 0.557, 0.137),
    "orange": (1., 0.647, 0.),
    "orangered": (1., 0.271, 0.),
    "orchid": (0.855, 0.439, 0.839),
    "palegoldenrod": (0.933, 0.91, 0.667),
    "palegreen": (0.596, 0.984, 0.596),
    "paleturquoise": (0.686, 0.933, 0.933),
    "palevioletred": (0.859, 0.439, 0.576),
    "papayawhip": (1., 0.937, 0.835),
    "peachpuff": (1., 0.855, 0.725),
    "peru": (0.804, 0.522, 0.247),
    "pink": (1., 0.753, 0.796),
    "plum": (0.867, 0.627, 0.867),
    "powderblue": (0.69, 0.878, 0.902),
    "purple": (0.502, 0., 0.502),
    "red": (1., 0., 0.),
    "rosybrown": (0.737, 0.561, 0.561),
    "royalblue": (0.255, 0.412, 0.882),
    "saddlebrown": (0.545, 0.271, 0.075),
    "salmon": (0.98, 0.502, 0.447),
    "sandybrown": (0.957, 0.643, 0.376),
    "seagreen": (0.18, 0.545, 0.341),
    "seashell": (1., 0.961, 0.933),
    "sienna": (0.627, 0.322, 0.176),
    "silver": (0.753, 0.753, 0.753),
    "skyblue": (0.529, 0.808, 0.922),
    "slateblue": (0.416, 0.353, 0.804),
    "slategray": (0.439, 0.502, 0.565),
    "slategrey": (0.439, 0.502, 0.565),
    "snow": (1., 0.98, 0.98),
    "springgreen": (0., 1., 0.498),
    "steelblue": (0.275, 0.51, 0.706),
    "tan": (0.824, 0.706, 0.549),
    "teal": (0., 0.502, 0.502),
    "thistle": (0.847, 0.749, 0.847),
    "tomato": (1., 0.388, 0.278),
    "turquoise": (0.251, 0.878, 0.816),
    "violet": (0.933, 0.51, 0.933),
    "wheat": (0.961, 0.871, 0.702),
    "white": (1., 1., 1.),
    "whitesmoke": (0.961, 0.961, 0.961),
    "yellow": (1., 1., 0.),
    "yellowgreen": (0.604, 0.804, 0.196)
}