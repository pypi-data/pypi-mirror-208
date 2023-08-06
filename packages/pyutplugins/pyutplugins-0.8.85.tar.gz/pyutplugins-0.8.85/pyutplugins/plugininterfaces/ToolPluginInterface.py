
from abc import ABC
from abc import abstractmethod

from pyutplugins.plugininterfaces.BasePluginInterface import BasePluginInterface

from pyutplugins.IPluginAdapter import IPluginAdapter


class ToolPluginInterface(BasePluginInterface, ABC):
    """
    This interface defines the methods and properties that Pyut Tool
    pyutplugins must implement.
    """

    def __init__(self, pluginAdapter: IPluginAdapter):

        super().__init__(pluginAdapter=pluginAdapter)

        self._menuTitle: str = 'Not Set'

    def executeTool(self):
        """
        This is used by Pyut to invoke the tool.  This should NOT
        be overridden
        TODO: Check for active frame
        """
        if self.setOptions() is True:
            self.doAction()

    @property
    def menuTitle(self) -> str:
        return self._menuTitle

    @abstractmethod
    def setOptions(self) -> bool:
        """
        Prepare for the tool action
        This can be used to query the user for additional plugin options

        Returns: If False, the import should be cancelled.  'True' to proceed
        """
        pass

    @abstractmethod
    def doAction(self):
        """
        Do the tool's action
        """
        pass
