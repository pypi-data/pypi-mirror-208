
from typing import List

from logging import Logger
from logging import getLogger

from untangle import Element

from pyutmodel.PyutSDInstance import PyutSDInstance
from pyutmodel.PyutSDMessage import PyutSDMessage

from ogl.sd.OglSDInstance import OglSDInstance
from ogl.sd.OglSDMessage import OglSDMessage

from untanglepyut.Types import OglSDInstances
from untanglepyut.Types import OglSDMessages

from untanglepyut.BaseUnTangle import BaseUnTangle

from untanglepyut.Common import GraphicInformation
from untanglepyut.Common import toGraphicInfo

from untanglepyut.UnTanglePyut import ConvolutedPyutSDMessageInformation
from untanglepyut.UnTanglePyut import UnTanglePyut


def createOglSDInstances() -> OglSDInstances:
    return OglSDInstances({})


def createOglSDMessages() -> OglSDMessages:
    return OglSDMessages({})


class UntangleSequenceDiagram(BaseUnTangle):

    def __init__(self):

        super().__init__()

        self.logger: Logger = getLogger(__name__)

        self._oglSDInstances: OglSDInstances = createOglSDInstances()
        self._oglSDMessages:  OglSDMessages  = createOglSDMessages()

        self._untanglePyut: UnTanglePyut = UnTanglePyut()

    def unTangle(self, pyutDocument: Element):
        """

        Args:
            pyutDocument:  The pyut untangle element that represents a sequence diagram
        """
        self._oglSDInstances = self._untangleSDInstances(pyutDocument=pyutDocument)
        self._oglSDMessages  = self._untangleSDMessages(pyutDocument=pyutDocument)

    @property
    def oglSDInstances(self) -> OglSDInstances:
        return self._oglSDInstances

    @property
    def oglSDMessages(self) -> OglSDMessages:
        return self._oglSDMessages

    def _untangleSDInstances(self, pyutDocument: Element) -> OglSDInstances:

        oglSDInstances:     OglSDInstances = createOglSDInstances()
        graphicSDInstances: List[Element]   = pyutDocument.get_elements('GraphicSDInstance')

        for graphicSDInstance in graphicSDInstances:
            self.logger.debug(f'{graphicSDInstance=}')
            pyutSDInstance: PyutSDInstance     = self._untanglePyut.sdInstanceToPyutSDInstance(graphicSDInstance=graphicSDInstance)

            oglSDInstance:  OglSDInstance      = OglSDInstance(pyutSDInstance)
            graphicInfo:    GraphicInformation = toGraphicInfo(graphicElement=graphicSDInstance)

            oglSDInstance.SetSize(width=graphicInfo.width, height=graphicInfo.height)
            oglSDInstance.SetPosition(x=graphicInfo.x, y=graphicInfo.y)

            self._updateModel(oglObject=oglSDInstance, graphicInformation=graphicInfo)

            oglSDInstances[pyutSDInstance.id] = oglSDInstance
        return oglSDInstances

    def _untangleSDMessages(self, pyutDocument: Element) -> OglSDMessages:

        oglSDMessages:     OglSDMessages = createOglSDMessages()
        graphicSDMessages: List[Element] = pyutDocument.get_elements('GraphicSDMessage')

        for graphicSDMessage in graphicSDMessages:
            bogus: ConvolutedPyutSDMessageInformation = self._untanglePyut.sdMessageToPyutSDMessage(graphicSDMessage=graphicSDMessage)

            pyutSDMessage: PyutSDMessage = bogus.pyutSDMessage

            srcInstance: OglSDInstance = self._oglSDInstances[bogus.sourceId]
            dstInstance: OglSDInstance = self._oglSDInstances[bogus.destinationId]

            pyutSDMessage.setSource(srcInstance.pyutObject)          # Ugh, time was set by sdMessageToPyutSDMessage
            pyutSDMessage.setDestination(dstInstance.pyutObject)     # This "split" functionality must be fixed
            oglSDMessage: OglSDMessage = OglSDMessage(srcSDInstance=srcInstance, pyutSDMessage=pyutSDMessage, dstSDInstance=dstInstance)

            srcInstance.addLink(link=oglSDMessage)
            dstInstance.addLink(link=oglSDMessage)

            oglSDMessages[pyutSDMessage.id] = oglSDMessage

        return oglSDMessages
