
from logging import Logger
from logging import getLogger
from typing import Dict
from typing import List
from typing import NewType
from typing import Union
from typing import cast

from dataclasses import dataclass

from miniogl.AttachmentSide import AttachmentSide
from pyutmodel.PyutClass import PyutClass
from untangle import Element


from miniogl.ControlPoint import ControlPoint
from miniogl.SelectAnchorPoint import SelectAnchorPoint

from pyutmodel.PyutLinkType import PyutLinkType
from pyutmodel.PyutInterface import PyutInterface
from pyutmodel.PyutLink import PyutLink

from ogl.OglPosition import OglPosition
from ogl.OglAggregation import OglAggregation
from ogl.OglAssociation import OglAssociation
from ogl.OglComposition import OglComposition
from ogl.OglInheritance import OglInheritance
from ogl.OglInterface import OglInterface
from ogl.OglNoteLink import OglNoteLink
from ogl.OglNote import OglNote
from ogl.OglActor import OglActor
from ogl.OglUseCase import OglUseCase
from ogl.OglClass import OglClass
from ogl.OglLink import OglLink
from ogl.OglInterface2 import OglInterface2
from ogl.OglAssociationLabel import OglAssociationLabel

from untanglepyut.Common import UntangledControlPoints
from untanglepyut.Common import UntangledOglLinks
from untanglepyut.Common import createUntangledOglLinks
from untanglepyut.Common import str2bool

from untanglepyut.UnTanglePyut import UnTanglePyut


LinkableOglObject = Union[OglClass, OglNote, OglActor, OglUseCase]

LinkableOglObjects = NewType('LinkableOglObjects',   Dict[int, LinkableOglObject])


def createLinkableOglObjects() -> LinkableOglObjects:
    return LinkableOglObjects({})


@dataclass
class GraphicLinkAttributes:

    srcX:   int = -1
    srcY:   int = -1
    dstX:   int = -1
    dstY:   int = -1
    spline: bool = False


def fromGraphicLink(graphicLink: Element) -> GraphicLinkAttributes:

    gla: GraphicLinkAttributes = GraphicLinkAttributes()
    gla.srcX = int(graphicLink['srcX'])
    gla.srcY = int(graphicLink['srcY'])
    gla.dstX = int(graphicLink['dstX'])
    gla.dstY = int(graphicLink['dstY'])

    gla.spline = str2bool(graphicLink['spline'])

    return gla


