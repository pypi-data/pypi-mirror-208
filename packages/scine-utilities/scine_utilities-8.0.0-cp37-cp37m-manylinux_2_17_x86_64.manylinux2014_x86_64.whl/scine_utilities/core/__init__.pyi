"""
    The ``core`` submodule defines interfaces that permeate the SCINE Project.
    Individual components may offer models of these interfaces that are then
    available through the :class:`core.ModuleManager` class.
  """
import scine_utilities.core
import typing
from typing import Union
import scine_utilities

__all__ = [
    "Calculator",
    "CalculatorWithReference",
    "Log",
    "Module",
    "ModuleManager",
    "ObjectWithStructure",
    "Sink",
    "State",
    "StateHandableObject",
    "WavefunctionOutputGenerator",
    "get_available_settings",
    "get_calculator",
    "get_possible_properties",
    "has_calculator",
    "load_system",
    "load_system_into_calculator",
    "to_wf_generator"
]


class ObjectWithStructure():
    pass
class CalculatorWithReference():
    """
    The CalculatorWithReference is the abstract base for classes running calculations based on a reference one, f.i. Excited-state calculations.
    """
    def apply_settings(self) -> None: 
        """
        Applies the settings given.
        """
    def calculate(self) -> scine_utilities.Results: 
        """
        Execute the calculation. Needs a reference_calculation call beforehand.
        """
    def get_results(self) -> scine_utilities.Results: 
        """
        Get any strored results.
        """
    def has_results(self) -> bool: 
        """
        Check if results are present.
        """
    def list_settings(self) -> typing.List[str]: 
        """
        Returns the list of settings available in this instance.
        """
    def name(self) -> str: 
        """
        Yields the name of the calculator
        """
    def reference_calculation(self) -> None: 
        """
        Execute the reference calculation
        """
    @property
    def log(self) -> Log:
        """
        Logger of the calculator with reference.

        :type: Log
        """
    @log.setter
    def log(self, arg1: Log) -> None:
        """
        Logger of the calculator with reference.
        """
    @property
    def reference_calculator(self) -> Calculator:
        """
        The reference calculator.

        :type: Calculator
        """
    @reference_calculator.setter
    def reference_calculator(self, arg1: Calculator) -> None:
        """
        The reference calculator.
        """
    @property
    def settings(self) -> scine_utilities.Settings:
        """
        Settings of the calculator

        :type: scine_utilities.Settings
        """
    @settings.setter
    def settings(self, arg1: scine_utilities.Settings) -> None:
        """
        Settings of the calculator
        """
    INTERFACE = 'calculator_with_reference'
    pass
class Log():
    """
        Multi-domain multi-sink logger

        A log object consists of multiple domains. These domains are debug, warning,
        error and output, in ascending order of importance to an end user.

        Each domain has its own set of sinks into which information can be fed.
        Multiple domains can have the same sink. Imagine a breadboard with all the
        little cables that you have to manually connect.

        By default, the debug domain has no sinks. The warning and error domains
        have a sink to stderr named "cerr". The output domain has a sink to stdout
        named "cout".

        >>> log = core.Log()
        >>> log.debug.has_sinks()
        False
        >>> log.error.has_sinks()
        True
        >>> log.debug.line("Hello world")
        >>> log.debug.add("cout", core.Log.cout_sink())
        >>> log.debug.has_sinks()
        True
        >>> log.error.remove("cerr") # Remove the stderr sink from the error domain
        >>> log.error.add("logfile", core.Log.file_sink("errors.log")) # Add a file sink instead
      
    """
    class Domain():
        def __init__(self) -> None: 
            """
            Default initialize
            """
        def add(self, arg0: str, arg1: Sink) -> None: 
            """
            Adds a named sink to the domain
            """
        def clear(self) -> None: 
            """
            Removes all sink from the domain
            """
        def has_sinks(self) -> bool: ...
        def lazy(self, arg0: typing.Callable[[], str]) -> None: 
            """
            Calls a string composing function and sinks its output only if the log has sinks
            """
        def line(self, arg0: str) -> None: 
            """
            Write a line to all sinks
            """
        def remove(self, arg0: str) -> None: 
            """
            Removes a named sink from the domain.
            """
        pass
    def __init__(self) -> None: 
        """
        Default initialize
        """
    @staticmethod
    def cerr_sink() -> Sink: 
        """
        Creates a sink to cerr
        """
    @staticmethod
    def cout_sink() -> Sink: 
        """
        Creates a sink to cout
        """
    @staticmethod
    def file_sink(arg0: str) -> Sink: 
        """
        Creates a file sink
        """
    @staticmethod
    def silent() -> Log: 
        """
        Returns a silent log (i.e. all of its domains have no sinks)
        """
    @property
    def debug(self) -> Log.Domain:
        """
        Access the log's debug domain

        :type: Log.Domain
        """
    @debug.setter
    def debug(self, arg0: Log.Domain) -> None:
        """
        Access the log's debug domain
        """
    @property
    def error(self) -> Log.Domain:
        """
        Access the log's error domain

        :type: Log.Domain
        """
    @error.setter
    def error(self, arg0: Log.Domain) -> None:
        """
        Access the log's error domain
        """
    @property
    def output(self) -> Log.Domain:
        """
        Access the log's output domain

        :type: Log.Domain
        """
    @output.setter
    def output(self, arg0: Log.Domain) -> None:
        """
        Access the log's output domain
        """
    @property
    def warning(self) -> Log.Domain:
        """
        Access the log's warning domain

        :type: Log.Domain
        """
    @warning.setter
    def warning(self, arg0: Log.Domain) -> None:
        """
        Access the log's warning domain
        """
    pass
