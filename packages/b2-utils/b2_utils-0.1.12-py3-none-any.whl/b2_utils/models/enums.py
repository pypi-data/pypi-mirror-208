import operator as _operator
from enum import Enum as _Enum
from typing import Callable as _Callable

from django.db import models as _models
from django.db.models import enums as _enums

__all__ = [
    "States",
    "Colors",
    "Operator",
    "OrderedTextChoices",
]


class Operator(_Enum):
    LT = _operator.lt
    GT = _operator.gt
    LTE = _operator.le
    GTE = _operator.ge


class OrderedTextChoices(_models.TextChoices):
    """Class for creating enumerated string choices, establishing hierarchy between the
    values. Lowest members has higher values than the highest, then, you can compare
    the two using compare method::

        from b2_utils.models import Operator, OrderedTextChoices

        class Role(OrderedTextChoices):
            SUPPORT = "SUPPORT", "Support"
            MANAGER = "MANAGER", "Manager"
            ADMIN = "ADMIN", "Admin"

        Role.compare(Role.ADMIN, Operator.GT, Role.SUPPORT) # True
    """

    @classmethod
    def _get_value(cls, choice) -> int | None:
        for index, option in enumerate(cls.choices):
            if choice == option[0]:
                return index
        return None

    @classmethod
    def compare(cls, first, operator: Operator | _Callable, second) -> bool:
        """Compares two values from the same Enum.

        Parameters
        ---------
        first : any
            The first operand
        operator : Operator | Callable
            The operator used to make the comparison. It also can be a function, in
            that case, your function may accept receive two integers, and return a
            boolean. Eg::

            def custom_compare(a: int, b: int) -> bool:
                return b - a == 3

        second : any
            The second operand

        Returns
        -------
        bool
            A boolean which represents the result of operation between the two operands
        """
        if callable(operator):
            return operator(cls._get_value(first), cls._get_value(second))

        return operator.value(cls._get_value(first), cls._get_value(second))


class States(_enums.TextChoices):
    AC = "AC", "Acre"
    AL = "AL", "Alagoas"
    AM = "AM", "Amazonas"
    AP = "AP", "Amapá"
    BA = "BA", "Bahia"
    CE = "CE", "Ceará"
    ES = "ES", "Espírito Santo"
    GO = "GO", "Goiás"
    MA = "MA", "Maranhão"
    MG = "MG", "Minas Gerais"
    MS = "MS", "Mato Grosso do Sul"
    MT = "MT", "Mato Grosso"
    PA = "PA", "Pará"
    PB = "PB", "Paraíba"
    PE = "PE", "Pernambuco"
    PI = "PI", "Piauí"
    PR = "PR", "Paraná"
    RJ = "RJ", "Rio de Janeiro"
    RN = "RN", "Rio Grande do Norte"
    RO = "RO", "Rondônia"
    RR = "RR", "Roraima"
    RS = "RS", "Rio Grande do Sul"
    SC = "SC", "Santa Catarina"
    SE = "SE", "Sergipe"
    SP = "SP", "São Paulo"
    TO = "TO", "Tocantins"
    DF = "DF", "Distrito Federal"


