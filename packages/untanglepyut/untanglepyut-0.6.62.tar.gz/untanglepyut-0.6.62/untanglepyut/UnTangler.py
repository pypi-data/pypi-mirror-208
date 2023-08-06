
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass
from dataclasses import field

from untangle import parse
from untangle import Element

from ogl.OglClass import OglClass
from ogl.OglNote import OglNote
from ogl.OglText import OglText

from pyutmodel.PyutClass import PyutClass
from pyutmodel.PyutNote import PyutNote
from pyutmodel.PyutText import PyutText

from untanglepyut.BaseUnTangle import BaseUnTangle

from untanglepyut.Common import Elements
from untanglepyut.Common import toGraphicInfo
from untanglepyut.Common import GraphicInformation
from untanglepyut.Common import UntangledOglLinks
from untanglepyut.Common import createUntangledOglActors
from untanglepyut.Common import createUntangledOglLinks
from untanglepyut.Common import createUntangledOglUseCases

from untanglepyut.Types import UntangledOglActors
from untanglepyut.Types import UntangledOglClasses
from untanglepyut.Types import UntangledOglNotes
from untanglepyut.Types import UntangledOglTexts
from untanglepyut.Types import UntangledOglUseCases

from untanglepyut.UnTangleOglLinks import LinkableOglObjects
from untanglepyut.UnTangleOglLinks import createLinkableOglObjects
from untanglepyut.UnTanglePyut import UnTanglePyut
from untanglepyut.UnTangleOglLinks import UnTangleOglLinks
from untanglepyut.UnTangleUseCaseDiagram import UnTangleUseCaseDiagram
from untanglepyut.UntangleSequenceDiagram import OglSDMessages
from untanglepyut.UntangleSequenceDiagram import OglSDInstances
from untanglepyut.UntangleSequenceDiagram import UntangleSequenceDiagram
from untanglepyut.UntangleSequenceDiagram import createOglSDMessages
from untanglepyut.UntangleSequenceDiagram import createOglSDInstances


@dataclass
class ProjectInformation:
    fileName: str = cast(str, None)
    version:  str = cast(str, None)
    codePath: str = cast(str, None)


"""
Factory methods for our dataclasses
"""


def createUntangledOglClasses() -> UntangledOglClasses:
    """
    Factory method to create  the UntangledClasses data structure;

    Returns:  A new data structure
    """
    return UntangledOglClasses([])


def createUntangledOglNotes() -> UntangledOglNotes:
    return UntangledOglNotes([])


def createUntangledOglTexts() -> UntangledOglTexts:
    return UntangledOglTexts([])


@dataclass
class Document:
    """
    Create a UseCaseDocument and a ClassDiagramDocument
    """
    documentType:    str = ''
    documentTitle:   str = ''
    scrollPositionX: int = -1
    scrollPositionY: int = -1
    pixelsPerUnitX:  int = -1
    pixelsPerUnitY:  int = -1
    oglClasses:      UntangledOglClasses  = field(default_factory=createUntangledOglClasses)
    oglLinks:        UntangledOglLinks    = field(default_factory=createUntangledOglLinks)
    oglNotes:        UntangledOglNotes    = field(default_factory=createUntangledOglNotes)
    oglTexts:        UntangledOglTexts    = field(default_factory=createUntangledOglTexts)
    oglActors:       UntangledOglActors   = field(default_factory=createUntangledOglActors)
    oglUseCases:     UntangledOglUseCases = field(default_factory=createUntangledOglUseCases)
    oglSDInstances:  OglSDInstances = field(default_factory=createOglSDInstances)
    oglSDMessages:   OglSDMessages  = field(default_factory=createOglSDMessages)


# @dataclass
# class SDDocument(Document):
#     oglSDInstances:  OglSDInstances = field(default_factory=createOglSDInstances)
#     oglSDMessages:   OGLSDMessages  = field(default_factory=createOGLSDMessages)


DocumentTitle = NewType('DocumentTitle', str)
Documents     = NewType('Documents', dict[DocumentTitle, Document])


