
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import Tuple
from typing import Union
from typing import cast

from logging import Logger
from logging import getLogger

from os import sep as osSep

from antlr4 import CommonTokenStream
from antlr4 import FileStream

from ogl.OglLink import OglLink
from ogl.OglClass import OglClass

from pyutmodel.PyutLinkType import PyutLinkType
from pyutmodel.PyutClass import PyutClass
from pyutmodel.PyutField import PyutField
from pyutmodel.PyutMethod import PyutMethod
from pyutmodel.PyutMethod import PyutParameters
from pyutmodel.PyutMethod import SourceCode
from pyutmodel.PyutParameter import PyutParameter
from pyutmodel.PyutType import PyutType
from pyutmodel.PyutVisibilityEnum import PyutVisibilityEnum

from pyutplugins.common.LinkMakerMixin import LinkMakerMixin
from pyutplugins.ExternalTypes import OglClasses
from pyutplugins.ExternalTypes import OglLinks


from pyutplugins.ioplugins.python.PythonParseException import PythonParseException
from pyutplugins.ioplugins.python.PyutPythonVisitor import ChildName
from pyutplugins.ioplugins.python.PyutPythonVisitor import Children
from pyutplugins.ioplugins.python.PyutPythonVisitor import ClassName
from pyutplugins.ioplugins.python.PyutPythonVisitor import ClassNames
from pyutplugins.ioplugins.python.PyutPythonVisitor import DataClassProperties
from pyutplugins.ioplugins.python.PyutPythonVisitor import MethodName
from pyutplugins.ioplugins.python.PyutPythonVisitor import MethodNames
from pyutplugins.ioplugins.python.PyutPythonVisitor import MultiParameterNames
from pyutplugins.ioplugins.python.PyutPythonVisitor import Parameters
from pyutplugins.ioplugins.python.PyutPythonVisitor import ParentName
from pyutplugins.ioplugins.python.PyutPythonVisitor import Parents
from pyutplugins.ioplugins.python.PyutPythonVisitor import PyutPythonVisitor
from pyutplugins.ioplugins.python.pyantlrparser.Python3Lexer import Python3Lexer
from pyutplugins.ioplugins.python.pyantlrparser.Python3Parser import Python3Parser

PyutClassName  = NewType('PyutClassName', str)
PyutClasses    = NewType('PyutClasses', Dict[PyutClassName, PyutClass])
OglClassesDict = NewType('OglClassesDict', Dict[Union[PyutClassName, ParentName, ChildName, ClassName], OglClass])


