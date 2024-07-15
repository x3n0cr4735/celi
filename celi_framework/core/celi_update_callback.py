from abc import ABC, abstractmethod
from typing import Dict, Tuple


class CELIUpdateCallback(ABC):
    """ProcessRunner takes an instance of this callback function, which can be used to receive updates on CELI
    processing."""

    @abstractmethod
    def on_message(self, section: str, msg: Dict[str, str] | Tuple[str, str]):
        """
        A description of the entire function, its parameters, and its return types.
        """
        pass

    @abstractmethod
    def on_section_complete(self, section: str):
        """
        This method is called when a section is completed.

        Args:
            section (str): The name of the completed section.
        """
        pass

    @abstractmethod
    def on_all_sections_complete(self):
        """
        This method is called when all sections is completed.

        Args:
            section (str): The name of the completed section.
        """
        pass

    @abstractmethod
    def on_output(self, section: str, output: str):
        """Not used directly by CELI, but if a tool implementation takes a callback argument,
        CELI will pass the callback in, and the tool can call on_output (or other methods).
        """
