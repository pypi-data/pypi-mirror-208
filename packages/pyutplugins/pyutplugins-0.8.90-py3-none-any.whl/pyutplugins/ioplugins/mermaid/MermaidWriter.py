
from typing import List
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from enum import Enum

from os import linesep as eol

from datetime import datetime

from pathlib import Path

from pyutmodel.PyutField import PyutField
from pyutmodel.PyutField import PyutFields
from pyutmodel.PyutLink import PyutLink
from pyutmodel.PyutLinkedObject import PyutLinkedObject
from pyutmodel.PyutNote import PyutNote
from pyutmodel.PyutText import PyutText
from pyutmodel.PyutType import PyutType
from pyutmodel.PyutClass import PyutClass
from pyutmodel.PyutMethod import PyutMethod
from pyutmodel.PyutParameter import PyutParameter
from pyutmodel.PyutStereotype import PyutStereotype
from pyutmodel.PyutVisibilityEnum import PyutVisibilityEnum

from ogl.OglNote import OglNote
from ogl.OglText import OglText
from ogl.OglLink import OglLink
from ogl.OglNoteLink import OglNoteLink
from ogl.OglClass import OglClass
from ogl.OglInterface2 import OglInterface2
from ogl.OglAggregation import OglAggregation
from ogl.OglInheritance import OglInheritance
from ogl.OglComposition import OglComposition
from ogl.OglAssociation import OglAssociation
from ogl.OglInterface import OglInterface

from pyutplugins.ExternalTypes import OglObjects
from pyutplugins.ioplugins.mermaid.MermaidDirection import MermaidDirection
from pyutplugins.preferences.PluginPreferences import PluginPreferences


indent1: str = '    '
indent2: str = f'{indent1}    '
indent3: str = f'{indent2}    '
indent4: str = f'{indent3}    '
indent5: str = f'{indent4}    '


class MermaidArrow(Enum):
    INHERITANCE_ARROW = '<|--'  # Points to parent class
    AGGREGATION_LINK  = 'o--'   #
    COMPOSITION_LINK  = '*--'   #
    INTERFACE_LINK    = '..|>'  #
    ASSOCIATION_LINK  = '--'