class Colors(_enums.IntegerChoices):
    PINK = 0xFFC0CB, "Pink"
    HOTPINK = 0xFF69B4, "Hot Pink"
    LIGHTPINK = 0xFFB6C1, "Light Pink"
    DEEPPINK = 0xFF1493, "Deep Pink"
    PALEVIOLETRED = 0xDB7093, "Pale Violet Red"
    MEDIUMVIOLETRED = 0xC71585, "Medium Violet Red"
    LAVENDER = 0xE6E6FA, "Lavender"
    THISTLE = 0xD8BFD8, "Thistle"
    PLUM = 0xDDA0DD, "Plum"
    ORCHID = 0xDA70D6, "Orchid"
    VIOLET = 0xEE82EE, "Violet"
    MAGENTA = 0xFF00FF, "Magenta"
    MEDIUMORCHID = 0xBA55D3, "Medium Orchid"
    DARKORCHID = 0x9932CC, "Dark Orchid"
    DARKVIOLET = 0x9400D3, "Dark Violet"
    BLUEVIOLET = 0x8A2BE2, "Blue Violet"
    DARKMAGENTA = 0x8B008B, "Dark Magenta"
    PURPLE = 0x800080, "Purple"
    MEDIUMPURPLE = 0x9370DB, "Medium Purple"
    MEDIUMSLATEBLUE = 0x7B68EE, "Medium Slate Blue"
    SLATEBLUE = 0x6A5ACD, "Slate Blue"
    DARKSLATEBLUE = 0x483D8B, "Dark Slate Blue"
    REBECCAPURPLE = 0x663399, "Rebecca Purple"
    INDIGO = 0x4B0082, "Indigo"
    LIGHTSALMON = 0xFFA07A, "Light Salmon"
    SALMON = 0xFA8072, "Salmon"
    DARKSALMON = 0xE9967A, "Dark Salmon"
    LIGHTCORAL = 0xF08080, "Light Coral"
    INDIANRED = 0xCD5C5C, "Indian Red"
    CRIMSON = 0xDC143C, "Crimson"
    RED = 0xFF0000, "Red"
    FIREBRICK = 0xB22222, "Fire Brick"
    DARKRED = 0x8B0000, "DarkRed"
    ORANGE = 0xFFA500, "Orange"
    DARKORANGE = 0xFF8C00, "Dark Orange"
    CORAL = 0xFF7F50, "Coral"
    TOMATO = 0xFF6347, "Tomato"
    ORANGERED = 0xFF4500, "Orange Red"
    GOLD = 0xFFD700, "Gold"
    YELLOW = 0xFFFF00, "Yellow"
    LIGHTYELLOW = 0xFFFFE0, "Light Yellow"
    LEMONCHIFFON = 0xFFFACD, "Lemon Chiffon"
    LIGHTGOLDENRODYELLOW = 0xFAFAD2, "Light Goldenrod Yellow"
    PAPAYAWHIP = 0xFFEFD5, "Papaya Whip"
    MOCCASIN = 0xFFE4B5, "Moccasin"
    PEACHPUFF = 0xFFDAB9, "Peach Puff"
    PALEGOLDENROD = 0xEEE8AA, "Pale Goldenrod"
    KHAKI = 0xF0E68C, "Khaki"
    DARKKHAKI = 0xBD536B, "Dark Khaki"
    GREENYELLOW = 0xADFF2F, "Green Yellow"
    CHARTREUSE = 0x7FFF00, "Chartreuse"
    LAWNGREEN = 0x7CFC00, "Lawn Green"
    LIME = 0x00FF00, "Lime"
    LIMEGREEN = 0x32CD32, "Lime Green"
    PALEGREEN = 0x98FB98, "Pale Green"
    LIGHTGREEN = 0x90EE90, "Light Green"
    MEDIUMSPRINGGREEN = 0x00FA9A, "Medium Spring Green"
    SPRINGGREEN = 0x00FF7F, "Spring Green"
    MEDIUMSEAGREEN = 0x3CB371, "Medium Sea Green"
    SEAGREEN = 0x2E8B57, "Sea Green"
    FORESTGREEN = 0x228B22, "Forest Green"
    GREEN = 0x008000, "Green"
    DARKGREEN = 0x006400, "Dark Green"
    YELLOWGREEN = 0x9ACD32, "Yellow Green"
    OLIVEDRAB = 0x6B8E23, "Olive Drab"
    DARKOLIVEGREEN = 0x556B2F, "Dark Olive Green"
    MEDIUMAQUAMARINE = 0x66CDAA, "Medium Aquamarine"
    DARKSEAGREEN = 0x8FBC8F, "Dark Sea Green"
    LIGHTSEAGREEN = 0x20B2AA, "Light Sea Green"
    DARKCYAN = 0x008B8B, "Dark Cyan"
    TEAL = 0x008080, "Teal"
    CYAN = 0x00FFFF, "Cyan"
    LIGHTCYAN = 0xE0FFFF, "Light Cyan"
    PALETURQUOISE = 0xAFEEEE, "Pale Turquoise"
    AQUAMARINE = 0x7FFFD4, "Aquamarine"
    TURQUOISE = 0x40E0D0, "Turquoise"
    MEDIUMTURQUOISE = 0x48D1CC, "Medium Turquoise"
    DARKTURQUOISE = 0x00CED1, "Dark Turquoise"
    CADETBLUE = 0x5F9EA0, "Cadet Blue"
    STEELBLUE = 0x4682B4, "Steel Blue"
    LIGHTSTEELBLUE = 0xB0C4DE, "Light Steel Blue"
    LIGHTBLUE = 0xADD8E6, "Light Blue"
    POWDERBLUE = 0xB0E0E6, "Powder Blue"
    LIGHTSKYBLUE = 0x87CEFA, "Light Sky Blue"
    SKYBLUE = 0x87CEEB, "Sky Blue"
    CORNFLOWERBLUE = 0x6495ED, "Cornflower Blue"
    DEEPSKYBLUE = 0x00BFFF, "Deep Sky Blue"
    DODGERBLUE = 0x1E90FF, "Dodger Blue"
    ROYALBLUE = 0x4169E1, "Royal Blue"
    BLUE = 0x0000FF, "Blue"
    MEDIUMBLUE = 0x0000CD, "Medium Blue"
    DARKBLUE = 0x00008B, "Dark Blue"
    NAVY = 0x000080, "Navy"
    MIDNIGHTBLUE = 0x191970, "Midnight Blue"
    CORNSILK = 0xFFF8DC, "Cornsilk"
    BLANCHEDALMOND = 0xFFEBCD, "Blanched Almond"
    BISQUE = 0xFFE4C4, "Bisque"
    NAVAJOWHITE = 0xFFDEAD, "Navajo White"
    WHEAT = 0xF5DEB3, "Wheat"
    BURLYWOOD = 0xDEB887, "Burly Wood"
    TAN = 0xD2B48C, "Tan"
    ROSYBROWN = 0xBC8F8F, "Rosy Brown"
    SANDYBROWN = 0xF4A460, "Sandy Brown"
    GOLDENROD = 0xDAA520, "Goldenrod"
    DARKGOLDENROD = 0xB8860B, "Dark Goldenrod"
    PERU = 0xCD853F, "Peru"
    CHOCOLATE = 0xD2691E, "Chocolate"
    OLIVE = 0x808000, "Olive"
    SADDLEBROWN = 0x8B4513, "Saddle Brown"
    SIENNA = 0xA0522D, "Sienna"
    BROWN = 0xA52A2A, "Brown"
    MAROON = 0x800000, "Maroon"
    WHITE = 0xFFFFFF, "White"
    SNOW = 0xFFFAFA, "Snow"
    HONEYDEW = 0xF0FFF0, "Honeydew"
    MINTCREAM = 0xF5FFFA, "Mint Cream"
    AZURE = 0xF0FFFF, "Azure"
    ALICEBLUE = 0xF0F8FF, "Alice Blue"
    GHOSTWHITE = 0xF8F8FF, "Ghost White"
    WHITESMOKE = 0xF5F5F5, "White Smoke"
    SEASHELL = 0xFFF5EE, "Seashell"
    BEIGE = 0xF5F5DC, "Beige"
    OLDLACE = 0xFDF5E6, "Old Lace"
    FLORALWHITE = 0xFFFAF0, "Floral White"
    IVORY = 0xFFFFF0, "Ivory"
    ANTIQUEWHITE = 0xFAEBD7, "Antique White"
    LINEN = 0xFAF0E6, "Linen"
    LAVENDERBLUSH = 0xFFF0F5, "Lavender Blush"
    MISTYROSE = 0xFFE4E1, "Misty Rose"
    GAINSBORO = 0xDCDCDC, "Gainsboro"
    LIGHTGRAY = 0xD3D3D3, "Light Gray"
    SILVER = 0xC0C0C0, "Silver"
    DARKGRAY = 0xA9A9A9, "Dark Gray"
    DIMGRAY = 0x696969, "Dim Gray"
    GRAY = 0x808080, "Gray"
    LIGHTSLATEGRAY = 0x778899, "Light Slate Gray"
    SLATEGRAY = 0x708090, "Slate Gray"
    DARKSLATEGRAY = 0x2F4F4F, "Dark Slate Gray"
    BLACK = 0x000000, "Black"
