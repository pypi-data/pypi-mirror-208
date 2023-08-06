from dataclasses import dataclass
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from untangle import Element

from pyutmodel.PyutField import PyutField
from pyutmodel.PyutField import PyutFields

from pyutmodel.PyutObject import PyutObject
from pyutmodel.PyutUseCase import PyutUseCase
from pyutmodel.PyutActor import PyutActor
from pyutmodel.PyutInterface import PyutInterface
from pyutmodel.PyutLink import PyutLink
from pyutmodel.PyutLinkType import PyutLinkType

from pyutmodel.PyutMethod import PyutMethods
from pyutmodel.PyutMethod import PyutParameters
from pyutmodel.PyutMethod import SourceCode
from pyutmodel.PyutParameter import PyutParameter
from pyutmodel.PyutMethod import PyutMethod
from pyutmodel.PyutMethod import PyutModifiers

from pyutmodel.PyutModifier import PyutModifier
from pyutmodel.PyutType import PyutType
from pyutmodel.PyutClass import PyutClass
from pyutmodel.PyutNote import PyutNote
from pyutmodel.PyutText import PyutText
from pyutmodel.PyutStereotype import PyutStereotype
from pyutmodel.PyutVisibilityEnum import PyutVisibilityEnum
from pyutmodel.PyutDisplayParameters import PyutDisplayParameters
from pyutmodel.PyutSDInstance import PyutSDInstance
from pyutmodel.PyutSDMessage import PyutSDMessage

from untanglepyut.Common import secureInteger
from untanglepyut.Common import str2bool

Elements = NewType('Elements',  List[Element])


@dataclass
class ConvolutedPyutSDMessageInformation:
    """
    This class is necessary because I do not want to mix Ogl and PyutModel code;  Unfortunately,
    the IDs of the PyutSDInstance are buried and require a lookup

    """
    pyutSDMessage: PyutSDMessage = cast(PyutSDMessage, None)
    sourceId:      int           = -1
    destinationId: int           = -1