class MermaidWriter:
    VERSION: str = '0.5'

    def __init__(self, fqFileName: Path, writeCredits: bool = True):
        """

        Args:
            fqFileName:     Fully qualified file name to write to
            writeCredits:   We will always write credits.  Unit tests turn this off
            because of the time stamps
        """
        self.logger: Logger = getLogger(__name__)

        self._fqFileName: Path = fqFileName

        self._preferences: PluginPreferences = PluginPreferences()

        self._writeCredits(writeCredits=writeCredits)

    def translate(self, oglObjects: OglObjects):

        mermaidString: str              = f'```mermaid{eol}'
        direction:     MermaidDirection = self._preferences.mermaidLayoutDirection
        mermaidString = f'{mermaidString}classDiagram{eol}{indent1}{direction.diagramValue}{eol}'

        linksStanza: str = self._generateLinksStanza(oglObjects=oglObjects)

        mermaidString = f'{mermaidString}{linksStanza}'

        for oglObject in oglObjects:
            match oglObject:
                case OglClass():
                    oglClass:  OglClass  = cast(OglClass, oglObject)
                    generatedString: str = self._generateClassStanza(oglClass)
                    mermaidString += f'{generatedString}'
                case OglNote():
                    pass
                case OglText():
                    oglText: OglText = cast(OglText, oglObject)
                    generatedString = self._mermaidStandaloneNoteStanza(oglText)
                    mermaidString += f'{generatedString}'
                case OglLink():
                    pass
                case _:
                    self.logger.warning(f'Unsupported Ogl element: {oglObject}')

        mermaidString += f'```{eol}'
        with self._fqFileName.open(mode='a') as fd:
            fd.write(f'{mermaidString}')

    def _mermaidStandaloneNoteStanza(self, oglText: OglText) -> str:

        pyutText: PyutText = oglText.pyutObject
        generatedString: str = (
            f'{indent1}note "{pyutText.content}"{eol}'
        )

        return generatedString

    def _generateClassStanza(self, oglObject: OglClass) -> str:
        """

        Args:
            oglObject:  A Pyut Class Definition

        Returns:  A Mermaid class definition
        """
        oglClass:  OglClass  = cast(OglClass, oglObject)
        pyutClass: PyutClass = oglClass.pyutObject

        fields:         PyutFields      = pyutClass.fields
        fieldsRefrain:  str              = self._generateFieldsRefrain(fields)
        methods:        List[PyutMethod] = pyutClass.methods
        methodsStr:     str              = self._generateMethods(methods)

        if pyutClass.stereotype == PyutStereotype.NO_STEREOTYPE:
            stereotypeRefrain: str = ''
        else:
            stereotypeRefrain = f'{indent2}<<{pyutClass.stereotype.value}>>{eol}'

        generatedString: str = (
            f'{indent1}class {pyutClass.name} {{ {eol}'
            f'{fieldsRefrain}'
            f'{stereotypeRefrain}'
            f'{methodsStr}'
            f'{indent1}}}{eol}'
        )
        return generatedString

    def _generateLinksStanza(self, oglObjects: OglObjects) -> str:
        """
        Make a pass through creating links
        Args:
            oglObjects:

        Returns:

        """
        linksStanza: str = f'{indent1}%% Links follow{eol}'

        for oglObject in oglObjects:
            linkRefrain: str = ''
            match oglObject:
                case OglInheritance():
                    linkRefrain = self._getInheritanceLinkRefrain(oglLink=oglObject)
                case OglAggregation():
                    oglAggregation: OglAggregation = cast(OglAggregation, oglObject)
                    linkRefrain = self._getAssociationLinkRefrain(oglAssociation=oglAggregation, arrowType=MermaidArrow.AGGREGATION_LINK)
                case OglComposition():
                    oglComposition: OglComposition = cast(OglComposition, oglObject)
                    linkRefrain = self._getAssociationLinkRefrain(oglAssociation=oglComposition, arrowType=MermaidArrow.COMPOSITION_LINK)
                case OglInterface():
                    oglInterface: OglInterface = cast(OglInterface, oglObject)
                    linkRefrain = self._getRealizationLinkRefrain(oglInterface)
                case OglNoteLink():
                    oglNoteLink: OglNoteLink = cast(OglNoteLink, oglObject)
                    linkRefrain = self._getNoteLinkRefrain(oglNoteLink)
                case OglAssociation():      # Most general needs to be last
                    oglAssociation: OglAssociation = cast(OglAssociation, oglObject)
                    linkRefrain = self._getAssociationLinkRefrain(oglAssociation=oglAssociation, arrowType=MermaidArrow.ASSOCIATION_LINK)
                case OglInterface2():
                    self.logger.warning(f'OglInterface2 (lollipops) not supported in Mermaid')
                case _:
                    pass        # Ignore non links
            linksStanza += linkRefrain

        return linksStanza

    def _getInheritanceLinkRefrain(self, oglLink: OglLink) -> str:
        """
        Produces strings of the form:

        Animal<|--Duck

        Where Animal is the parent class and Duck is the subclass

        Args:
            oglLink:  The inheritance link

        Returns:  Mermaid string for inheritance
        """
        pyutLink: PyutLink = oglLink.pyutObject

        subClassName:  str = pyutLink.getSource().name
        baseClassName: str = pyutLink.getDestination().name
        self.logger.info(f'{subClassName=} {pyutLink.linkType=} {baseClassName=}')

        linkRefrain: str  = (
            f'{indent1}{baseClassName}{MermaidArrow.INHERITANCE_ARROW.value}{subClassName}{eol}'
        )

        return linkRefrain

    def _getRealizationLinkRefrain(self, oglInterface: OglInterface) -> str:
        pyutLink: PyutLink = oglInterface.pyutObject
        interfaceName:   str = pyutLink.getSource().name
        implementorName: str = pyutLink.getDestination().name
        linkRefrain: str = (
            f'{indent1}{interfaceName} {MermaidArrow.INTERFACE_LINK.value} {implementorName}{eol}'
        )

        return linkRefrain

    def _getAssociationLinkRefrain(self, oglAssociation: OglAssociation, arrowType: MermaidArrow) -> str:
        """
        For Composition and Aggregation the diamond is on the source side
        Produces refrains of the form:

        For composition:
        Person "1" *-- "1" Heart

        Where Person is the 'composer' and Heart is the 'composed'

        For aggregation

        Author "1.*" o-- "0.*" Book

        Where Author aggregates Books

        Args:
            oglAssociation:
            arrowType:

        Returns:
        """
        pyutLink: PyutLink = oglAssociation.pyutObject
        sourceName:      str = pyutLink.getSource().name
        destinationName: str = pyutLink.getDestination().name
        self.logger.info(f'{oglAssociation} {sourceName=} {destinationName=}')

        sourceCardinality, destinationCardinality = self._getCardinalityStrings(pyutLink)
        linkRefrain: str = (
            f'{indent1}{sourceName} {sourceCardinality} {arrowType.value} {destinationCardinality} {destinationName} : {pyutLink.name}{eol}'
        )
        return linkRefrain

    def _getNoteLinkRefrain(self, oglNoteLink: OglNoteLink) -> str:
        """

        Args:
            oglNoteLink: The note link

        Returns:  Mermaid string for a note link
        """
        pyutLink:  PyutLink          = oglNoteLink.pyutObject
        destObject: PyutLinkedObject = pyutLink.getDestination()
        pyutNote:   PyutNote         = pyutLink.getSource()
        linkRefrain: str = (
            f'{indent1}note for {destObject.name} "{pyutNote.content}"{eol}'
        )
        return linkRefrain

    def _getCardinalityStrings(self, pyutLink) -> Tuple[str, str]:
        """

        Args:
            pyutLink:

        Returns: A tuple of source, destination cardinality strings

        """
        if pyutLink.sourceCardinality == '':
            sourceCardinality: str = ''
        else:
            sourceCardinality = f'"{pyutLink.sourceCardinality}"'

        if pyutLink.destinationCardinality == '':
            destinationCardinality: str = ''
        else:
            destinationCardinality = f'"{pyutLink.destinationCardinality}"'

        return sourceCardinality, destinationCardinality

    def _generateFieldsRefrain(self, fields: PyutFields) -> str:
        fieldsRefrain: str = ''
        for field in fields:
            pyutField: PyutField = cast(PyutField, field)
            visibility: PyutVisibilityEnum = pyutField.visibility
            retType:    PyutType = pyutField.type

            fieldString: str = (
                f'{indent2}{visibility.value}{retType.value} {pyutField.name}{eol}'
            )
            fieldsRefrain += fieldString
        return fieldsRefrain

    def _generateMethods(self, methods: List[PyutMethod]) -> str:

        retString: str = f''

        for method in methods:
            pyutMethod: PyutMethod = cast(PyutMethod, method)
            visibility: PyutVisibilityEnum = pyutMethod.visibility
            retType:    PyutType = pyutMethod.returnType

            parameterString: str = self._generateParameters(pyutMethod)
            methodString: str = (
                f'{indent2}{visibility.value}{retType.value} {pyutMethod.name}'
                f'('
                f'{parameterString}'
                f'){eol}'
            )
            retString += methodString
        return retString

    def _generateParameters(self, pyutMethod: PyutMethod) -> str:
        retString: str = ''

        for parameter in pyutMethod.parameters:
            pyutParameter: PyutParameter = cast(PyutParameter, parameter)
            parameterString: str = (
                f'{pyutParameter.name}, '
            )
            retString += parameterString
        return retString.strip(', ')

    def _writeCredits(self, writeCredits: bool):

        # ensure it is empty
        with self._fqFileName.open(mode='w') as fd:
            if writeCredits is True:

                fd.write(f'---{eol}')
                fd.write(f'Generated by Mermaid Writer Version: {MermaidWriter.VERSION}{eol}')

                now:      datetime = datetime.now()  # current date and time
                dateTime: str      = now.strftime('%d %b %Y, %H:%M:%S')

                fd.write(f'{dateTime}{eol}')
                fd.write(f'---{eol}')
            else:
                fd.write('')
