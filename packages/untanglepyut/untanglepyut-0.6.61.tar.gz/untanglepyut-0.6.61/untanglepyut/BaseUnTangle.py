
from logging import Logger
from logging import getLogger

from miniogl.ShapeModel import ShapeModel
from ogl.OglObject import OglObject

from untanglepyut.Common import GraphicInformation


class BaseUnTangle:

    def __init__(self):
        self.baseLogger: Logger = getLogger(__name__)

    def _updateModel(self, oglObject: OglObject, graphicInformation: GraphicInformation) -> ShapeModel:
        """
        This is necessary if it is never added to a diagram
        and immediately serialized

        Args:
            oglObject:      OglObject with a model
            graphicInformation:   The graphic class graphic information

        Returns:  The updated shape model as a way of documenting that we updated it
        """
        model: ShapeModel = oglObject.GetModel()
        model.SetPosition(x=graphicInformation.x, y=graphicInformation.y)

        return model