class ReverseEngineerPython2(LinkMakerMixin):
    """
    How to use this code

    After instance initialization call the .reversePython method with the necessary parameters.  That method populates a dictionary
    of class names to OglClasses;  After it returns the caller captures the parsed Ogl classes vi the .oglClasses property.  Through
    each call with a different package and module names the class is updating a dictionary of classes that are parents.
    The dictionary is keyed by the name of the class that is a parent class.  The value is a list of class names that
    are subclasses (aka children)

    TODO:

    This interaction is weird;  I think this class should keep track of all internal state
    """

    PYTHON_ASSIGNMENT:     str = '='
    PYTHON_TYPE_DELIMITER: str = ':'
    PYTHON_EOL_COMMENT:    str = '#'

    def __init__(self):

        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._pyutClasses:    PyutClasses     = PyutClasses({})
        self._oglClassesDict: OglClassesDict  = OglClassesDict({})
        self._oglClasses:     OglClasses      = cast(OglClasses, None)
        self._oglLinks:       OglLinks        = OglLinks([])
        self._onGoingParents: Parents = Parents({})

        self.visitor: PyutPythonVisitor = cast(PyutPythonVisitor, None)

    def reversePython(self,  directoryName: str, files: List[str], progressCallback: Callable):
        """
        Reverse engineering Python files to OglClass's

        Args:
            directoryName:  The directory name where the selected files reside
            files:          A list of files to parse
            progressCallback: The method to call to report progress
        """
        currentFileCount: int = 0

        self._pyutClasses    = PyutClasses({})
        self._oglClassesDict = OglClassesDict({})
        self._oglClasses     = cast(OglClasses, None)
        self._oglLinks       = OglLinks([])

        for fileName in files:

            try:
                fqFileName: str = f'{directoryName}{osSep}{fileName}'
                self.logger.info(f'Processing file: {fqFileName}')

                progressCallback(currentFileCount, f'Processing: {directoryName}\n {fileName}')

                fileStream: FileStream   = FileStream(fqFileName)
                lexer:      Python3Lexer = Python3Lexer(fileStream)

                stream: CommonTokenStream = CommonTokenStream(lexer)
                parser: Python3Parser     = Python3Parser(stream)

                tree: Python3Parser.File_inputContext = parser.file_input()
                if parser.getNumberOfSyntaxErrors() != 0:
                    eMsg: str = f"File {fileName} contains {parser.getNumberOfSyntaxErrors()} syntax errors"
                    self.logger.error(eMsg)
                    raise PythonParseException(eMsg)

                self.visitor = PyutPythonVisitor()
                self.visitor.parents = self._onGoingParents
                self.visitor.visit(tree)
                self._generatePyutClasses()

                self._onGoingParents = self.visitor.parents
                currentFileCount += 1
            except (ValueError, Exception) as e:
                self.logger.error(e)
                raise PythonParseException(e)
        self._generateOglClasses()
        # self._generateInheritanceLinks()

    @property
    def oglClasses(self) -> OglClassesDict:
        return self._oglClassesDict

    @property
    def oglLinks(self) -> OglLinks:
        return self._oglLinks

    def generateInheritanceLinks(self, oglClassesDict: OglClassesDict):

        parents: Parents = self._onGoingParents

        for parentName in parents.keys():
            children: Children = parents[parentName]
            for childName in children:

                try:
                    parentOglClass: OglClass = oglClassesDict[parentName]
                    childOglClass:  OglClass = oglClassesDict[childName]
                    oglLink: OglLink = self.createLink(src=childOglClass, dst=parentOglClass, linkType=PyutLinkType.INHERITANCE)
                    self._oglLinks.append(oglLink)
                except KeyError as ke:        # Probably there is no parent we are tracking
                    self.logger.warning(f'Apparently we are not tracking this parent:  {ke}')
                    continue

    def _generateOglClasses(self):

        for pyutClassName in self._pyutClasses:
            try:
                pyutClass: PyutClass = self._pyutClasses[pyutClassName]
                oglClass:  OglClass  = OglClass(pyutClass)

                self._oglClassesDict[pyutClassName] = oglClass
            except (ValueError, Exception) as e:
                self.logger.error(f"Error while creating class {pyutClassName},  {e}")

    def _generatePyutClasses(self):

        for className in self._classNames():
            pyutClass: PyutClass = PyutClass(name=className)

            pyutClass = self._addFields(pyutClass)

            for methodName in self._methodNames(className):
                pyutMethod: PyutMethod = PyutMethod(name=methodName)
                if methodName[0:2] == "__":
                    pyutMethod.setVisibility(PyutVisibilityEnum.PRIVATE)
                elif methodName[0] == "_":
                    pyutMethod.setVisibility(PyutVisibilityEnum.PROTECTED)
                else:
                    pyutMethod.setVisibility(PyutVisibilityEnum.PUBLIC)
                pyutMethod = self._addParameters(pyutMethod)
                pyutMethod.sourceCode = SourceCode(self.visitor.methodCode[methodName])

                pyutClass.addMethod(pyutMethod)

            setterProperties: Parameters = self.visitor.setterProperties
            getterProperties: Parameters = self.visitor.getterProperties

            pyutClass = self._generatePropertiesAsMethods(pyutClass, getterProperties, setterProperties)

            if className in self.visitor.dataClassNames:
                self._createDataClassPropertiesAsFields(pyutClass, self.visitor.dataClassProperties)

            self._pyutClasses[PyutClassName(className)] = pyutClass
        self.logger.info(f'Generated {len(self._pyutClasses)} classes')

    def _generatePropertiesAsMethods(self, pyutClass: PyutClass, getterProperties, setterProperties) -> PyutClass:

        for propName in self.visitor.propertyNames:
            # Might be a read-only property
            try:
                setterParams: List[str] = setterProperties[propName]
            except KeyError:
                setterParams = []

            getterParams: List[str] = getterProperties[propName]
            self.logger.info(f'Processing - {propName=} {setterParams=} {getterParams=}')
            setter, getter = self._createProperties(propName=propName, setterParams=setterParams)
            if setter is not None:
                setter.isProperty = True
                pyutClass.addMethod(setter)
            getter.isProperty = True
            pyutClass.addMethod(getter)

        return pyutClass

    def _createProperties(self, propName: str, setterParams: List[str]) -> Tuple[PyutMethod, PyutMethod]:

        getter: PyutMethod = PyutMethod(name=propName, visibility=PyutVisibilityEnum.PUBLIC)
        if len(setterParams) == 0:
            setter: PyutMethod = cast(PyutMethod, None)
        else:
            setter = PyutMethod(name=propName, visibility=PyutVisibilityEnum.PUBLIC)

        if setter is not None:
            nameType: str = setterParams[0]
            potentialNameType: List[str] = nameType.split(':')

            if len(potentialNameType) == 2:

                param: PyutParameter = PyutParameter(name=potentialNameType[0], parameterType=PyutType(value=potentialNameType[1]))
                setter.addParameter(param)
                getter.returnType = PyutType(value=potentialNameType[1])
            else:
                param = PyutParameter(name=potentialNameType[0])
                setter.addParameter(param)

        return setter, getter

    def _createDataClassPropertiesAsFields(self, pyutClass: PyutClass, dataClassProperties: DataClassProperties) -> PyutClass:
        """

        Args:
            pyutClass:  The PyutClass to update
            dataClassProperties:    The dataclass properties to parse

        Returns:
            Updated PyutClass with new fields
        """
        className: str = pyutClass.name
        for dPropertyTuple in dataClassProperties:
            if dPropertyTuple[0] == className:

                pyutField: PyutField = self._parseFieldToPyut(fieldData=dPropertyTuple[1])
                pyutClass.addField(pyutField)

        return pyutClass

    def _addParameters(self, pyutMethod: PyutMethod) -> PyutMethod:

        methodName: MethodName = MethodName(pyutMethod.name)
        if methodName in self.visitor.parameters:
            multiParameterNames: MultiParameterNames = self.visitor.parameters[methodName]

            pyutParameters: PyutParameters = self._generateParameters(multiParameterNames)
            pyutMethod.parameters = pyutParameters

        return pyutMethod

    def _addFields(self, pyutClass: PyutClass) -> PyutClass:
        """
        Can look like this:

           fieldData: x:int=0
           fieldData = 0

        Args:
            pyutClass:  Where to add the fields

        Returns:  The updated input class

        """
        for fieldData in self.visitor.fields:
            self.logger.debug(f'fieldData: {fieldData}')
            pyutField: PyutField = self._parseFieldToPyut(fieldData)
            pyutClass.addField(pyutField)

        return pyutClass

    def _methodNames(self, className: ClassName) -> MethodNames:

        methodNames: MethodNames = MethodNames([])
        try:
            methodNames = self.visitor.classMethods[className]
        except KeyError:
            self.logger.warning(f'{className} has no methods')

        return methodNames

    def _classNames(self) -> ClassNames:
        return self.visitor.classNames

    def _parseFieldToPyut(self, fieldData: str) -> PyutField:

        self.logger.debug(f'fieldData: {fieldData}')

        if ReverseEngineerPython2.PYTHON_TYPE_DELIMITER in fieldData and ReverseEngineerPython2.PYTHON_ASSIGNMENT in fieldData:
            pyutField: PyutField = self.__complexParseFieldToPyut(fieldData)
        else:
            pyutField = self.__simpleParseFieldToPyut(fieldData)

        return pyutField

    def _generateParameters(self, multiParameterNames: str) -> PyutParameters:
        """
        Handles the following 4 cases:
        Simple:                       param
        Typed:                        param: float
        SimpleDefaultValue:           param=0.0
        ComplexTypedAndDefaultValue: param: float = 0.0
        Args:
            multiParameterNames:

        Returns:  A list of PyutParam objects
        """
        parameterNameList: List[str] = multiParameterNames.split(',')
        pyutParams:        PyutParameters = PyutParameters([])
        for parameterStr in parameterNameList:
            if ':' in parameterStr and '=' in parameterStr:
                pyutParam: PyutParameter = self.__complexTypedAndDefaultValue(parameterStr)
            elif '=' in parameterStr:
                pyutParam = self._simpleDefaultValue(parameterStr)
            elif ':' in parameterStr:
                pyutParam = self._typedParameter(parameterStr)
            else:
                pyutParam = PyutParameter(parameterStr)
            pyutParams.append(pyutParam)

        return pyutParams

    def __complexTypedAndDefaultValue(self, complexParam: str) -> PyutParameter:

        paramNameType:  List[str] = complexParam.split(':')
        paramName:      str = paramNameType[0]
        paramTypeValue: List[str] = paramNameType[1].split('=')
        paramType:      str = paramTypeValue[0]
        paramValue:     str = paramTypeValue[1]

        pyutType: PyutType = PyutType(paramType)
        return PyutParameter(name=paramName, parameterType=pyutType, defaultValue=paramValue)

    def _simpleDefaultValue(self, simpleDefaultValueParam: str) -> PyutParameter:

        pyutParamAndValue: List[str] = simpleDefaultValueParam.split('=')
        paramName:  str = pyutParamAndValue[0]
        paramValue: str = pyutParamAndValue[1]

        pyutParam: PyutParameter = PyutParameter(name=paramName, defaultValue=paramValue)

        return pyutParam

    def _typedParameter(self, typedParam: str) -> PyutParameter:
        pyutParamAndType: List[str] = typedParam.split(':')
        paramName:        str = pyutParamAndType[0]
        paramType:        str = pyutParamAndType[1]

        pyutParam: PyutParameter = PyutParameter(name=paramName, parameterType=PyutType(value=paramType))
        return pyutParam

    def __simpleParseFieldToPyut(self, fieldData: str) -> PyutField:

        pyutField: PyutField = PyutField()

        noCommentFieldData: str = self.__stripEndOfLineComment(fieldData)
        fieldAndValue: List[str] = noCommentFieldData.split(ReverseEngineerPython2.PYTHON_ASSIGNMENT)

        if len(fieldAndValue) == 2:
            pyutField.name         = fieldAndValue[0].strip()
            pyutField.defaultValue = fieldAndValue[1].strip()
        else:   # might just be a declaration
            pyutField = self.__declarationOnlyParseToPyut(fieldData=fieldAndValue[0])
        return pyutField

    def __complexParseFieldToPyut(self, fieldData: str) -> PyutField:
        """
          Can look like this:

           fieldData: x:int=0

        Args:
            fieldData:

        Returns:
        """
        noCommentFieldData: str = self.__stripEndOfLineComment(fieldData)

        fieldAndType: List[str] = noCommentFieldData.split(ReverseEngineerPython2.PYTHON_TYPE_DELIMITER)
        fieldName:    str       = fieldAndType[0]

        vis: PyutVisibilityEnum = self.__determineFieldVisibility(fieldName)

        fieldName = self.__appropriatelyCleanupName(vis=vis, fieldName=fieldName)

        pyutField: PyutField = PyutField(name=fieldName, visibility=vis)

        if len(fieldAndType) > 1:
            typeAndDefaultValue: List[str] = fieldAndType[1].split(ReverseEngineerPython2.PYTHON_ASSIGNMENT)

            pyutType: PyutType = PyutType(value=typeAndDefaultValue[0].strip())
            pyutField.type = pyutType
            if len(typeAndDefaultValue) > 1:
                pyutField.defaultValue = typeAndDefaultValue[1].strip()

        return pyutField

    def __declarationOnlyParseToPyut(self, fieldData: str) -> PyutField:

        self.logger.info(f'{fieldData=}')
        fieldAndType: List[str] = fieldData.split(ReverseEngineerPython2.PYTHON_TYPE_DELIMITER)

        pyutField: PyutField = PyutField(name=fieldAndType[0])

        #
        # Might be something complex expression as a default value we can't handle it
        #
        if len(fieldAndType) > 1:
            pyutField.type       = PyutType(value=fieldAndType[1])
        pyutField.visibility = PyutVisibilityEnum.PUBLIC

        return pyutField

    def __determineFieldVisibility(self, name: str) -> PyutVisibilityEnum:

        vis: PyutVisibilityEnum = PyutVisibilityEnum.PUBLIC
        if len(name) > 1:
            if name[-2:] != "__":
                if name[0:2] == "__":
                    vis = PyutVisibilityEnum.PRIVATE
                elif name[0] == "_":
                    vis = PyutVisibilityEnum.PROTECTED
        return vis

    def __appropriatelyCleanupName(self, vis: PyutVisibilityEnum, fieldName: str) -> str:

        if vis == PyutVisibilityEnum.PUBLIC:
            return fieldName
        elif vis == PyutVisibilityEnum.PRIVATE:
            fieldName = fieldName[2:]
            return fieldName
        else:
            fieldName = fieldName[1:]
            return fieldName

    def __stripEndOfLineComment(self, fieldData: str) -> str:

        fieldAndComment: List[str] = fieldData.split(ReverseEngineerPython2.PYTHON_EOL_COMMENT)

        return fieldAndComment[0]
