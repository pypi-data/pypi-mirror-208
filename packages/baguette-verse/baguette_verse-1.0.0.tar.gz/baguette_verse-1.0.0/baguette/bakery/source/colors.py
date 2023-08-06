"""
This module defines colors to be used for graphs.
"""

from typing import Any, Iterable, Iterator, Tuple, Union

__all__ = ["chart", "Color"]





__chart_init = {
    'black' : (0.0, 0.0, 0.0),
    'navy' : (0.0, 0.0, 0.5019607843137255),
    'darkblue' : (0.0, 0.0, 0.5450980392156862),
    'mediumblue' : (0.0, 0.0, 0.803921568627451),
    'blue' : (0.0, 0.0, 1.0),
    'darkgreen' : (0.0, 0.39215686274509803, 0.0),
    'green' : (0.0, 0.5019607843137255, 0.0),
    'teal' : (0.0, 0.5019607843137255, 0.5019607843137255),
    'darkcyan' : (0.0, 0.5450980392156862, 0.5450980392156862),
    'deepskyblue' : (0.0, 0.7490196078431373, 1.0),
    'darkturquoise' : (0.0, 0.807843137254902, 0.8196078431372549),
    'mediumspringgreen' : (0.0, 0.9803921568627451, 0.6039215686274509),
    'lime' : (0.0, 1.0, 0.0),
    'springgreen' : (0.0, 1.0, 0.4980392156862745),
    'cyan' : (0.0, 1.0, 1.0),
    'midnightblue' : (0.09803921568627451, 0.09803921568627451, 0.4392156862745098),
    'dodgerblue' : (0.11764705882352941, 0.5647058823529412, 1.0),
    'lightseagreen' : (0.12549019607843137, 0.6980392156862745, 0.6666666666666666),
    'forestgreen' : (0.13333333333333333, 0.5450980392156862, 0.13333333333333333),
    'seagreen' : (0.1803921568627451, 0.5450980392156862, 0.3411764705882353),
    'darkslategrey' : (0.1843137254901961, 0.30980392156862746, 0.30980392156862746),
    'limegreen' : (0.19607843137254902, 0.803921568627451, 0.19607843137254902),
    'mediumseagreen' : (0.23529411764705882, 0.7019607843137254, 0.44313725490196076),
    'turquoise' : (0.25098039215686274, 0.8784313725490196, 0.8156862745098039),
    'royalblue' : (0.2549019607843137, 0.4117647058823529, 0.8823529411764706),
    'steelblue' : (0.27450980392156865, 0.5098039215686274, 0.7058823529411765),
    'darkslateblue' : (0.2823529411764706, 0.23921568627450981, 0.5450980392156862),
    'mediumturquoise' : (0.2823529411764706, 0.8196078431372549, 0.8),
    'indigo' : (0.29411764705882354, 0.0, 0.5098039215686274),
    'darkolivegreen' : (0.3333333333333333, 0.4196078431372549, 0.1843137254901961),
    'cadetblue' : (0.37254901960784315, 0.6196078431372549, 0.6274509803921569),
    'cornflowerblue' : (0.39215686274509803, 0.5843137254901961, 0.9294117647058824),
    'rebeccapurple' : (0.4, 0.2, 0.6),
    'mediumaquamarine' : (0.4, 0.803921568627451, 0.6666666666666666),
    'dimgrey' : (0.4117647058823529, 0.4117647058823529, 0.4117647058823529),
    'slateblue' : (0.41568627450980394, 0.35294117647058826, 0.803921568627451),
    'olivedrab' : (0.4196078431372549, 0.5568627450980392, 0.13725490196078433),
    'slategrey' : (0.4392156862745098, 0.5019607843137255, 0.5647058823529412),
    'lightslategrey' : (0.4666666666666667, 0.5333333333333333, 0.6),
    'mediumslateblue' : (0.4823529411764706, 0.40784313725490196, 0.9333333333333333),
    'lawngreen' : (0.48627450980392156, 0.9882352941176471, 0.0),
    'chartreuse' : (0.4980392156862745, 1.0, 0.0),
    'aquamarine' : (0.4980392156862745, 1.0, 0.8313725490196079),
    'maroon' : (0.5019607843137255, 0.0, 0.0),
    'purple' : (0.5019607843137255, 0.0, 0.5019607843137255),
    'olive' : (0.5019607843137255, 0.5019607843137255, 0.0),
    'grey' : (0.5019607843137255, 0.5019607843137255, 0.5019607843137255),
    'skyblue' : (0.5294117647058824, 0.807843137254902, 0.9215686274509803),
    'lightskyblue' : (0.5294117647058824, 0.807843137254902, 0.9803921568627451),
    'blueviolet' : (0.5411764705882353, 0.16862745098039217, 0.8862745098039215),
    'darkred' : (0.5450980392156862, 0.0, 0.0),
    'darkmagenta' : (0.5450980392156862, 0.0, 0.5450980392156862),
    'saddlebrown' : (0.5450980392156862, 0.27058823529411763, 0.07450980392156863),
    'darkseagreen' : (0.5607843137254902, 0.7372549019607844, 0.5607843137254902),
    'lightgreen' : (0.5647058823529412, 0.9333333333333333, 0.5647058823529412),
    'mediumpurple' : (0.5764705882352941, 0.4392156862745098, 0.8588235294117647),
    'darkviolet' : (0.5803921568627451, 0.0, 0.8274509803921568),
    'palegreen' : (0.596078431372549, 0.984313725490196, 0.596078431372549),
    'darkorchid' : (0.6, 0.19607843137254902, 0.8),
    'yellowgreen' : (0.6039215686274509, 0.803921568627451, 0.19607843137254902),
    'sienna' : (0.6274509803921569, 0.3215686274509804, 0.17647058823529413),
    'brown' : (0.6470588235294118, 0.16470588235294117, 0.16470588235294117),
    'darkgrey' : (0.6627450980392157, 0.6627450980392157, 0.6627450980392157),
    'lightblue' : (0.6784313725490196, 0.8470588235294118, 0.9019607843137255),
    'greenyellow' : (0.6784313725490196, 1.0, 0.1843137254901961),
    'paleturquoise' : (0.6862745098039216, 0.9333333333333333, 0.9333333333333333),
    'lightsteelblue' : (0.6901960784313725, 0.7686274509803922, 0.8705882352941177),
    'powderblue' : (0.6901960784313725, 0.8784313725490196, 0.9019607843137255),
    'firebrick' : (0.6980392156862745, 0.13333333333333333, 0.13333333333333333),
    'darkgoldenrod' : (0.7215686274509804, 0.5254901960784314, 0.043137254901960784),
    'mediumorchid' : (0.7294117647058823, 0.3333333333333333, 0.8274509803921568),
    'rosybrown' : (0.7372549019607844, 0.5607843137254902, 0.5607843137254902),
    'darkkhaki' : (0.7411764705882353, 0.7176470588235294, 0.4196078431372549),
    'silver' : (0.7529411764705882, 0.7529411764705882, 0.7529411764705882),
    'mediumvioletred' : (0.7803921568627451, 0.08235294117647059, 0.5215686274509804),
    'indianred' : (0.803921568627451, 0.3607843137254902, 0.3607843137254902),
    'peru' : (0.803921568627451, 0.5215686274509804, 0.24705882352941178),
    'chocolate' : (0.8235294117647058, 0.4117647058823529, 0.11764705882352941),
    'tan' : (0.8235294117647058, 0.7058823529411765, 0.5490196078431373),
    'lightgrey' : (0.8274509803921568, 0.8274509803921568, 0.8274509803921568),
    'thistle' : (0.8470588235294118, 0.7490196078431373, 0.8470588235294118),
    'orchid' : (0.8549019607843137, 0.4392156862745098, 0.8392156862745098),
    'goldenrod' : (0.8549019607843137, 0.6470588235294118, 0.12549019607843137),
    'palevioletred' : (0.8588235294117647, 0.4392156862745098, 0.5764705882352941),
    'crimson' : (0.8627450980392157, 0.0784313725490196, 0.23529411764705882),
    'gainsboro' : (0.8627450980392157, 0.8627450980392157, 0.8627450980392157),
    'plum' : (0.8666666666666667, 0.6274509803921569, 0.8666666666666667),
    'burlywood' : (0.8705882352941177, 0.7215686274509804, 0.5294117647058824),
    'lightcyan' : (0.8784313725490196, 1.0, 1.0),
    'lavender' : (0.9019607843137255, 0.9019607843137255, 0.9803921568627451),
    'darksalmon' : (0.9137254901960784, 0.5882352941176471, 0.47843137254901963),
    'violet' : (0.9333333333333333, 0.5098039215686274, 0.9333333333333333),
    'palegoldenrod' : (0.9333333333333333, 0.9098039215686274, 0.6666666666666666),
    'lightcoral' : (0.9411764705882353, 0.5019607843137255, 0.5019607843137255),
    'khaki' : (0.9411764705882353, 0.9019607843137255, 0.5490196078431373),
    'aliceblue' : (0.9411764705882353, 0.9725490196078431, 1.0),
    'honeydew' : (0.9411764705882353, 1.0, 0.9411764705882353),
    'azure' : (0.9411764705882353, 1.0, 1.0),
    'sandybrown' : (0.9568627450980393, 0.6431372549019608, 0.3764705882352941),
    'wheat' : (0.9607843137254902, 0.8705882352941177, 0.7019607843137254),
    'beige' : (0.9607843137254902, 0.9607843137254902, 0.8627450980392157),
    'whitesmoke' : (0.9607843137254902, 0.9607843137254902, 0.9607843137254902),
    'mintcream' : (0.9607843137254902, 1.0, 0.9803921568627451),
    'ghostwhite' : (0.9725490196078431, 0.9725490196078431, 1.0),
    'salmon' : (0.9803921568627451, 0.5019607843137255, 0.4470588235294118),
    'antiquewhite' : (0.9803921568627451, 0.9215686274509803, 0.8431372549019608),
    'linen' : (0.9803921568627451, 0.9411764705882353, 0.9019607843137255),
    'lightgoldenrodyellow' : (0.9803921568627451, 0.9803921568627451, 0.8235294117647058),
    'oldlace' : (0.9921568627450981, 0.9607843137254902, 0.9019607843137255),
    'red' : (1.0, 0.0, 0.0),
    'magenta' : (1.0, 0.0, 1.0),
    'deeppink' : (1.0, 0.0784313725490196, 0.5764705882352941),
    'orangered' : (1.0, 0.27058823529411763, 0.0),
    'tomato' : (1.0, 0.38823529411764707, 0.2784313725490196),
    'hotpink' : (1.0, 0.4117647058823529, 0.7058823529411765),
    'coral' : (1.0, 0.4980392156862745, 0.3137254901960784),
    'darkorange' : (1.0, 0.5490196078431373, 0.0),
    'lightsalmon' : (1.0, 0.6274509803921569, 0.47843137254901963),
    'orange' : (1.0, 0.6470588235294118, 0.0),
    'lightpink' : (1.0, 0.7137254901960784, 0.7568627450980392),
    'pink' : (1.0, 0.7529411764705882, 0.796078431372549),
    'gold' : (1.0, 0.8431372549019608, 0.0),
    'peachpuff' : (1.0, 0.8549019607843137, 0.7254901960784313),
    'navajowhite' : (1.0, 0.8705882352941177, 0.6784313725490196),
    'moccasin' : (1.0, 0.8941176470588236, 0.7098039215686275),
    'bisque' : (1.0, 0.8941176470588236, 0.7686274509803922),
    'mistyrose' : (1.0, 0.8941176470588236, 0.8823529411764706),
    'blanchedalmond' : (1.0, 0.9215686274509803, 0.803921568627451),
    'papayawhip' : (1.0, 0.9372549019607843, 0.8352941176470589),
    'lavenderblush' : (1.0, 0.9411764705882353, 0.9607843137254902),
    'seashell' : (1.0, 0.9607843137254902, 0.9333333333333333),
    'cornsilk' : (1.0, 0.9725490196078431, 0.8627450980392157),
    'lemonchiffon' : (1.0, 0.9803921568627451, 0.803921568627451),
    'floralwhite' : (1.0, 0.9803921568627451, 0.9411764705882353),
    'snow' : (1.0, 0.9803921568627451, 0.9803921568627451),
    'yellow' : (1.0, 1.0, 0.0),
    'lightyellow' : (1.0, 1.0, 0.8784313725490196),
    'ivory' : (1.0, 1.0, 0.9411764705882353),
    'white' : (1.0, 1.0, 1.0)
}