class UnTanglePyut:
    """
    Converts PyutModel XML to Pyut Objects
    """
    # https://www.codetable.net/hex/a
    END_OF_LINE_MARKER: str ='&#xA;'

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def classToPyutClass(self, graphicClass: Element) -> PyutClass:
        classElement: Element = graphicClass.Class

        pyutClass: PyutClass = PyutClass()

        pyutClass = cast(PyutClass, self._addPyutObjectAttributes(pyutElement=classElement, pyutObject=pyutClass))

        displayParameters: PyutDisplayParameters = PyutDisplayParameters.toEnum(classElement['displayParameters'])

        showStereotype:    bool = bool(classElement['showStereotype'])
        showFields:        bool = bool(classElement['showFields'])
        showMethods:       bool = bool(classElement['showMethods'])
        stereotypeStr:     str  = classElement['stereotype']

        pyutClass.displayParameters = displayParameters

        pyutClass.displayStereoType = showStereotype
        pyutClass.showFields     = showFields
        pyutClass.showMethods    = showMethods

        pyutClass.description = classElement['description']
        pyutClass.stereotype = PyutStereotype.toEnum(stereotypeStr)

        pyutClass.methods = self._methodToPyutMethods(classElement=classElement)
        pyutClass.fields  = self._fieldToPyutFields(classElement=classElement)

        return pyutClass

    def textToPyutText(self, graphicText: Element) -> PyutText:
        """
        Parses Text elements
        Args:
            graphicText:   Of the form:   <Text id="3" content="I am standalone text"/>

        Returns: A PyutText Object
        """
        textElement: Element  = graphicText.Text
        pyutText:    PyutText = PyutText()

        pyutText.id  = textElement['id']

        rawContent:   str = textElement['content']
        cleanContent: str = rawContent.replace(UnTanglePyut.END_OF_LINE_MARKER, osLineSep)
        pyutText.content = cleanContent

        return pyutText

    def noteToPyutNote(self, graphicNote: Element) -> PyutNote:
        """
        Parse Note elements
        Args:
            graphicNote: of the form:  <Note id="2" content="I am a UML Note" filename=""/>

        Returns: A PyutNote Object
        """
        noteElement: Element = graphicNote.Note
        pyutNote: PyutNote = PyutNote()

        # fix line feeds
        pyutNote = cast(PyutNote, self._addPyutObjectAttributes(pyutElement=noteElement, pyutObject=pyutNote))

        rawContent:   str = noteElement['content']
        cleanContent: str = rawContent.replace(UnTanglePyut.END_OF_LINE_MARKER, osLineSep)
        pyutNote.content = cleanContent
        return pyutNote

    def interfaceToPyutInterface(self, interface: Element) -> PyutInterface:

        interfaceId: int = int(interface['id'])
        name:        str = interface['name']
        description: str = interface['description']

        pyutInterface: PyutInterface = PyutInterface(name=name)
        pyutInterface.id          = interfaceId
        pyutInterface.description = description

        implementors: Element = interface.get_elements('Implementor')
        for implementor in implementors:
            pyutInterface.addImplementor(implementor['implementingClassName'])

        pyutInterface.methods = self._interfaceMethodsToPyutMethods(interface=interface)
        return pyutInterface

    def actorToPyutActor(self, graphicActor: Element) -> PyutActor:
        """
        <GraphicActor width="87" height="114" x="293" y="236">
            <Actor id="1" name="BasicActor" filename=""/>
        </GraphicActor>

        Args:
            graphicActor:   untangle Element in the above format

        Returns:   PyutActor
        """
        actorElement: Element   = graphicActor.Actor
        pyutActor:    PyutActor = PyutActor()

        pyutActor = cast(PyutActor, self._addPyutObjectAttributes(pyutElement=actorElement, pyutObject=pyutActor))

        return pyutActor

    def useCaseToPyutUseCase(self, graphicUseCase: Element) -> PyutUseCase:
        """
        <GraphicUseCase width="100" height="60" x="575" y="250">
            <UseCase id="2" name="Basic Use Case" filename=""/>
        </GraphicUseCase>

        Args:
            graphicUseCase:  An untangle Element in the above format

        Returns:  PyutUseCase
        """
        useCaseElement: Element     = graphicUseCase.UseCase
        pyutUseCase:    PyutUseCase = PyutUseCase()

        pyutUseCase = cast(PyutUseCase, self._addPyutObjectAttributes(pyutElement=useCaseElement, pyutObject=pyutUseCase))

        return pyutUseCase

    def linkToPyutLink(self, singleLink: Element, source: PyutClass, destination: PyutClass) -> PyutLink:
        linkTypeStr:     str          = singleLink['type']
        linkType:        PyutLinkType = PyutLinkType.toEnum(linkTypeStr)
        cardSrc:         str          = singleLink['cardSrc']
        cardDest:        str          = singleLink['cardDestination']
        bidir:           bool         = str2bool(singleLink['bidir'])
        linkDescription: str          = singleLink['name']

        pyutLink: PyutLink = PyutLink(name=linkDescription,
                                      linkType=linkType,
                                      cardSrc=cardSrc, cardDest=cardDest,
                                      bidir=bidir,
                                      source=source,
                                      destination=destination)

        return pyutLink

    def sdInstanceToPyutSDInstance(self, graphicSDInstance: Element) -> PyutSDInstance:

        instanceElement: Element        = graphicSDInstance.SDInstance
        pyutSDInstance:  PyutSDInstance = PyutSDInstance()

        pyutSDInstance.id                     = int(instanceElement['id'])
        pyutSDInstance.instanceName           = instanceElement['instanceName']
        pyutSDInstance.instanceLifeLineLength = secureInteger(instanceElement['lifeLineLength'])

        return pyutSDInstance

    def sdMessageToPyutSDMessage(self, graphicSDMessage: Element) -> ConvolutedPyutSDMessageInformation:
        """
        TODO:  Need to fix how SD Messages are created
        Args:
            graphicSDMessage:

        Returns:  Bogus data class
        """

        messageElement: Element       = graphicSDMessage.SDMessage
        pyutSDMessage:  PyutSDMessage = PyutSDMessage()

        pyutSDMessage.id = int(messageElement['id'])
        pyutSDMessage.message = messageElement['message']
        pyutSDMessage.linkType = PyutLinkType.SD_MESSAGE

        srcID: int = int(messageElement['srcID'])
        dstID: int = int(messageElement['dstID'])

        srcTime: int = int(messageElement['srcTime'])
        dstTime: int = int(messageElement['dstTime'])

        pyutSDMessage.sourceY      = srcTime
        pyutSDMessage.destinationY = dstTime

        bogus: ConvolutedPyutSDMessageInformation = ConvolutedPyutSDMessageInformation()

        bogus.pyutSDMessage = pyutSDMessage
        bogus.sourceId      = srcID
        bogus.destinationId = dstID

        return bogus

    def _methodToPyutMethods(self, classElement: Element) -> PyutMethods:
        """
        The pyutClass may not have methods;
        Args:
            classElement:  The pyutClassElement

        Returns:  May return an empty list
        """
        untangledPyutMethods: PyutMethods = PyutMethods([])

        methodElements = classElement.get_elements('Method')
        for methodElement in methodElements:
            methodName: str                = methodElement['name']
            visibility: PyutVisibilityEnum = PyutVisibilityEnum.toEnum(methodElement['visibility'])
            self.logger.debug(f"{methodName=} - {visibility=}")

            pyutMethod: PyutMethod = PyutMethod(name=methodName, visibility=visibility)

            pyutMethod.modifiers = self._modifierToPyutMethodModifiers(methodElement=methodElement)

            returnElement = methodElement.get_elements('Return')

            if len(returnElement) > 0:
                pyutType: PyutType = PyutType(value=returnElement[0]['type'])
                pyutMethod.returnType = pyutType

            parameters = self._paramToPyutParameters(methodElement)
            pyutMethod.parameters = parameters
            pyutMethod.sourceCode = self._sourceCodeToPyutSourceCode(methodElement=methodElement)

            untangledPyutMethods.append(pyutMethod)

        return untangledPyutMethods

    def _fieldToPyutFields(self, classElement: Element) -> PyutFields:
        untangledPyutFields: PyutFields = PyutFields([])

        fieldElements: Elements = classElement.get_elements('Field')
        for fieldElement in fieldElements:
            visibility:    PyutVisibilityEnum = PyutVisibilityEnum.toEnum(fieldElement['visibility'])
            paramElements: Elements           = fieldElement.get_elements('Param')
            assert len(paramElements) == 1, 'Curiously there should be only one'

            paramElement: Element = paramElements[0]
            fieldName:    str       = paramElement['name']
            pyutType:     PyutType  = PyutType(paramElement['type'])
            defaultValue: str       = paramElement['defaultValue']
            if defaultValue is None:
                defaultValue = ''
            pyutField: PyutField = PyutField(name=fieldName, visibility=visibility, fieldType=pyutType, defaultValue=defaultValue)

            untangledPyutFields.append(pyutField)

        return untangledPyutFields

    def _modifierToPyutMethodModifiers(self, methodElement: Element) -> PyutModifiers:
        """
        Should be in this form:

            <Modifier name="Modifier1"/>
            <Modifier name="Modifier2"/>
            <Modifier name="Modifier3"/>
            <Modifier name="Modifier4"/>

        Args:
            methodElement:

        Returns:  PyutModifiers if not exist returns an empty
        """

        modifierElements = methodElement.get_elements('Modifier')

        pyutModifiers: PyutModifiers = PyutModifiers([])
        if len(modifierElements) > 0:
            for modifierElement in modifierElements:
                modifierName:           str       = modifierElement['name']
                pyutModifier: PyutModifier = PyutModifier(modifierTypeName=modifierName)
                pyutModifiers.append(pyutModifier)

        return pyutModifiers

    def _paramToPyutParameters(self, methodElement: Element) -> PyutParameters:

        parameterElements = methodElement.get_elements('Param')     # TODO:  https://github.com/hasii2011/PyUt/issues/326
        untangledPyutMethodParameters: PyutParameters = PyutParameters([])
        for parameterElement in parameterElements:
            name:           str = parameterElement['name']
            defaultValue:   str = parameterElement['defaultValue']
            parameterType:  PyutType = PyutType(parameterElement['type'])

            pyutParameter: PyutParameter = PyutParameter(name=name, parameterType=parameterType, defaultValue=defaultValue)
            # <Param name="intParameter" type="int" defaultValue="0"/>
            # <Param name="floatParameter" type="float" defaultValue="0.0"/>
            # <Param name="stringParameter" type="str" defaultValue="''"/>
            untangledPyutMethodParameters.append(pyutParameter)

        return untangledPyutMethodParameters

    def _sourceCodeToPyutSourceCode(self, methodElement: Element) -> SourceCode:

        sourceCodeElements = methodElement.get_elements('SourceCode')
        codeElements = sourceCodeElements[0].get_elements('Code')
        sourceCode: SourceCode = SourceCode([])
        for codeElement in codeElements:
            self.logger.debug(f'{codeElement.cdata=}')
            codeLine: str = codeElement.cdata
            sourceCode.append(codeLine)
        return sourceCode

    def _interfaceMethodsToPyutMethods(self, interface: Element) -> PyutMethods:

        pyutMethods: PyutMethods = self._methodToPyutMethods(interface)

        return pyutMethods

    def _addPyutObjectAttributes(self, pyutElement: Element, pyutObject: PyutObject) -> PyutObject:
        """

        Args:
            pyutElement:    pyutElement XML with common keys
            pyutObject:     The PyutObject to update

        Returns:  The updated pyutObject as
        """

        pyutObject.id       = int(pyutElement['id'])    # TODO revisit this when we start using UUIDs
        pyutObject.name     = pyutElement['name']
        pyutObject.fileName = pyutElement['fileName']

        return pyutObject