class UnTangler(BaseUnTangle):

    def __init__(self):
        """
        """
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._projectInformation: ProjectInformation = ProjectInformation()
        self._documents:          Documents          = Documents({})

        self._untanglePyut:     UnTanglePyut     = UnTanglePyut()
        self._untangleOglLinks: UnTangleOglLinks = UnTangleOglLinks()

    @property
    def projectInformation(self) -> ProjectInformation:
        """
        This property return nothing valid until you untangle the file

        Returns:  The project information of the untangled pyut file
        """
        return self._projectInformation

    @property
    def documents(self) -> Documents:
        return self._documents

    def untangleFile(self, fqFileName: str):
        """
        Read input file and untangle to Ogl
        Args:
            fqFileName:  The file name with the XML

        """
        xmlString:   str     = self.getRawXml(fqFileName=fqFileName)
        self.untangleXml(xmlString=xmlString)

        self._projectInformation.fileName = fqFileName

    def untangleXml(self, xmlString: str):
        """
        Untangle the input Xml string to Ogl
        Args:
            xmlString: The string wit the raw XML
        """
        root:        Element = parse(xmlString)
        pyutProject: Element = root.PyutProject

        self._populateProjectInformation(pyutProject=pyutProject)

        for pyutDocument in pyutProject.PyutDocument:
            document: Document = self._updateCurrentDocumentInformation(pyutDocument=pyutDocument)

            self._documents[DocumentTitle(document.documentTitle)] = document

            self.logger.debug(f'{document=}')
            if document.documentType == 'CLASS_DIAGRAM':
                document.oglClasses = self._graphicClassesToOglClasses(pyutDocument=pyutDocument)
                document.oglNotes   = self._graphicNotesToOglNotes(pyutDocument=pyutDocument)
                document.oglTexts   = self._graphicalTextToOglTexts(pyutDocument=pyutDocument)

                linkableOglObjects: LinkableOglObjects = self._buildDictionary(document=document)
                document.oglLinks   = self._untangleOglLinks.graphicLinksToOglLinks(pyutDocument, linkableOglObjects=linkableOglObjects)
            elif document.documentType == 'SEQUENCE_DIAGRAM':
                untangleSequenceDiagram: UntangleSequenceDiagram = UntangleSequenceDiagram()

                untangleSequenceDiagram.unTangle(pyutDocument=pyutDocument)
                document.oglSDInstances = untangleSequenceDiagram.oglSDInstances
                document.oglSDMessages  = untangleSequenceDiagram.oglSDMessages

            elif document.documentType == 'USECASE_DIAGRAM':

                unTangleUseCaseDiagram: UnTangleUseCaseDiagram = UnTangleUseCaseDiagram()

                unTangleUseCaseDiagram.unTangle(pyutDocument=pyutDocument)
                document.oglActors   = unTangleUseCaseDiagram.oglActors
                document.oglUseCases = unTangleUseCaseDiagram.oglUseCases
                document.oglNotes    = self._graphicNotesToOglNotes(pyutDocument=pyutDocument)
                document.oglTexts    = self._graphicalTextToOglTexts(pyutDocument=pyutDocument)

                linkableOglObjects = self._buildDictionary(document=document)
                document.oglLinks  = self._untangleOglLinks.graphicLinksToOglLinks(pyutDocument, linkableOglObjects=linkableOglObjects)
            else:
                assert False, f'Unknown document type: {document.documentType}'

    def getRawXml(self, fqFileName: str) -> str:
        """
        Convenience method to read a file.  Assumes the file has XML.
        No check is done to verify this
        Args:
            fqFileName: The file to read

        Returns:  The contents of the file
        """
        try:
            with open(fqFileName, "r") as xmlFile:
                xmlString: str = xmlFile.read()
        except (ValueError, Exception) as e:
            self.logger.error(f'xml open:  {e}')
            raise e

        return xmlString

    def _populateProjectInformation(self, pyutProject: Element):
        self._projectInformation.version  = pyutProject['version']
        self._projectInformation.codePath = pyutProject['CodePath']

    def _updateCurrentDocumentInformation(self, pyutDocument: Element) -> Document:

        documentInformation: Document = Document()

        documentTitle: DocumentTitle = DocumentTitle(pyutDocument['title'])

        documentInformation.documentType = pyutDocument['type']
        documentInformation.documentTitle = documentTitle

        documentInformation.scrollPositionX = int(pyutDocument['scrollPositionX'])
        documentInformation.scrollPositionY = int(pyutDocument['scrollPositionY'])
        documentInformation.pixelsPerUnitX  = int(pyutDocument['pixelsPerUnitX'])
        documentInformation.pixelsPerUnitY  = int(pyutDocument['pixelsPerUnitY'])

        self.logger.debug(f'{documentInformation=}')

        return documentInformation

    def _graphicClassesToOglClasses(self, pyutDocument: Element) -> UntangledOglClasses:

        oglClasses:     UntangledOglClasses = createUntangledOglClasses()
        graphicClasses: Elements            = pyutDocument.get_elements('GraphicClass')
        
        for graphicClass in graphicClasses:
            self.logger.debug(f'{graphicClass=}')

            graphicInformation: GraphicInformation = toGraphicInfo(graphicElement=graphicClass)
            oglClass: OglClass = OglClass(pyutClass=None, w=graphicInformation.width, h=graphicInformation.height)
            oglClass.SetPosition(x=graphicInformation.x, y=graphicInformation.y)
            #
            # This is necessary if it is never added to a diagram
            # and immediately serialized
            #
            self._updateModel(oglObject=oglClass, graphicInformation=graphicInformation)

            pyutClass: PyutClass = self._untanglePyut.classToPyutClass(graphicClass=graphicClass)
            oglClass.pyutObject = pyutClass
            oglClasses.append(oglClass)

        return oglClasses

    def _graphicNotesToOglNotes(self, pyutDocument: Element) -> UntangledOglNotes:
        """

        Args:
            pyutDocument:

        Returns: untangled OglNote objects if any exist, else an empty list
        """
        oglNotes:     UntangledOglNotes = createUntangledOglNotes()
        graphicNotes: Elements          = pyutDocument.get_elements('GraphicNote')

        for graphicNote in graphicNotes:
            self.logger.debug(f'{graphicNote}')

            graphicInformation: GraphicInformation = toGraphicInfo(graphicElement=graphicNote)
            oglNote:            OglNote            = OglNote(w=graphicInformation.width, h=graphicInformation.height)
            oglNote.SetPosition(x=graphicInformation.x, y=graphicInformation.y)
            self._updateModel(oglObject=oglNote, graphicInformation=graphicInformation)
            pyutNote: PyutNote = self._untanglePyut.noteToPyutNote(graphicNote=graphicNote)
            oglNote.pyutObject = pyutNote
            oglNotes.append(oglNote)

        return oglNotes

    def _graphicalTextToOglTexts(self, pyutDocument: Element) -> UntangledOglTexts:
        """
        Yeah, yeah, I know bad English;

        Args:
            pyutDocument:  The Element document

        Returns:  untangled OglText objects if any exist, else an empty list
        """
        oglTexts:     UntangledOglTexts = createUntangledOglTexts()
        graphicTexts: Elements          = pyutDocument.get_elements('GraphicText')

        for graphicText in graphicTexts:
            self.logger.debug(f'{graphicText}')

            graphicInformation: GraphicInformation = toGraphicInfo(graphicElement=graphicText)
            pyutText:           PyutText           = self._untanglePyut.textToPyutText(graphicText=graphicText)
            oglText:            OglText            = OglText(pyutText=pyutText, width=graphicInformation.width, height=graphicInformation.height)
            oglText.SetPosition(x=graphicInformation.x, y=graphicInformation.y)
            #
            # This is necessary if it is never added to a diagram
            # and immediately serialized
            #
            self._updateModel(oglObject=oglText, graphicInformation=graphicInformation)
            oglText.pyutText = pyutText
            oglTexts.append(oglText)

        return oglTexts

    def _buildDictionary(self, document: Document) -> LinkableOglObjects:
        """

        Args:
            document:   The created document either Use case or class diagram

        Returns:  Linkable Objects Dictionary
        """

        linkableOglObjects: LinkableOglObjects = createLinkableOglObjects()

        for oglClass in document.oglClasses:
            linkableOglObjects[oglClass.pyutObject.id] = oglClass

        for oglNote in document.oglNotes:
            linkableOglObjects[oglNote.pyutObject.id] = oglNote

        for oglUseCase in document.oglUseCases:
            linkableOglObjects[oglUseCase.pyutObject.id] = oglUseCase

        for oglActor in document.oglActors:
            linkableOglObjects[oglActor.pyutObject.id] = oglActor

        return linkableOglObjects