chart : dict[str, "Color"] = {}





class ColorType(type):

    """
    This is the class for the Color class. It allows to find colors by name.
    """

    def __getattribute__(self, name: str) -> "Color":
        """
        Implements getattr(Color, name).
        """
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in chart:
                return chart[name]
            else:
                raise AttributeError("type object " + repr(super().__getattribute__("__name__")) + " has no attribute " + repr(name))
            
    def __dir__(self) -> list[str]:
        """
        Implements dir(Color).
        """
        return list(super().__dir__()) + list(chart)





class Color(metaclass = ColorType):

    """
    This class is used to describe colors.
    """

    __slots__ = ("R", "G", "B")

    def __new__(cls: type, r : int | float, g : int | float, b : int | float) -> "Color":
        if not isinstance(r, int | float) or not isinstance(g, int | float) or not isinstance(b, int | float):
            raise TypeError("Expected three int or float, got " + repr(r.__class__.__name__) + ", " + repr(g.__class__.__name__) + " and " + repr(b.__class__.__name__))
        if isinstance(r, int) and isinstance(g, int) and isinstance(b, int):
            r, g, b = r / 255, g / 255, b / 255
        r, g, b = float(r), float(g), float(b)
        for name, value in chart.items():
            if isinstance(value, Color) and (value.R, value.G, value.B) == (r, g, b):
                return value
        return super().__new__(cls)


    def __init__(self, r : int | float, g : int | float, b : int | float) -> None:
        if isinstance(r, int) and isinstance(g, int) and isinstance(b, int):
            r, g, b = r / 255, g / 255, b / 255
        r, g, b = float(r), float(g), float(b)
        if not 0 <= r <= 1 or not 0 <= g <= 1 or not 0 <= b <= 1:
            raise ValueError("Colors must be between 0.0 and 1.0 (or all integers between 0 and 255)")
        self.R, self.G, self.B = r, g, b
    

    def __str__(self) -> str:
        """
        Implements str(self).
        """
        for name, value in chart.items():
            if Color(value.R, value.G, value.B) == self:
                return "Color." + name
        return "Color" + str((self.R, self.G, self.B))
    

    __repr__ = __str__
    

    def __eq__(self, o: object) -> bool:
        """
        Implements self == o.
        """
        if not isinstance(o, Color):
            return False
        return (self.R, self.G, self.B) == (o.R, o.G, o.B)
    

    def __hash__(self) -> int:
        """
        Implements hash(self).
        """
        return hash((self.R, self.G, self.G))

    
    def __pos__(self) -> "Color":
        """
        Implements +self.
        """
        return Color(self.R, self.G, self.B)
    

    def __neg__(self) -> "Color":
        """
        Implements -self.
        """
        return Color(1.0 - self.R, 1.0 - self.G, 1.0 - self.B)

    
    def __add__(self, o : "Color") -> "Color":
        """
        Implements self + o.
        """
        if not isinstance(o, Color):
            return NotImplemented
        return Color(min(self.R + o.R, 1.0), min(self.G + o.G, 1.0), min(self.B + o.B, 1.0))
    

    def __sub__(self, o : "Color") -> "Color":
        """
        Implements self - o.
        """
        if not isinstance(o, Color):
            return NotImplemented
        return Color(max(self.R - o.R, 0.0), max(self.G - o.G, 0.0), max(self.B - o.B, 0.0))


    def __mul__(self, o : Union["Color", float]) -> "Color":
        """
        Implements self * o.
        """
        if isinstance(o, int | float):
            return Color(min(1.0, max(0.0, self.R * o)), min(1.0, max(0.0, self.G * o)), min(1.0, max(0.0, self.B * o)))
        elif isinstance(o, Color):
            return Color(min(1.0, max(0.0, self.R * o.R)), min(1.0, max(0.0, self.G * o.G)), min(1.0, max(0.0, self.B * o.B)))
        else:
            return NotImplemented
    

    def __rmul__(self, o : Union["Color", float]) -> "Color":
        """
        Implements o * self.
        """
        if isinstance(o, int | float):
            return Color(min(1.0, max(0.0, o * self.R)), min(1.0, max(0.0, o * self.G)), min(1.0, max(0.0, o * self.B)))
        else:
            return NotImplemented


    def __pow__(self, o : float) -> "Color":
        """
        Implements self ** o.
        """
        if isinstance(o, int | float):
            return Color(min(1.0, max(0.0, self.R ** o)), min(1.0, max(0.0, self.G ** o)), min(1.0, max(0.0, self.B ** o)))
        else:
            return NotImplemented
        

    def negative_to(self, ref : "Color") -> "Color":
        """
        Returns the negative of this color relative to another color. (Equivalent to -self relatively to any whitescale color)
        """
        if not isinstance(ref, Color):
            raise TypeError(f"Exepcted Color, got '{type(ref).__name__}'")
        M = Color(0.5, 0.5, 0.5)
        if ref == M:
            raise ZeroDivisionError(f"Cannot compute negative relative to central Color ({M})")
        SM : tuple[float, float, float] = tuple(Mi - Si for Mi, Si in zip(M, self))
        RM : tuple[float, float, float] = tuple(Mi - Ri for Mi, Ri in zip(M, ref))
        fact = 2 * sum(a * b for a, b in zip(SM, RM)) / sum(b ** 2 for b in RM)
        return Color(*(max(min(Si + fact * RMi, 1.0), 0.0) for Si, RMi in zip(self, RM)))


    def __iter__(self) -> Iterator[float]:
        """
        Implements iter(self).
        """
        yield self.R
        yield self.G
        yield self.B

    
    def to_int(self) -> Tuple[int, int, int]:
        """
        Returns a tuple of three integers representing the color.
        """
        return (round(self.R * 255), round(self.G * 255), round(self.B * 255))
    

    def __reduce__(self) -> str | tuple[Any, ...]:
        """
        Implements dump(self).
        """
        return Color, (self.R, self.G, self.B)
    
    @staticmethod
    def average(*colors : "Color") -> "Color":
        """
        Returns the average of all the given colors.
        """
        R, G, B = sum(c.R for c in colors), sum(c.G for c in colors), sum(c.B for c in colors)
        n = len(colors)
        return Color(R / n, G / n, B / n)
    
    @staticmethod
    def linear(colors : Iterable["Color"], weights : Iterable[float]) -> "Color":
        """
        Returns the linear combination of given colors with given weights as a new color.
        """
        colors, weights = list(colors), list(weights)
        R, G, B = sum(c.R * w for c, w in zip(colors, weights)), sum(c.G * w for c, w in zip(colors, weights)), sum(c.B * w for c, w in zip(colors, weights))
        return Color(min(1.0, max(0.0, R)), min(1.0, max(0.0, G)), min(1.0, max(0.0, B)))





# Convert color vectors of the __chart_init to Color objects in the real chart
chart.update((name, Color(*value)) for name, value in __chart_init.items())

del Any, Tuple, Union, ColorType, Iterable, Iterator, __chart_init