class Module():
    """
    Abstract base class for a module, which flexibly provides consumers with common interface derived classes.
    """
    def __init__(self) -> None: ...
    pass
class ModuleManager():
    """
        Manager for all dynamically loaded SCINE modules

        SCINE Modules are shared libraries that offer models of the interfaces
        defined in SCINE Core, such as the :class:`core.Calculator`. Generally,
        loading a python module that wraps a particular SCINE project directly
        loads these shared libraries and makes the models it provides available
        through the query interface present here.

        This class is a singleton, accessible via a default ``__init__`` method:

        >>> m = core.ModuleManager()
      
    """
    def __init__(self) -> None: ...
    def get(self, interface: str, model: str) -> typing.Optional[Union[Calculator, CalculatorWithReference]]: 
        """
              Get an instance of an interface model

              :param interface: String name of the interface to check for
              :param model: String name of the model of the interface to check for
              :returns: The model if available, ``None`` otherwise

              >>> m = core.ModuleManager()
              >>> m.get(core.Calculator.INTERFACE, "PM6") # if Sparrow is not loaded
            
        """
    def has(self, interface: str, model: str) -> bool: 
        """
              Check whether a particular model of an interface is available

              :param interface: String name of the interface to check for
              :param model: String name of the model of the interface to check for
              :returns: Whether the model is available

              >>> m = core.ModuleManager()
              >>> m.has(core.Calculator.INTERFACE, "PM6") # If Sparrow is not loaded
              False
            
        """
    def load(self, filename: str) -> None: 
        """
              Load a module file

              SCINE Module files have the suffix ``.module.so`` to clearly disambiguate
              them from general-purpose shared libraries.
            
        """
    def load_module(self, module: Module) -> None: 
        """
              Load a module object directly.
            
        """
    def models(self, interface: str) -> typing.List[str]: 
        """
              List of available models of an interface

              Collects all classes modeling a particular interface. If no further
              SCINE python modules such as Sparrow are loaded, the list of models for
              the calculator is empty. Some external quantum chemical software is
              auto-detected and made available via the :class:`core.Calculator`
              interface, so your mileage may vary.

              :param interface: String name of the interface to check for
              :returns: List of string names of models of the interface argument. You
                can use these as arguments to the ``get`` function.

              >>> m = core.ModuleManager()
              >>> m.models(core.Calculator.INTERFACE)
              ['TEST', 'LENNARDJONES']
            
        """
    def module_loaded(self, module: str) -> bool: 
        """
              Check whether a particular module is loaded

              :param module: Name of the module to check for
              :returns: Whether the module is loaded

              >>> m = core.ModuleManager()
              >>> m.module_loaded("Sparrow")
              False
            
        """
    @property
    def interfaces(self) -> typing.List[str]:
        """
        List of interfaces for which at least one model is loaded

        :type: typing.List[str]
        """
    @property
    def modules(self) -> typing.List[str]:
        """
        List of loaded module names

        :type: typing.List[str]
        """
    pass
class StateHandableObject():
    pass
