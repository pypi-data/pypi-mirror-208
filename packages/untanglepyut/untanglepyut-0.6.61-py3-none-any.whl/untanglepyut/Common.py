
from typing import List
from typing import NewType

from dataclasses import dataclass

from untangle import Element

from miniogl.ControlPoint import ControlPoint

from untanglepyut.Types import UntangledOglActors
from untanglepyut.Types import UntangledOglLinks
from untanglepyut.Types import UntangledOglUseCases

UntangledControlPoints = NewType('UntangledControlPoints', List[ControlPoint])

Elements = NewType('Elements', List[Element])

@dataclass
class GraphicInformation:
    """
    Internal Class use to move information from a Graphic XML element
    into Python
    """
    x: int = -1
    y: int = -1
    width:  int = -1
    height: int = -1


"""
Factory methods for our dataclasses
"""


def createUntangledOglLinks() -> UntangledOglLinks:
    return UntangledOglLinks([])


def createUntangledOglUseCases() -> UntangledOglUseCases:
    return UntangledOglUseCases([])


def createUntangledOglActors() -> UntangledOglActors:
    return UntangledOglActors([])


def str2bool(strValue: str) -> bool:
    """
    Converts a known set of strings to a boolean value

    TODO: Put in common place;  Also, in UnTanglePyut

    Args:
        strValue:

    Returns:  the boolean value
    """
    return strValue.lower() in ("yes", "true", "t", "1", 'True')


def secureInteger(x: str):
    if x is not None and x != '':
        return int(x)
    else:
        return 0


def toGraphicInfo(graphicElement: Element) -> GraphicInformation:
    graphicInformation: GraphicInformation = GraphicInformation()

    graphicInformation.x = int(graphicElement['x'])
    graphicInformation.y = int(graphicElement['y'])

    graphicInformation.width  = int(graphicElement['width'])
    graphicInformation.height = int(graphicElement['height'])

    return graphicInformation