class UnTangleOglLinks:
    """
    Currently, unsupported:

    ```html
      <LabelCenter x="579" y="300"/>
      <LabelSrc x="579" y="300"/>
      <LabelDst x="579" y="300"/>
    ```
    See:
    """

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._untanglePyut:     UnTanglePyut     = UnTanglePyut()

    def graphicLinksToOglLinks(self, pyutDocument: Element, linkableOglObjects: LinkableOglObjects) -> UntangledOglLinks:
        """
        Convert from XML to Ogl Links

        Args:
            pyutDocument:  The Element that represents the Class Diagram XML
            linkableOglObjects:    OGL objects that can have links

        Returns:  The links between any of the above objects.  Also returns the graphic lollipop links
        """

        oglLinks: UntangledOglLinks = createUntangledOglLinks()

        graphicLinks: Element = pyutDocument.get_elements('GraphicLink')
        for graphicLink in graphicLinks:
            oglLink: OglLink = self._graphicLinkToOglLink(graphicLink, linkableOglObjects=linkableOglObjects)
            oglLinks.append(oglLink)

        graphicLollipops: Element = pyutDocument.get_elements('GraphicLollipop')
        for graphicLollipop in graphicLollipops:
            oglInterface2: OglInterface2 = self._graphicLollipopToOglInterface(graphicLollipop, linkableOglObjects)
            oglLinks.append(oglInterface2)

        return oglLinks

    def _graphicLinkToOglLink(self, graphicLink: Element, linkableOglObjects: LinkableOglObjects) -> OglLink:
        """
        This code is way too convoluted.  Failing to do any of these step in this code leads to BAD
        visual representations.
        TODO:  Figure out how to simplify this code and/or make it more readable and obvious on how to create
        links (of whatever kind) between 2 OglClass'es

        Args:
            graphicLink:        The XML `GraphicClass` element
            linkableOglObjects:    OGL objects that can have links

        Returns:  A fully formed OglLink including control points
        """

        assert len(linkableOglObjects) != 0, 'Developer forgot to create dictionary'
        gla: GraphicLinkAttributes = fromGraphicLink(graphicLink=graphicLink)

        links: Element = graphicLink.get_elements('Link')
        assert len(links) == 1, 'Should only ever be one'

        singleLink:  Element = links[0]
        sourceId:    int = int(singleLink['sourceId'])
        dstId:       int = int(singleLink['destId'])
        self.logger.debug(f'graphicLink= {gla.srcX=} {gla.srcY=} {gla.dstX=} {gla.dstY=} {gla.spline=}')

        try:
            srcShape: LinkableOglObject = linkableOglObjects[sourceId]
            dstShape: LinkableOglObject = linkableOglObjects[dstId]
        except KeyError as ke:
            self.logger.error(f'Developer Error -- srcId: {sourceId} - dstId: {dstId}  KeyError index: {ke}')
            return cast(OglLink, None)

        pyutLink: PyutLink = self._untanglePyut.linkToPyutLink(singleLink, source=srcShape.pyutObject, destination=dstShape.pyutObject)
        oglLink:  OglLink  = self._oglLinkFactory(srcShape=srcShape, pyutLink=pyutLink, destShape=dstShape,
                                                  linkType=pyutLink.linkType,
                                                  srcPos=(gla.srcX, gla.srcY),
                                                  dstPos=(gla.dstX, gla.dstY)
                                                  )
        oglLink.SetSpline(gla.spline)
        srcShape.addLink(oglLink)
        dstShape.addLink(oglLink)

        # put the anchors at the right position
        srcAnchor = oglLink.sourceAnchor
        dstAnchor = oglLink.destinationAnchor
        srcAnchor.SetPosition(gla.srcX, gla.srcY)
        dstAnchor.SetPosition(gla.dstX, gla.dstY)

        srcModel = srcAnchor.GetModel()
        srcModel.SetPosition(x=gla.srcX, y=gla.srcY)
        dstModel = dstAnchor.GetModel()
        dstModel.SetPosition(x=gla.dstX, y=gla.dstY)

        # add the control points to the line
        line   = srcAnchor.GetLines()[0]     # only 1 line per anchor in Pyut
        parent = line.sourceAnchor.GetParent()
        selfLink: bool = parent is oglLink.destinationAnchor.GetParent()

        controlPoints: UntangledControlPoints = self._generateControlPoints(graphicLink=graphicLink)
        for controlPoint in controlPoints:
            oglLink.AddControl(control=controlPoint, after=None)
            if selfLink:
                x, y = controlPoint.GetPosition()
                controlPoint.SetParent(parent)
                controlPoint.SetPosition(x, y)

        if isinstance(oglLink, OglAssociation):
            oglLink = self.__furtherCustomizeAssociationLink(graphicLink, oglLink)

        self._reconstituteLinkDataModel(oglLink)

        return oglLink

    def _oglLinkFactory(self, srcShape, pyutLink, destShape, linkType: PyutLinkType, srcPos=None, dstPos=None):
        """
        Used to get a OglLink of the given linkType.

        Args:
            srcShape:   Source shape
            pyutLink:   Conceptual links associated with the graphical links.
            destShape:  Destination shape
            linkType:   The linkType of the link (OGL_INHERITANCE, ...)
            srcPos:     source position
            dstPos:     destination position

        Returns:  The requested link
        """
        if linkType == PyutLinkType.AGGREGATION:
            return OglAggregation(srcShape, pyutLink, destShape, srcPos=srcPos, dstPos=dstPos)

        elif linkType == PyutLinkType.COMPOSITION:
            return OglComposition(srcShape, pyutLink, destShape, srcPos=srcPos, dstPos=dstPos)

        elif linkType == PyutLinkType.INHERITANCE:
            return OglInheritance(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.ASSOCIATION:
            return OglAssociation(srcShape, pyutLink, destShape, srcPos=srcPos, dstPos=dstPos)

        elif linkType == PyutLinkType.INTERFACE:
            return OglInterface(srcShape, pyutLink, destShape, srcPos=srcPos, dstPos=dstPos)

        elif linkType == PyutLinkType.NOTELINK:
            return OglNoteLink(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.SD_MESSAGE:
            assert False, 'Sequence Diagram Messages not supported'
            # return OglSDMessage(srcShape=srcShape, pyutSDMessage=pyutLink, dstShape=destShape)
        else:
            self.logger.error(f"Unknown OglLinkType: {linkType}")
            return None

    def _graphicLollipopToOglInterface(self, graphicLollipop: Element, linkableOglObjects: LinkableOglObjects) -> OglInterface2:

        assert len(linkableOglObjects) != 0, 'Developer forgot to create dictionary'

        #
        # TODO: Do not use these x,y positions;  They are diagram relative
        #
        # x: int = int(graphicLollipop['x'])
        # y: int = int(graphicLollipop['y'])
        attachmentLocationStr: str            = graphicLollipop['attachmentPoint']
        attachmentSide:        AttachmentSide = AttachmentSide.toEnum(attachmentLocationStr)

        elements: Element = graphicLollipop.get_elements('Interface')
        assert len(elements) == 1, 'If more than one interface tag the XML is invalid'
        interfaceElement: Element        = elements[0]
        pyutInterface:    PyutInterface = self._untanglePyut.interfaceToPyutInterface(interface=interfaceElement)

        oglClass:    OglClass    = self._getOglClassFromName(pyutInterface.implementors[0], linkableOglObjects)
        oglPosition: OglPosition = self._determineAttachmentPoint(attachmentSide, oglClass)
        self.logger.debug(f'{oglPosition.x=},{oglPosition.y=}')

        anchorPoint:      SelectAnchorPoint = SelectAnchorPoint(x=oglPosition.x, y=oglPosition.y, attachmentSide=attachmentSide, parent=oglClass)
        oglInterface2:    OglInterface2     = OglInterface2(pyutInterface=pyutInterface, destinationAnchor=anchorPoint)

        return oglInterface2

    def _getOglClassFromName(self, className: str, linkableOglObjects: LinkableOglObjects) -> OglClass:
        """
        Looks up a name in the linkable objects dictionary and return the associated class
        TODO: Make a simple lookup and catch any Key errors

        Args:
            className:
            linkableOglObjects:

        Returns:
        """

        foundClass: OglClass = cast(OglClass, None)
        for oglClass in linkableOglObjects.values():
            if oglClass.pyutObject.name == className:
                foundClass = cast(OglClass, oglClass)
                break
        assert foundClass is not None, 'XML must be in error'
        return foundClass

    def _determineAttachmentPoint(self, attachmentPoint: AttachmentSide, oglClass: OglClass) -> OglPosition:
        """
        Even though we serialize the attachment point location that position is relative to the diagram.
        When we recreate the attachment point position we have to create it relative to its parent
        TODO: When the Pyut serializer makes the positions relative to the implementor we will not need this code

        Args:
            attachmentPoint:    Where on the parent
            oglClass:           The implementor

        Returns:  An OglPosition with coordinates relative to the implementor
        """

        oglPosition: OglPosition = OglPosition()

        dw, dh     = oglClass.GetSize()

        if attachmentPoint == AttachmentSide.NORTH:
            northX: int = dw // 2
            northY: int = 0
            oglPosition.x = northX
            oglPosition.y = northY
        elif attachmentPoint == AttachmentSide.SOUTH:
            southX = dw // 2
            southY = dh
            oglPosition.x = southX
            oglPosition.y = southY
        elif attachmentPoint == AttachmentSide.WEST:
            westX: int = 0
            westY: int = dh // 2
            oglPosition.x = westX
            oglPosition.y = westY
        elif attachmentPoint == AttachmentSide.EAST:
            eastX: int = dw
            eastY: int = dh // 2
            oglPosition.x = eastX
            oglPosition.y = eastY
        else:
            self.logger.warning(f'Unknown attachment point: {attachmentPoint}')
            assert False, 'Unknown attachment point'

        return oglPosition

    def _generateControlPoints(self, graphicLink: Element) -> UntangledControlPoints:

        controlPoints: UntangledControlPoints = UntangledControlPoints([])

        controlPointElements: Element = graphicLink.get_elements('ControlPoint')
        for controlPointElement in controlPointElements:
            x: int = int(controlPointElement['x'])
            y: int = int(controlPointElement['y'])
            controlPoint: ControlPoint = ControlPoint(x=x, y=y)
            controlPoints.append(controlPoint)

        return controlPoints

    def _reconstituteLinkDataModel(self, oglLink: OglLink):
        """
        Updates one the following lists in a PyutLinkedObject:

        ._parents   for Inheritance links
        ._links     for all other link types

        Args:
            oglLink:       An OglLink
        """
        srcShape:  OglClass = oglLink.sourceShape
        destShape: OglClass = oglLink.destinationShape
        self.logger.debug(f'source ID: {srcShape.id} - destination ID: {destShape.id}')

        pyutLink: PyutLink = oglLink.pyutObject

        if pyutLink.linkType == PyutLinkType.INHERITANCE:
            childPyutClass:  PyutClass = cast(PyutClass, srcShape.pyutObject)
            parentPyutClass: PyutClass = cast(PyutClass, destShape.pyutObject)
            childPyutClass.addParent(parentPyutClass)
        else:
            srcPyutClass:  PyutClass = cast(PyutClass, srcShape.pyutObject)
            srcPyutClass.addLink(pyutLink)

    def __furtherCustomizeAssociationLink(self, graphicLink: Element, oglLink: OglAssociation) -> OglAssociation:
        """
        Customize the visual aspects of an Association link

        TODO:  There is no support for this yet.  Need to add it to OglAssociation

        Args:
            graphicLink:  The top level GraphicLink Element
            oglLink:      The current OGL representation of the graphicLink

        Returns:  The updated association link
        """
        center: OglAssociationLabel = oglLink.centerLabel
        src:    OglAssociationLabel = oglLink.sourceCardinality
        dest:   OglAssociationLabel = oglLink.destinationCardinality

        oglLink.centerLabel            = self.__setAssociationLabelPosition(graphicLink, 'LabelCenter', center)
        oglLink.sourceCardinality      = self.__setAssociationLabelPosition(graphicLink, 'LabelSrc',    src)
        oglLink.destinationCardinality = self.__setAssociationLabelPosition(graphicLink, 'LabelDst',    dest)

        return oglLink

    def __setAssociationLabelPosition(self, graphicLink: Element, tagName: str, associationLabel: OglAssociationLabel) -> OglAssociationLabel:
        """

        Args:
            graphicLink:  The top level GraphicLink Element
            tagName:      The XML Element name
            associationLabel:  The Ogl association label to update

        Returns:  The updated association label
        """
        labels:  List[Element]   = graphicLink.get_elements(tagName)
        assert len(labels) == 1, 'There can be only one'
        label: Element = labels[0]
        x: int = int(label['x'])
        y: int = int(label['y'])

        self.logger.debug(f'tagName: {tagName} `{associationLabel.text=}`  pos: ({x},{y})')

        associationLabel.oglPosition.x = x
        associationLabel.oglPosition.y = y

        return associationLabel