class Sink():
    """
    Abstract object into which logging information can be sunk
    """
    pass
class State():
    pass
class Calculator(StateHandableObject, ObjectWithStructure):
    """
    The Calculator is the abstract base for classes running electronic structure calculations.
    """
    def __init__(self) -> None: 
        """
        Default Constructor
        """
    def calculate(self, dummy: str = '') -> scine_utilities.Results: 
        """
        Execute the calculation
        """
    def clone(self) -> Calculator: 
        """
        Yields a copy of the calculator
        """
    def get_possible_properties(self) -> scine_utilities.PropertyList: 
        """
        Yields a list of properties that the calculator can calculate
        """
    def get_results(self) -> scine_utilities.Results: 
        """
        Get any stored results.
        """
    def has_results(self) -> bool: 
        """
        Check if results are present.
        """
    def name(self) -> str: 
        """
        Yields the name of the calculator
        """
    @typing.overload
    def set_required_properties(self, arg0: scine_utilities.PropertyList) -> None: 
        """
        Set the required properties

        Set the required properties
        """
    @typing.overload
    def set_required_properties(self, arg0: typing.List[scine_utilities.Property]) -> None: ...
    def shared_from_this(self) -> Calculator: 
        """
        Yields a shared pointer to copy of the calculator
        """
    @property
    def log(self) -> Log:
        """
        Logger of the calculator.

        :type: Log
        """
    @log.setter
    def log(self, arg1: Log) -> None:
        """
        Logger of the calculator.
        """
    @property
    def positions(self) -> numpy.ndarray:
        """
        Positions of the molecular structure

        :type: numpy.ndarray
        """
    @positions.setter
    def positions(self, arg1: numpy.ndarray) -> None:
        """
        Positions of the molecular structure
        """
    @property
    def settings(self) -> scine_utilities.Settings:
        """
        Settings of the calculator

        :type: scine_utilities.Settings
        """
    @settings.setter
    def settings(self, arg1: scine_utilities.Settings) -> None:
        """
        Settings of the calculator
        """
    @property
    def structure(self) -> scine_utilities.AtomCollection:
        """
        The molecular structure to calculate

        :type: scine_utilities.AtomCollection
        """
    @structure.setter
    def structure(self, arg1: scine_utilities.AtomCollection) -> None:
        """
        The molecular structure to calculate
        """
    INTERFACE = 'calculator'
    pass
class WavefunctionOutputGenerator():
    """
    The WavefunctionOutputGenerator is the abstract base for classes obtaining information based on a wavefunction, f.i. a molden input file from a converged SCF.
    """
    def output_wavefunction(self) -> str: 
        """
        Outputs the wavefunction. For instance, the molecular orbitals for visualization.
        """
    def wavefunction2file(self, arg0: str) -> None: 
        """
        Outputs the wavefunction. For instance, the molecular orbitals for visualization, in a file.
        """
    @property
    def settings(self) -> scine_utilities.Settings:
        """
        Settings of the wavefunction output generator

        :type: scine_utilities.Settings
        """
    @settings.setter
    def settings(self, arg1: scine_utilities.Settings) -> None:
        """
        Settings of the wavefunction output generator
        """
    INTERFACE = 'wavefunction_output_generator'
    pass
def get_available_settings(method_family: str, program: str = 'Any') -> scine_utilities.Settings:
    """
    Gives the available default settings of a Calculator with the given method and from the given program
    """
def get_calculator(method_family: str, program: str = 'Any') -> Calculator:
    """
    Generates a calculator with the given method and from the given program.
    """
def get_possible_properties(method_family: str, program: str = 'Any') -> scine_utilities.PropertyList:
    """
    Lists the available properties of a Calculator with the given method and from the given program.
    """
def has_calculator(method_family: str, program: str = 'Any') -> bool:
    """
    Checks if a calculator with the given method and the given program is available.
    """
def load_system(path: str, method_family: str, **kwargs) -> Calculator:
    """
    Loads a single system (xyz-file) into a Calculator with the given method and optional settings. (Deprecated)
    """
def load_system_into_calculator(path: str, method_family: str, **kwargs) -> Calculator:
    """
    Loads a single system (xyz-file) into a Calculator with the given method and optional settings.
    """
def to_wf_generator(arg0: Union[Calculator, CalculatorWithReference]) -> WavefunctionOutputGenerator:
    pass
