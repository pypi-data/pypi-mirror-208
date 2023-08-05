"""Python bindings for SCINE-Database"""
import scine_database
import typing
from typing import Union
import scine_database.layout as layout
import datetime
import numpy
import scine_utilities
import scine_utilities.bsplines
import scipy.sparse

__all__ = [
    "BoolProperty",
    "Calculation",
    "Collection",
    "Compound",
    "CompoundOrFlask",
    "Credentials",
    "DenseMatrixProperty",
    "ElementaryStep",
    "ElementaryStepType",
    "Flask",
    "ID",
    "Job",
    "Label",
    "Manager",
    "Model",
    "NumberProperty",
    "Object",
    "Property",
    "Reaction",
    "Results",
    "Side",
    "SparseMatrixProperty",
    "Status",
    "StringProperty",
    "Structure",
    "VectorProperty",
    "database_version",
    "layout",
    "levenshtein_distance"
]


class Object():
    """
        Base class for any object stored in a database

        Objects by data representation consist of optionally an ID and optionally a
        linked collection. IDs in MongoDB are unique within a collection only, so
        a database object must be represented both by a collection and an ID.

        So in principle there are four possible states for the data in this object.
        Only if both ID and collection are populated can database operations against
        existing data succeed. In all other states, data access and modification of
        existing data will raise exceptions.

        :example:
        >>> property = NumberProperty()  # Empty init: No ID, no collection
        >>> isinstance(property, Object)  # This is a derived Object class
        True
        >>> property.data  # Try to access database data
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        RuntimeError: Missing linked collection.
        >>> property.link(manager.get_collection("properties"))
        >>> property.data
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        RuntimeError: The Object is missing an ID to be used in this context.

        ..note: It is important to consider that no ``Object`` class caches data.
                All methods and properties read or write data from the database so
                it is important to consider this when writing code.
      
    """
    def __str__(self) -> str: ...
    def analyze(self) -> bool: ...
    def created(self) -> datetime.datetime: 
        """
              Fetches the time when an object was created in the database

              :raises RuntimeError: If no collection is linked or the object has no ID.
                See `link` and `has_link`.
            
        """
    def detach(self) -> None: 
        """
              Unlinks the instance, removing the collection pointer. Subsequent calls
              attempting to alter database data cannot cause changes in the database.
            
        """
    def disable_analysis(self) -> None: ...
    def disable_exploration(self) -> None: ...
    def enable_analysis(self) -> None: ...
    def enable_exploration(self) -> None: ...
    def exists(self) -> bool: 
        """
              Checks if the object exists in the linked collection

              :raises RuntimeError: If no collection is linked or the object has no ID.
                See `link` and `has_link`.
            
        """
    def explore(self) -> bool: ...
    def get_collection(self) -> Collection: ...
    def get_id(self) -> ID: 
        """
        Returns the ID of the object
        """
    def has_created_timestamp(self) -> bool: ...
    def has_id(self) -> bool: 
        """
        Checks if the object has an ID
        """
    def has_last_modified_timestamp(self) -> bool: ...
    def has_link(self) -> bool: 
        """
              Returns whether the object is linked to a collection or not. If the
              object is unlinked, database interaction is limited and many interface
              functions can raise errors.
            
        """
    def id(self) -> ID: 
        """
        Returns the ID of the object
        """
    def json(self) -> str: 
        """
        Fetches the JSON representation of the object's contents
        """
    def last_modified(self) -> datetime.datetime: 
        """
              Fetches the time when an object was last modified in the database

              :raises RuntimeError: If no collection is linked or the object has no ID.
                See `link` and `has_link`.
            
        """
    def link(self, collection: Collection) -> None: 
        """
              Link the object to a collection. All calls to other functions will then
              try to edit/create a document for this object in the linked collection
              with the given/generated ID.

              :param collection: The collection to link this object to
            
        """
    def older_than(self, other: Object, modification: bool = False) -> bool: 
        """
              Compares the database timestamps of two objects

              :param other: Object to compare timestamps against
              :param modification: Selects which timestamps to compare. If true,
                compares the last modified time. If false, compares the time of creation.

              :raises RuntimeError: If no collection is linked or the object has no ID.
                See `link` and `has_link`.
            
        """
    def print(self) -> None: 
        """
        Prints a JSON string of the object's contents
        """
    def touch(self) -> None: 
        """
              Sets or updates the last modified timestamp of this object in the database

              :raises RuntimeError: If no collection is linked or the object has no ID.
                See `link` and `has_link`.
            
        """
    def wipe(self, expect_presence: bool = False) -> None: 
        """
              Remove the object from the linked collection in a database

              Will also remove the ID from this object, if one is present.

              :param expect_presence: Raise an error if the object does not exist in
                the database
            
        """
    pass
class Calculation(Object):
    """
          Class referencing a calculation database object

          A Calculation is conceptualized as the data necessary to schedule, run
          and store the results of a time-intensive calculation.

          Calculations have the following relationships to other database objects:
          - ``Structure``: Calculations are performed on input structures and can
            produce output structures.
          - ``Property``: Calculations can generate new properties on input or output
            structures
          - ``ElementaryStep``: Calculations may generate elementary step objects
            linking structures by transition states

          Calculations' data representation consists of many parts. Conceptually,
          it can be separated into scheduling details, inputs and outputs. The
          scheduling details comprise the ``Job`` data, the ``priority``,
          ``status`` and ``executor``.

          :example:
          >>> collection = manager.get_collection("calculations")
          >>> model = Model("dft", "pbe", "def2-svp")
          >>> job = Job("single_point")
          >>> calculation = Calculation.make(model, job, [ID(), ID()], collection)
          >>> calculation.status == Status.CONSTRUCTION
          True
          >>> calculation.priority
          10
          >>> calculation.model.method_family = "pffft"  # WARNING: This does nothing!
          >>> calculation.model.method_family
          'dft'
          >>> model.method_family = "pffft"  # Manipulate a local dataclass instance
          >>> calculation.model = model  # Overwrite the database representation
          >>> calculation.model.method_family
          'pffft'

          The inputs of the calculation are composed of the input structures and
          the ``settings``. Settings are a specially typed collection of various
          data structures, in what is essentially a nested string-any dictionary.
          The settings allow data specific to the job to be abstracted away in
          a regularized form.

          :example:
          >>> collection = manager.get_collection("calculations")
          >>> job = Job("remy")
          >>> model = Model("cooking", "heat", "oven")
          >>> calculation = Calculation.make(model, job, [ID(), ID()], collection)
          >>> import scine_utilities as utils
          >>> settings = utils.ValueCollection()
          >>> settings["temperature"] = 180.0
          >>> settings["temperature_unit"] = "celsius"
          >>> ingredients = {"tomatoes": 20, "kohlrabi": 2, "chillies": 1, "olive_oil": True}
          >>> settings["ingredients"] = utils.ValueCollection(ingredients)  # Nesting!
          >>> calculation.set_settings(settings)

          The outputs of a calculation are stored in ``raw_output``,
          ``auxiliaries`` and ``results``. The raw output generally lists captured
          standard output and error output of the job. Auxiliaries are intended as
          relatively hints for interpreting the results (e.g. labels for a new
          structure or relationships between them). ``Results`` group
          database objects generated during calculation execution.
        
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    def add_structure(self, id: ID) -> None: ...
    def clear_auxiliaries(self) -> None: ...
    def clear_comment(self) -> None: ...
    def clear_executor(self) -> None: ...
    def clear_raw_output(self) -> None: ...
    def clear_results(self) -> None: ...
    def clear_runtime(self) -> None: ...
    def clear_settings(self) -> None: ...
    def clear_structures(self) -> None: ...
    def create(self, model: Model, job: Job, structures: typing.List[ID]) -> ID: ...
    def get_auxiliaries(self) -> typing.Dict[str, ID]: ...
    def get_auxiliary(self, key: str) -> ID: ...
    def get_comment(self) -> str: ...
    def get_executor(self) -> str: ...
    def get_job(self) -> Job: ...
    def get_model(self) -> Model: ...
    def get_priority(self) -> int: ...
    def get_raw_output(self) -> str: ...
    def get_results(self) -> Results: ...
    def get_runtime(self) -> float: ...
    def get_setting(self, key: str) -> Union[bool, int, float, str, scine_utilities.ValueCollection, scine_utilities.ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[scine_utilities.ValueCollection]]: ...
    def get_settings(self) -> scine_utilities.ValueCollection: ...
    def get_status(self) -> Status: ...
    @typing.overload
    def get_structures(self) -> typing.List[ID]: ...
    @typing.overload
    def get_structures(self, manager: Manager, collection: str) -> typing.List[Structure]: ...
    def has_auxiliary(self, key: str) -> bool: ...
    def has_comment(self) -> bool: ...
    def has_executor(self) -> bool: ...
    def has_raw_output(self) -> bool: ...
    def has_runtime(self) -> bool: ...
    def has_setting(self, key: str) -> bool: ...
    def has_structure(self, id: ID) -> bool: ...
    @staticmethod
    def make(model: Model, job: Job, structures: typing.List[ID], collection: Collection) -> Calculation: ...
    def remove_auxiliary(self, key: str) -> None: ...
    def remove_setting(self, key: str) -> None: ...
    def remove_structure(self, id: ID) -> None: ...
    def set_auxiliaries(self, auxiliaries: typing.Dict[str, ID]) -> None: ...
    def set_auxiliary(self, key: str, id: ID) -> None: ...
    def set_comment(self, comment: str) -> None: ...
    def set_executor(self, executor: str) -> None: ...
    def set_job(self, job: Job) -> None: ...
    def set_model(self, model: Model) -> None: ...
    def set_priority(self, priority: int) -> None: ...
    def set_raw_output(self, raw_output: str) -> None: ...
    def set_results(self, results: Results) -> None: ...
    def set_runtime(self, runtime: float) -> None: ...
    def set_setting(self, key: str, value: Union[bool, int, float, str, scine_utilities.ValueCollection, scine_utilities.ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[scine_utilities.ValueCollection]]) -> None: ...
    def set_settings(self, settings: scine_utilities.ValueCollection) -> None: ...
    def set_status(self, status: Status) -> None: ...
    def set_structures(self, structures: typing.List[ID]) -> None: ...
    @property
    def comment(self) -> typing.Optional[str]:
        """
        Comment for the calculation

        :type: typing.Optional[str]
        """
    @comment.setter
    def comment(self, arg1: typing.Optional[str]) -> None:
        """
        Comment for the calculation
        """
    @property
    def executor(self) -> typing.Optional[str]:
        """
        Identifies the program/runner that executes the calculation

        :type: typing.Optional[str]
        """
    @executor.setter
    def executor(self, arg1: typing.Optional[str]) -> None:
        """
        Identifies the program/runner that executes the calculation
        """
    @property
    def job(self) -> Job:
        """
        :type: Job
        """
    @job.setter
    def job(self, arg1: Job) -> None:
        pass
    @property
    def model(self) -> Model:
        """
        The methodological details to apply in the calculation

        :type: Model
        """
    @model.setter
    def model(self, arg1: Model) -> None:
        """
        The methodological details to apply in the calculation
        """
    @property
    def priority(self) -> int:
        """
        :type: int
        """
    @priority.setter
    def priority(self, arg1: int) -> None:
        pass
    @property
    def raw_output(self) -> typing.Optional[str]:
        """
        Raw output of the calculation

        :type: typing.Optional[str]
        """
    @raw_output.setter
    def raw_output(self, arg1: typing.Optional[str]) -> None:
        """
        Raw output of the calculation
        """
    @property
    def runtime(self) -> typing.Optional[float]:
        """
        Runtime of the calculation in seconds

        :type: typing.Optional[float]
        """
    @runtime.setter
    def runtime(self, arg1: typing.Optional[float]) -> None:
        """
        Runtime of the calculation in seconds
        """
    @property
    def status(self) -> Status:
        """
        Stage of a calculation's existence

        :type: Status
        """
    @status.setter
    def status(self, arg1: Status) -> None:
        """
        Stage of a calculation's existence
        """
    pass
class Collection():
    def count(self, selection: str) -> int: ...
    def find(self, arg0: str) -> typing.Optional[Union[BoolProperty, Calculation, Compound, DenseMatrixProperty, ElementaryStep, NumberProperty, Reaction, SparseMatrixProperty, StringProperty, Structure, VectorProperty, Flask]]: 
        """
              Finds a single arbitrary object in this collection by a query and returns
              it (linked to the current collection), if found. Returns ``None`` otherwise.
            
        """
    def get_and_update_one_calculation(self, filter: str, update: str = '', sort: str = '') -> Calculation: ...
    def get_and_update_one_compound(self, filter: str, update: str = '', sort: str = '') -> Compound: ...
    def get_and_update_one_elementary_step(self, filter: str, update: str = '', sort: str = '') -> ElementaryStep: ...
    def get_and_update_one_flask(self, filter: str, update: str = '', sort: str = '') -> Flask: ...
    def get_and_update_one_property(self, filter: str, update: str = '', sort: str = '') -> Property: ...
    def get_and_update_one_reaction(self, filter: str, update: str = '', sort: str = '') -> Reaction: ...
    def get_and_update_one_structure(self, filter: str, update: str = '', sort: str = '') -> Structure: ...
    def get_calculation(self, calculation: ID) -> Calculation: ...
    def get_compound(self, compound: ID) -> Compound: ...
    def get_dense_matrix_property(self, property: ID) -> DenseMatrixProperty: ...
    def get_elementary_step(self, reaction_path: ID) -> ElementaryStep: ...
    def get_flasks(self, flask: ID) -> Flask: ...
    def get_number_property(self, property: ID) -> NumberProperty: ...
    def get_one_calculation(self, filter: str, sort: str = '') -> typing.Optional[Calculation]: ...
    def get_one_compound(self, filter: str, sort: str = '') -> typing.Optional[Compound]: ...
    def get_one_elementary_step(self, filter: str, sort: str = '') -> typing.Optional[ElementaryStep]: ...
    def get_one_flask(self, filter: str, sort: str = '') -> typing.Optional[Flask]: ...
    def get_one_property(self, filter: str, sort: str = '') -> typing.Optional[Property]: ...
    def get_one_reaction(self, filter: str, sort: str = '') -> typing.Optional[Reaction]: ...
    def get_one_structure(self, filter: str, sort: str = '') -> typing.Optional[Structure]: ...
    def get_property(self, property: ID) -> Property: ...
    def get_reaction(self, reaction: ID) -> Reaction: ...
    def get_sparse_matrix_property(self, property: ID) -> SparseMatrixProperty: ...
    def get_structure(self, structure: ID) -> Structure: ...
    def get_vector_property(self, property: ID) -> VectorProperty: ...
    def has(self, id: ID) -> bool: ...
    def has_calculation(self, id: ID) -> bool: ...
    def has_compound(self, id: ID) -> bool: ...
    def has_elementary_step(self, id: ID) -> bool: ...
    def has_flask(self, id: ID) -> bool: ...
    def has_property(self, id: ID) -> bool: ...
    def has_reaction(self, id: ID) -> bool: ...
    def has_structure(self, id: ID) -> bool: ...
    def iterate_all_calculations(self) -> typing.Iterator: ...
    def iterate_all_compounds(self) -> typing.Iterator: ...
    def iterate_all_elementary_steps(self) -> typing.Iterator: ...
    def iterate_all_flasks(self) -> typing.Iterator: ...
    def iterate_all_properties(self) -> typing.Iterator: ...
    def iterate_all_reactions(self) -> typing.Iterator: ...
    def iterate_all_structures(self) -> typing.Iterator: ...
    def iterate_calculations(self, selection: str) -> typing.Iterator: ...
    def iterate_compounds(self, selection: str) -> typing.Iterator: ...
    def iterate_elementary_steps(self, selection: str) -> typing.Iterator: ...
    def iterate_flasks(self, selection: str) -> typing.Iterator: ...
    def iterate_properties(self, selection: str) -> typing.Iterator: ...
    def iterate_reactions(self, selection: str) -> typing.Iterator: ...
    def iterate_structures(self, selection: str) -> typing.Iterator: ...
    def query_calculations(self, selection: str) -> typing.List[Calculation]: ...
    def query_compounds(self, selection: str) -> typing.List[Compound]: ...
    def query_elementary_steps(self, selection: str) -> typing.List[ElementaryStep]: ...
    def query_flasks(self, selection: str) -> typing.List[Flask]: ...
    def query_properties(self, selection: str) -> typing.List[Property]: ...
    def query_reactions(self, selection: str) -> typing.List[Reaction]: ...
    def query_structures(self, selection: str) -> typing.List[Structure]: ...
    def random_select_calculations(self, n_samples: int) -> typing.List[Calculation]: ...
    def random_select_compounds(self, n_samples: int) -> typing.List[Compound]: ...
    def random_select_elementary_steps(self, n_samples: int) -> typing.List[ElementaryStep]: ...
    def random_select_flasks(self, n_samples: int) -> typing.List[Flask]: ...
    def random_select_properties(self, n_samples: int) -> typing.List[Property]: ...
    def random_select_reactions(self, n_samples: int) -> typing.List[Reaction]: ...
    def random_select_structures(self, n_samples: int) -> typing.List[Structure]: ...
    pass
class Compound(Object):
    @typing.overload
    def __init__(self) -> None: 
        """
              Create a new compound with a database ID. A Compound in this state is not
              linked to any collection and most interface functions will raise Errors.
            
        """
    @typing.overload
    def __init__(self, id: ID) -> None: ...
    @typing.overload
    def __init__(self, id: ID, collection: Collection) -> None: ...
    def add_reaction(self, id: ID) -> None: ...
    def add_structure(self, id: ID) -> None: ...
    def clear_reactions(self) -> None: ...
    def clear_structures(self) -> None: ...
    def create(self, structure_ids: typing.List[ID]) -> ID: 
        """
              Generates a new compound in the linked collection from a list of
              structure IDs.

              :raises RuntimeError: If no collection is linked.

              :returns: The ID of the generated compound.
            
        """
    @typing.overload
    def get_centroid(self) -> ID: 
        """
              Returns the first entry in the vector of structures

              :raises RuntimeError: If no collection is linked.
            

        Fetch the first entry in the list of structures belonging to the compound
        """
    @typing.overload
    def get_centroid(self, manager: Manager, collection: str = 'structures') -> Structure: ...
    @typing.overload
    def get_reactions(self) -> typing.List[ID]: 
        """
        Fetch all reactions known for the compound
        """
    @typing.overload
    def get_reactions(self, manager: Manager, collection: str = 'reactions') -> typing.List[Reaction]: ...
    @typing.overload
    def get_structures(self) -> typing.List[ID]: 
        """
        Fetch all structures belonging to the compound
        """
    @typing.overload
    def get_structures(self, manager: Manager, collection: str = 'structures') -> typing.List[Structure]: ...
    def has_reaction(self, id: ID) -> bool: 
        """
              Checks if the compound is part of a given reaction by its ID.

              :raises RuntimeError: If no collection is linked.
            
        """
    def has_reactions(self) -> int: ...
    def has_structure(self, id: ID) -> bool: ...
    def has_structures(self) -> int: ...
    @staticmethod
    def make(structure_ids: typing.List[ID], collection: Collection) -> Compound: ...
    def remove_reaction(self, id: ID) -> None: ...
    def remove_structure(self, id: ID) -> None: ...
    def set_reactions(self, ids: typing.List[ID]) -> None: ...
    def set_structures(self, ids: typing.List[ID]) -> None: ...
    pass
class CompoundOrFlask():
    """
    Members:

      COMPOUND

      FLASK
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    COMPOUND: scine_database.CompoundOrFlask # value = <CompoundOrFlask.COMPOUND: 0>
    FLASK: scine_database.CompoundOrFlask # value = <CompoundOrFlask.FLASK: 1>
    __members__: dict # value = {'COMPOUND': <CompoundOrFlask.COMPOUND: 0>, 'FLASK': <CompoundOrFlask.FLASK: 1>}
    pass
class Credentials():
    def __eq__(self, arg0: Credentials) -> bool: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, ip: str, port: int, database: str, username: str = '', password: str = '', auth_database: str = '') -> None: ...
    def __ne__(self, arg0: Credentials) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    @property
    def authDatabase(self) -> str:
        """
        :type: str
        """
    @authDatabase.setter
    def authDatabase(self, arg0: str) -> None:
        pass
    @property
    def auth_database(self) -> str:
        """
        :type: str
        """
    @auth_database.setter
    def auth_database(self, arg0: str) -> None:
        pass
    @property
    def databaseName(self) -> str:
        """
        :type: str
        """
    @databaseName.setter
    def databaseName(self, arg0: str) -> None:
        pass
    @property
    def database_name(self) -> str:
        """
        :type: str
        """
    @database_name.setter
    def database_name(self, arg0: str) -> None:
        pass
    @property
    def hostname(self) -> str:
        """
        :type: str
        """
    @hostname.setter
    def hostname(self, arg0: str) -> None:
        pass
    @property
    def password(self) -> str:
        """
        :type: str
        """
    @password.setter
    def password(self, arg0: str) -> None:
        pass
    @property
    def port(self) -> int:
        """
        :type: int
        """
    @port.setter
    def port(self, arg0: int) -> None:
        pass
    @property
    def username(self) -> str:
        """
        :type: str
        """
    @username.setter
    def username(self, arg0: str) -> None:
        pass
    __hash__ = None
    pass
class Property(Object):
    """
          Base class for datatype-differentiated derived property classes

          A ``Property`` represents named calculated properties of structures.

          :note: This class is, data-wise, merely a database pointer. Nearly all
            methods or properties invoke a database operation. No data is cached. Be
            wary of performance pitfalls in failing to cache reused large objects.

          Relationships with other database objects:
          - ``Calculation``: Calculations can generate new properties during
            execution and reference these in their result data.
          - ``Structure``: Properties are usually calculated on the basis of
            structures and refer back to these.

          Properties consist of a name identifier and a model that describes how
          the property data was calculated. Optionally, a free-form comment string
          can be added.

          :example:
          >>> properties = manager.get_collection("properties")
          >>> model = Model("dft", "pbe", "def2-svp")
          >>> p = NumberProperty.make("energy", model, 42.0, properties)
          >>> isinstance(p, Property)  # NumberProperty is a derived Property
          True
          >>> p.name
          'energy'
          >>> p.comment = "answer to life, the universe and everything"

          Properties can link to a ``Calculation`` and ``Structure`` instance,
          usually referring back to the structure the property was calculated for
          and the calculation that performed that calculation.

          :example:
          >>> calculations = manager.get_collection("calculations")
          >>> model = Model("dft", "pbe", "def2-svp")
          >>> job = Job("single_point")
          >>> bogus_id = ID()  # Bogus ID referencing a non-existent structure
          >>> calculation = Calculation.make(model, job, [bogus_id], calculations)
          >>> properties = manager.get_collection("properties")
          >>> p = NumberProperty.make("energy", model, 42.0, properties)
          >>> p.calculation_id is None
          True
          >>> p.calculation_id = calculation.id()
          >>> p.calculation_id is None
          False
          >>> p.structure_id is None  # We haven't linked a structure
          True

          Derived property classes have a ``data`` member property whose type
          depends on the kind of data stored in the database for it.
        
    """
    @typing.overload
    def __init__(self, arg0: ID) -> None: 
        """
        Constructs an unlinked property. Cannot use any methods besides ``link``.


              Construct a Property representing an existing entry in a passed collection

              :param id: Id of the property in the database
              :param collection: The collection the property is in
            
        """
    @typing.overload
    def __init__(self, id: ID, collection: Collection) -> None: ...
    def clear_calculation(self) -> None: ...
    def clear_comment(self) -> None: ...
    def clear_structure(self) -> None: ...
    def get_calculation(self) -> ID: ...
    def get_comment(self) -> str: ...
    def get_derived(self) -> Union[BoolProperty, DenseMatrixProperty, NumberProperty, SparseMatrixProperty, StringProperty, VectorProperty]: 
        """
              Fetch the derived property for this base class instance

              Instantiates the right derived property type referring to the same
              database object.

              :example:
              >>> properties = manager.get_collection("properties")
              >>> model = Model("dft", "pbe", "def2-svp")
              >>> derived = NumberProperty.make("energy", model, 1.0, properties)
              >>> property = Property(derived.id(), properties)
              >>> derived_again = property.get_derived()
              >>> isinstance(derived_again, NumberProperty)
              True
              >>> derived.id() == property.id() == derived_again.id()
              True
              >>> derived_again.data
              1.0
            
        """
    def get_model(self) -> Model: ...
    def get_property_name(self) -> str: ...
    def get_structure(self) -> ID: ...
    def has_calculation(self) -> bool: ...
    def has_comment(self) -> bool: ...
    def has_structure(self) -> bool: ...
    def set_calculation(self, calculation: ID) -> None: ...
    def set_comment(self, comment: str) -> None: ...
    def set_model(self, model: Model) -> None: ...
    def set_property_name(self, property_name: str) -> None: ...
    def set_structure(self, structure: ID) -> None: ...
    @property
    def calculation_id(self) -> typing.Optional[ID]:
        """
        ID referencing the calculation where this property was calculated. Can be ``None``

        :type: typing.Optional[ID]
        """
    @calculation_id.setter
    def calculation_id(self, arg1: typing.Optional[ID]) -> None:
        """
        ID referencing the calculation where this property was calculated. Can be ``None``
        """
    @property
    def comment(self) -> typing.Optional[str]:
        """
        Free-form string comment on the property. Can be ``None``.

        :type: typing.Optional[str]
        """
    @comment.setter
    def comment(self, arg1: typing.Optional[str]) -> None:
        """
        Free-form string comment on the property. Can be ``None``.
        """
    @property
    def model(self) -> Model:
        """
        Model used to calculate the data

        :type: Model
        """
    @model.setter
    def model(self, arg1: Model) -> None:
        """
        Model used to calculate the data
        """
    @property
    def name(self) -> str:
        """
        Name of the property

        :type: str
        """
    @name.setter
    def name(self, arg1: str) -> None:
        """
        Name of the property
        """
    @property
    def structure_id(self) -> typing.Optional[ID]:
        """
        ID referencing the structure from which this property was calculated. Can be ``None``

        :type: typing.Optional[ID]
        """
    @structure_id.setter
    def structure_id(self, arg1: typing.Optional[ID]) -> None:
        """
        ID referencing the structure from which this property was calculated. Can be ``None``
        """
    pass
class ElementaryStep(Object):
    """
          Two sets of structures connected by a transition state

          An elementary step has the following relationships to other database
          objects:
          - ``Structure``: An elementary step connects two sets of structures, one
            set on each side of the transition state
          - ``Reaction``: A reaction groups elementary steps, abstracting away
            conformational differences between structures.

          Data-wise, the elementary step consists of a transition state
          ``Structure``, two sets of ``Structures``, one on each ``Side`` of the
          transition state, and a linked ``Reaction``.
          The `idx_map` arrays can be used to store which atom indices of the
          (joined) structures on one side of the elementary step correspond to which
          atom indices of the joined structures on the other side or of the
          transition state.

          :example:
          >>> lhs = [ID(), ID()]  # Generate a few placeholder IDs
          >>> rhs = [ID()]
          >>> collection = manager.get_collection("elementary_steps")
          >>> step = ElementaryStep.make(lhs, rhs, collection)
          >>> step.transition_state_id = ID()
          >>> step.reaction_id = ID()
          >>> reactants_tup = step.get_reactants(Side.BOTH)
          >>> reactants_tup == (lhs, rhs)
          True
          >>> step.reactants_counts
          (2, 1)
          >>> step.has_reaction()
          True
          >>> step.add_idx_maps([1, 2, 0, 3]) # Add the lhs-rhs map
          >>> step.has_idx_map(ElementaryStep.IdxMapType.LHS_RHS)
          True
          >>> step.has_idx_map(ElementaryStep.IdxMapType.LHS_TS)
          False
          >>> step.add_idx_maps([1, 2, 0, 3], [1, 3, 0, 2]) # Add the lhs-rhs and lhs-ts map
          >>> step.has_idx_map(ElementaryStep.IdxMapType.LHS_TS)
          True
          >>> step.has_idx_map(ElementaryStep.IdxMapType.TS_RHS) # ts-rhs from combination of stored maps
          True
          >>> step.get_idx_map(ElementaryStep.IdxMapType.TS_RHS)
          [0, 1, 3, 2]
        
    """
    class IdxMapType():
        """
        Members:

          LHS_TS : The atoms index map from lhs to ts.

          LHS_RHS : The atoms index map from lhs to rhs.

          TS_LHS : The atoms index map from ts to lhs.

          RHS_LHS : The atoms index map from rhs to lhs.

          TS_RHS : The atoms index map from ts to rhs.

          RHS_TS : The atoms index map from rhs to ts.
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: object) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        @property
        def name(self) -> str:
            """
            :type: str
            """
        @property
        def value(self) -> int:
            """
            :type: int
            """
        LHS_RHS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.LHS_RHS: 1>
        LHS_TS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.LHS_TS: 0>
        RHS_LHS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.RHS_LHS: 3>
        RHS_TS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.RHS_TS: 5>
        TS_LHS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.TS_LHS: 2>
        TS_RHS: scine_database.ElementaryStep.IdxMapType # value = <IdxMapType.TS_RHS: 4>
        __members__: dict # value = {'LHS_TS': <IdxMapType.LHS_TS: 0>, 'LHS_RHS': <IdxMapType.LHS_RHS: 1>, 'TS_LHS': <IdxMapType.TS_LHS: 2>, 'RHS_LHS': <IdxMapType.RHS_LHS: 3>, 'TS_RHS': <IdxMapType.TS_RHS: 4>, 'RHS_TS': <IdxMapType.RHS_TS: 5>}
        pass
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    def add_idx_maps(self, lhs_rhs_map: typing.List[int], lhs_ts_map: typing.Optional[typing.List[int]] = None) -> None: 
        """
        Adds the atom index map(s). The lhs to ts map is optional.
        """
    def add_reactant(self, id: ID, side: Side) -> None: ...
    def clear_path(self) -> None: ...
    def clear_reactants(self, side: Side) -> None: ...
    def clear_reaction(self) -> None: ...
    def clear_spline(self) -> None: ...
    def clear_transition_state(self) -> None: ...
    def create(self, lhs: typing.List[ID], rhs: typing.List[ID]) -> ID: ...
    def get_barrier_from_spline(self) -> typing.Tuple[float, float]: 
        """
              Returns the rhs and lhs barrier calculated from the spline as a tuple. If no spline is available, (0.0, 0.0)
              is returned.
        """
    def get_idx_map(self, map_type: ElementaryStep.IdxMapType) -> typing.List[int]: 
        """
        Gets the atom index map of the given type.
        """
    @typing.overload
    def get_path(self) -> typing.List[ID]: 
        """
        Fetch all structures belonging to the elementary step's path
        """
    @typing.overload
    def get_path(self, manager: Manager, collection: str = 'structures') -> typing.List[Structure]: ...
    def get_reactants(self, side: Side = Side.BOTH) -> typing.Tuple[typing.List[ID], typing.List[ID]]: ...
    @typing.overload
    def get_reaction(self) -> ID: 
        """
        Fetch the linked reaction instance
        """
    @typing.overload
    def get_reaction(self, manager: Manager, collection: str = 'reactions') -> Reaction: ...
    def get_spline(self) -> scine_utilities.bsplines.TrajectorySpline: ...
    @typing.overload
    def get_transition_state(self) -> ID: 
        """
        Fetch the linked transition state structure
        """
    @typing.overload
    def get_transition_state(self, manager: Manager, collection: str = 'structures') -> Structure: ...
    def get_type(self) -> ElementaryStepType: ...
    def has_idx_map(self, map_type: ElementaryStep.IdxMapType) -> bool: 
        """
        Checks whether a map with the given type exists or can be retrieved from the existing ones.
        """
    def has_path(self) -> int: ...
    def has_reactant(self, id: ID) -> Side: ...
    def has_reactants(self) -> typing.Tuple[int, int]: ...
    def has_reaction(self) -> bool: ...
    def has_spline(self) -> bool: ...
    def has_structure_in_path(self, id: ID) -> bool: ...
    def has_transition_state(self) -> bool: ...
    @staticmethod
    def make(lhs: typing.List[ID], rhs: typing.List[ID], collection: Collection) -> ElementaryStep: ...
    def remove_idx_maps(self) -> None: 
        """
        Removes the atom index maps.
        """
    def remove_reactant(self, id: ID, side: Side) -> None: ...
    def set_path(self, ids: typing.List[ID]) -> None: ...
    def set_reactants(self, ids: typing.List[ID], side: Side) -> None: ...
    def set_reaction(self, reaction_id: ID) -> None: ...
    def set_spline(self, spline: scine_utilities.bsplines.TrajectorySpline) -> None: ...
    def set_transition_state(self, transition_state_id: ID) -> None: ...
    def set_type(self, arg0: ElementaryStepType) -> None: ...
    @property
    def reactants_counts(self) -> typing.Tuple[int, int]:
        """
        :type: typing.Tuple[int, int]
        """
    @property
    def reaction_id(self) -> typing.Optional[ID]:
        """
        The reaction this elementary step belongs to

        :type: typing.Optional[ID]
        """
    @reaction_id.setter
    def reaction_id(self, arg1: typing.Optional[ID]) -> None:
        """
        The reaction this elementary step belongs to
        """
    @property
    def transition_state_id(self) -> typing.Optional[ID]:
        """
        The transition state structure ID

        :type: typing.Optional[ID]
        """
    @transition_state_id.setter
    def transition_state_id(self, arg1: typing.Optional[ID]) -> None:
        """
        The transition state structure ID
        """
    pass
class ElementaryStepType():
    """
    Members:

      REGULAR : A regular elementary step that involves exactly one transition state.

      BARRIERLESS : An elementary step that has no barrier/ transition state
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BARRIERLESS: scine_database.ElementaryStepType # value = <ElementaryStepType.BARRIERLESS: 1>
    REGULAR: scine_database.ElementaryStepType # value = <ElementaryStepType.REGULAR: 0>
    __members__: dict # value = {'REGULAR': <ElementaryStepType.REGULAR: 0>, 'BARRIERLESS': <ElementaryStepType.BARRIERLESS: 1>}
    pass
class Flask(Object):
    @typing.overload
    def __init__(self) -> None: 
        """
              Create a new flask with a database ID. A Flask in this state is not
              linked to any collection and most interface functions will raise Errors.
            
        """
    @typing.overload
    def __init__(self, id: ID) -> None: ...
    @typing.overload
    def __init__(self, id: ID, collection: Collection) -> None: ...
    def add_reaction(self, id: ID) -> None: ...
    def add_structure(self, id: ID) -> None: ...
    def clear_compounds(self) -> None: ...
    def clear_reactions(self) -> None: ...
    def clear_structures(self) -> None: ...
    def create(self, structure_ids: typing.List[ID], compound_ids: typing.List[ID]) -> ID: 
        """
              Generates a new flask in the linked collection from a list of
              structure IDs and compoud IDs. Stores the generated ID in the
              Flask object.

              :raises RuntimeError: If no collection is linked.

              :returns: The ID of the generated flask.
            
        """
    @typing.overload
    def get_centroid(self) -> ID: 
        """
              Returns the first entry in the vector of structures

              :raises RuntimeError: If no collection is linked.
            

        Fetch the first entry in the list of structures belonging to the flask
        """
    @typing.overload
    def get_centroid(self, manager: Manager, collection: str = 'structures') -> Structure: ...
    @typing.overload
    def get_compounds(self) -> typing.List[ID]: 
        """
        Fetch all compounds belonging to the flask
        """
    @typing.overload
    def get_compounds(self, manager: Manager, collection: str = 'compounds') -> typing.List[Compound]: ...
    @typing.overload
    def get_reactions(self) -> typing.List[ID]: 
        """
        Fetch all reactions known for the flask
        """
    @typing.overload
    def get_reactions(self, manager: Manager, collection: str = 'reactions') -> typing.List[Reaction]: ...
    @typing.overload
    def get_structures(self) -> typing.List[ID]: 
        """
        Fetch all structures belonging to the flask
        """
    @typing.overload
    def get_structures(self, manager: Manager, collection: str = 'structures') -> typing.List[Structure]: ...
    def has_compound(self, id: ID) -> bool: ...
    def has_compounds(self) -> int: ...
    def has_reaction(self, id: ID) -> bool: 
        """
              Checks if the flask is part of a given reaction by its ID.

              :raises RuntimeError: If no collection is linked.
            
        """
    def has_reactions(self) -> int: ...
    def has_structure(self, id: ID) -> bool: ...
    def has_structures(self) -> int: ...
    @staticmethod
    def make(structure_ids: typing.List[ID], compound_ids: typing.List[ID], collection: Collection) -> Flask: 
        """
              Create a new flask with a database ID.

              :returns: A Flask object linked to the given collection.
            
        """
    def remove_reaction(self, id: ID) -> None: ...
    def remove_structure(self, id: ID) -> None: ...
    def set_compounds(self, ids: typing.List[ID]) -> None: ...
    def set_reactions(self, ids: typing.List[ID]) -> None: ...
    def set_structures(self, ids: typing.List[ID]) -> None: ...
    pass
class ID():
    """
          A long unique identifier for a database object. Can be represented as a
          hexadecimal string and compared

          >>> first = ID()
          >>> second = ID()
          >>> first < second
          True
          >>> first < second.string()
          True
        
    """
    @typing.overload
    def __eq__(self, arg0: ID) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: str) -> bool: ...
    @typing.overload
    def __ge__(self, arg0: ID) -> bool: ...
    @typing.overload
    def __ge__(self, arg0: str) -> bool: ...
    def __getstate__(self) -> str: ...
    @typing.overload
    def __gt__(self, arg0: ID) -> bool: ...
    @typing.overload
    def __gt__(self, arg0: str) -> bool: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Initialize from an ID string serialization
        """
    @typing.overload
    def __init__(self, id_str: str) -> None: ...
    @typing.overload
    def __le__(self, arg0: ID) -> bool: ...
    @typing.overload
    def __le__(self, arg0: str) -> bool: ...
    @typing.overload
    def __lt__(self, arg0: ID) -> bool: ...
    @typing.overload
    def __lt__(self, arg0: str) -> bool: ...
    def __setstate__(self, arg0: str) -> None: ...
    def __str__(self) -> str: ...
    def string(self) -> str: 
        """
        Convert the identifier to string representation
        """
    __hash__ = None
    pass
class Job():
    """
          A data class representing execution details of the calculation.

          ..note: This class owns its data and is not conceptually a database
                  pointer similar to the database objects.

          A Job comprises only an identifier and minimum requirements on available
          memory, computer cores and disk space.

          :example:
          >>> job = Job("single_point")
          >>> job.cores = 4  # Four computer cores
          >>> job.disk = 2.0  # 2 GB of disk space
          >>> job.memory
          1.0
        
    """
    def __copy__(self) -> Job: ...
    def __deepcopy__(self, arg0: dict) -> Job: ...
    def __eq__(self, arg0: Job) -> bool: ...
    def __getstate__(self) -> tuple: ...
    def __init__(self, order: str) -> None: ...
    def __ne__(self, arg0: Job) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    @property
    def cores(self) -> int:
        """
        Minimum required number of cores

        :type: int
        """
    @cores.setter
    def cores(self, arg0: int) -> None:
        """
        Minimum required number of cores
        """
    @property
    def disk(self) -> float:
        """
        Minimum required disk space in GB

        :type: float
        """
    @disk.setter
    def disk(self, arg0: float) -> None:
        """
        Minimum required disk space in GB
        """
    @property
    def memory(self) -> float:
        """
        Minimum required memory in GB

        :type: float
        """
    @memory.setter
    def memory(self, arg0: float) -> None:
        """
        Minimum required memory in GB
        """
    @property
    def order(self) -> str:
        """
        Summary string of the type of job to be carried out, e.g. 'single_point'

        :type: str
        """
    @order.setter
    def order(self, arg0: str) -> None:
        """
        Summary string of the type of job to be carried out, e.g. 'single_point'
        """
    __hash__ = None
    pass
class Label():
    """
    Members:

      NONE

      IRRELEVANT

      DUPLICATE

      USER_GUESS

      USER_OPTIMIZED

      MINIMUM_GUESS

      MINIMUM_OPTIMIZED

      TS_GUESS

      TS_OPTIMIZED

      ELEMENTARY_STEP_GUESS

      ELEMENTARY_STEP_OPTIMIZED

      REACTIVE_COMPLEX_GUESS

      REACTIVE_COMPLEX_SCANNED

      REACTIVE_COMPLEX_OPTIMIZED

      SURFACE_GUESS

      SURFACE_OPTIMIZED

      SURFACE_ADSORPTION_GUESS

      COMPLEX_OPTIMIZED

      COMPLEX_GUESS
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    COMPLEX_GUESS: scine_database.Label # value = <Label.COMPLEX_GUESS: 15>
    COMPLEX_OPTIMIZED: scine_database.Label # value = <Label.COMPLEX_OPTIMIZED: 16>
    DUPLICATE: scine_database.Label # value = <Label.DUPLICATE: 100>
    ELEMENTARY_STEP_GUESS: scine_database.Label # value = <Label.ELEMENTARY_STEP_GUESS: 7>
    ELEMENTARY_STEP_OPTIMIZED: scine_database.Label # value = <Label.ELEMENTARY_STEP_OPTIMIZED: 8>
    IRRELEVANT: scine_database.Label # value = <Label.IRRELEVANT: 99>
    MINIMUM_GUESS: scine_database.Label # value = <Label.MINIMUM_GUESS: 3>
    MINIMUM_OPTIMIZED: scine_database.Label # value = <Label.MINIMUM_OPTIMIZED: 4>
    NONE: scine_database.Label # value = <Label.NONE: 0>
    REACTIVE_COMPLEX_GUESS: scine_database.Label # value = <Label.REACTIVE_COMPLEX_GUESS: 9>
    REACTIVE_COMPLEX_OPTIMIZED: scine_database.Label # value = <Label.REACTIVE_COMPLEX_OPTIMIZED: 11>
    REACTIVE_COMPLEX_SCANNED: scine_database.Label # value = <Label.REACTIVE_COMPLEX_SCANNED: 10>
    SURFACE_ADSORPTION_GUESS: scine_database.Label # value = <Label.SURFACE_ADSORPTION_GUESS: 14>
    SURFACE_GUESS: scine_database.Label # value = <Label.SURFACE_GUESS: 12>
    SURFACE_OPTIMIZED: scine_database.Label # value = <Label.SURFACE_OPTIMIZED: 13>
    TS_GUESS: scine_database.Label # value = <Label.TS_GUESS: 5>
    TS_OPTIMIZED: scine_database.Label # value = <Label.TS_OPTIMIZED: 6>
    USER_GUESS: scine_database.Label # value = <Label.USER_GUESS: 1>
    USER_OPTIMIZED: scine_database.Label # value = <Label.USER_OPTIMIZED: 2>
    __members__: dict # value = {'NONE': <Label.NONE: 0>, 'IRRELEVANT': <Label.IRRELEVANT: 99>, 'DUPLICATE': <Label.DUPLICATE: 100>, 'USER_GUESS': <Label.USER_GUESS: 1>, 'USER_OPTIMIZED': <Label.USER_OPTIMIZED: 2>, 'MINIMUM_GUESS': <Label.MINIMUM_GUESS: 3>, 'MINIMUM_OPTIMIZED': <Label.MINIMUM_OPTIMIZED: 4>, 'TS_GUESS': <Label.TS_GUESS: 5>, 'TS_OPTIMIZED': <Label.TS_OPTIMIZED: 6>, 'ELEMENTARY_STEP_GUESS': <Label.ELEMENTARY_STEP_GUESS: 7>, 'ELEMENTARY_STEP_OPTIMIZED': <Label.ELEMENTARY_STEP_OPTIMIZED: 8>, 'REACTIVE_COMPLEX_GUESS': <Label.REACTIVE_COMPLEX_GUESS: 9>, 'REACTIVE_COMPLEX_SCANNED': <Label.REACTIVE_COMPLEX_SCANNED: 10>, 'REACTIVE_COMPLEX_OPTIMIZED': <Label.REACTIVE_COMPLEX_OPTIMIZED: 11>, 'SURFACE_GUESS': <Label.SURFACE_GUESS: 12>, 'SURFACE_OPTIMIZED': <Label.SURFACE_OPTIMIZED: 13>, 'SURFACE_ADSORPTION_GUESS': <Label.SURFACE_ADSORPTION_GUESS: 14>, 'COMPLEX_OPTIMIZED': <Label.COMPLEX_OPTIMIZED: 16>, 'COMPLEX_GUESS': <Label.COMPLEX_GUESS: 15>}
    pass
class Manager():
    def __init__(self) -> None: ...
    def connect(self, expect_initialized_db: bool = False, connection_timeout: int = 60, access_timeout: int = 0) -> None: ...
    def disconnect(self) -> None: ...
    def get_collection(self, name: str, expectpresent: bool = True) -> Collection: ...
    def get_credentials(self) -> Credentials: ...
    def get_database_name(self) -> str: ...
    def get_db_version(self) -> typing.Tuple[int, int, int]: ...
    def has_collection(self, arg0: str) -> bool: ...
    def has_credentials(self) -> bool: ...
    def init(self, more_indices: bool = True) -> None: ...
    def is_connected(self) -> bool: ...
    def server_time(self) -> datetime.datetime: ...
    def set_credentials(self, arg0: Credentials) -> None: ...
    def set_database_name(self, arg0: str) -> None: ...
    def version_matches_wrapper(self) -> bool: ...
    def wipe(self, remote: bool = False) -> None: ...
    @property
    def connected(self) -> bool:
        """
        :type: bool
        """
    @property
    def credentials(self) -> Credentials:
        """
        :type: Credentials
        """
    @credentials.setter
    def credentials(self, arg1: Credentials) -> None:
        pass
    @property
    def database_name(self) -> str:
        """
        :type: str
        """
    @database_name.setter
    def database_name(self, arg1: str) -> None:
        pass
    pass
class Model():
    """
          Data class for the model used for a quantum chemical calculation. Data is
          free-form, stored as strings. These should generally be lowercase. Three
          special values exist:

          - ``none``: The parameter is is off or not applicable. For instance,
            ``solvation`` may be ``none`` to indicate a calculation is carried out
            in the gas phase. Empty strings are also interpreted as ``none``.
          - ``any``: The parameter applies, but is unspecified and may be
            determined automatically. For instance, leaving the ``program``
            parameter empty may let any program supporting the method execute the
            calculation.

          Relationships between parameters of the model are defined by downstream
          code.

          :note: Manipulations of members of this class do not change database values.

          :example:
          >>> model = Model(method_family="dft", method="pbe2", basis_set="def2-tzvp")
          >>> model.method_family
          'dft'
          >>> model.spin_mode
          'any'
        
    """
    def __copy__(self) -> Model: ...
    def __deepcopy__(self, arg0: dict) -> Model: ...
    def __eq__(self, arg0: Model) -> bool: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self, method_family: str, method: str, basis_set: str) -> None: ...
    @typing.overload
    def __init__(self, method_family: str, method: str, basis_set: str, spin_mode: str) -> None: ...
    def __ne__(self, arg0: Model) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: 
        """
        Gives a simple string representation of all model fields with each field in one separate line.
        """
    def complete_model(self, settings: scine_utilities.Settings) -> None: 
        """
              Complete ``any`` fields by ``Settings`` values at matching keys

              Completes indeterminate fields by values from a ``Settings`` instance by
              matching their keys. Skips the ``method_family``, ``program``, and
              ``version`` fields.

              :raises RuntimeError: If values in the ``Settings`` instance at matching
                keys differ, or if the ``Settings`` instance is missing a key that is
                not ``none`` in the ``Model``.
            
        """
    def complete_settings(self, settings: scine_utilities.Settings) -> None: 
        """
              Set ``Settings`` fields from non-``any`` fields in the database.

              Overwrites ``Settings`` key values matching fields in this ``Model`` unless
              they are ``any``. Skips the ``method_family``, ``program`` and
              ``version`` fields.

              :param settings: ``Settings`` instance to complete
              :raises RuntimeError: If ``settings`` lacks a non-``none`` field key
            
        """
    @property
    def basis_set(self) -> str:
        """
        Basis set, e.g.: ``def2-svp`` or an empty string for semiempirical methods

        :type: str
        """
    @basis_set.setter
    def basis_set(self, arg0: str) -> None:
        """
        Basis set, e.g.: ``def2-svp`` or an empty string for semiempirical methods
        """
    @property
    def electronic_temperature(self) -> str:
        """
        Temperature of electrons moving around nuclei

        :type: str
        """
    @electronic_temperature.setter
    def electronic_temperature(self, arg1: Union[str, float]) -> None:
        """
        Temperature of electrons moving around nuclei
        """
    @property
    def embedding(self) -> str:
        """
        QM/MM embedding system boundaries, in program-specific format

        :type: str
        """
    @embedding.setter
    def embedding(self, arg0: str) -> None:
        """
        QM/MM embedding system boundaries, in program-specific format
        """
    @property
    def external_field(self) -> str:
        """
        Magnetic field boundary conditions

        :type: str
        """
    @external_field.setter
    def external_field(self, arg0: str) -> None:
        """
        Magnetic field boundary conditions
        """
    @property
    def method(self) -> str:
        """
        Specific method in family of methods, e.g. ``pbe0`` in ``dft`` family

        :type: str
        """
    @method.setter
    def method(self, arg0: str) -> None:
        """
        Specific method in family of methods, e.g. ``pbe0`` in ``dft`` family
        """
    @property
    def method_family(self) -> str:
        """
        Overarching method category for family of methods, e.g. ``cc`` for ``ccsd``, ``ccsd(t)`` etc.

        :type: str
        """
    @method_family.setter
    def method_family(self, arg0: str) -> None:
        """
        Overarching method category for family of methods, e.g. ``cc`` for ``ccsd``, ``ccsd(t)`` etc.
        """
    @property
    def periodic_boundaries(self) -> str:
        """
        Periodic boundary conditions

        :type: str
        """
    @periodic_boundaries.setter
    def periodic_boundaries(self, arg0: str) -> None:
        """
        Periodic boundary conditions
        """
    @property
    def program(self) -> str:
        """
        Software program executing the calculation

        :type: str
        """
    @program.setter
    def program(self, arg0: str) -> None:
        """
        Software program executing the calculation
        """
    @property
    def solvation(self) -> str:
        """
        Implicit solvation model

        :type: str
        """
    @solvation.setter
    def solvation(self, arg0: str) -> None:
        """
        Implicit solvation model
        """
    @property
    def solvent(self) -> str:
        """
        Solvent of solvation model

        :type: str
        """
    @solvent.setter
    def solvent(self, arg0: str) -> None:
        """
        Solvent of solvation model
        """
    @property
    def spin_mode(self) -> str:
        """
        Spin mode of the calculation: ``restricted``/``unrestricted``/``any``

        :type: str
        """
    @spin_mode.setter
    def spin_mode(self, arg0: str) -> None:
        """
        Spin mode of the calculation: ``restricted``/``unrestricted``/``any``
        """
    @property
    def temperature(self) -> str:
        """
        Temperature for thermodynamical property calculations

        :type: str
        """
    @temperature.setter
    def temperature(self, arg1: Union[str, float]) -> None:
        """
        Temperature for thermodynamical property calculations
        """
    @property
    def version(self) -> str:
        """
        Version of the software program executing the calculation

        :type: str
        """
    @version.setter
    def version(self, arg0: str) -> None:
        """
        Version of the software program executing the calculation
        """
    __hash__ = None
    pass
class NumberProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: float) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: float) -> ID: ...
    def get_data(self) -> float: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: float, collection: Collection) -> NumberProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: float, structure_id: ID, calculation_id: ID, collection: Collection) -> NumberProperty: ...
    def set_data(self, data: float) -> None: ...
    @property
    def data(self) -> float:
        """
        :type: float
        """
    @data.setter
    def data(self, arg1: float) -> None:
        pass
    pass
class BoolProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: bool) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: bool) -> ID: ...
    def get_data(self) -> bool: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: bool, collection: Collection) -> BoolProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: bool, structure_id: ID, calculation_id: ID, collection: Collection) -> BoolProperty: ...
    def set_data(self, data: bool) -> None: ...
    @property
    def data(self) -> bool:
        """
        :type: bool
        """
    @data.setter
    def data(self, arg1: bool) -> None:
        pass
    pass
class DenseMatrixProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: numpy.ndarray) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: numpy.ndarray) -> ID: ...
    def get_data(self) -> numpy.ndarray: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: numpy.ndarray, collection: Collection) -> DenseMatrixProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: numpy.ndarray, structure_id: ID, calculation_id: ID, collection: Collection) -> DenseMatrixProperty: ...
    def set_data(self, data: numpy.ndarray) -> None: ...
    @property
    def data(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @data.setter
    def data(self, arg1: numpy.ndarray) -> None:
        pass
    pass
class Reaction(Object):
    """
        Grouping of ElementarySteps that operate on common Compounds

        A reaction is a set of elementary steps, all connecting structures from
        the same compounds in the same way.

        A reaction has the following relationships with other database objects:
        - ``Compound``: A reaction groups elementary steps that operate on the same
          compounds.
        - ``ElementaryStep``: A reaction is a set of elementary steps.

        Data-wise, a reaction consists of two sets of compounds and a set of
        elementary steps. Each structure in the elementary steps should be part of
        the compounds.

        :example:
        >>> lhs_structures = [ID(), ID()]
        >>> rhs_structures = [ID()]
        >>> steps = manager.get_collection("elementary_steps")
        >>> step = ElementaryStep.make(lhs_structures, rhs_structures, steps)
        >>> lhs_compounds = [ID(), ID()]
        >>> rhs_compounds = [ID()]
        >>> reactions = manager.get_collection("reactions")
        >>> reaction = Reaction.make(lhs_compounds, rhs_compounds, reactions)
        >>> reaction.elementary_step_ids = [step.id()]
        >>> reaction.get_reactants(Side.LHS) == (lhs_compounds, [])
        True
        >>> reaction.get_reactants(Side.RHS) == ([], rhs_compounds)
        True
      
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    def add_elementary_step(self, id: ID) -> None: ...
    def add_reactant(self, id: ID, side: Side, type: CompoundOrFlask) -> None: ...
    def clear_elementary_steps(self) -> None: ...
    def clear_reactants(self, side: Side) -> None: ...
    def create(self, lhs: typing.List[ID], rhs: typing.List[ID], lhsTypes: typing.List[CompoundOrFlask] = [], rhsTypes: typing.List[CompoundOrFlask] = []) -> ID: ...
    @typing.overload
    def get_elementary_steps(self) -> typing.List[ID]: 
        """
        Fetch all elementary steps constituting the reaction
        """
    @typing.overload
    def get_elementary_steps(self, manager: Manager, collection: str = 'elementary_steps') -> typing.List[ElementaryStep]: ...
    def get_reactant_type(self, ids: ID) -> CompoundOrFlask: ...
    def get_reactant_types(self, side: Side) -> typing.Tuple[typing.List[CompoundOrFlask], typing.List[CompoundOrFlask]]: ...
    def get_reactants(self, side: Side) -> typing.Tuple[typing.List[ID], typing.List[ID]]: ...
    def has_elementary_step(self, id: ID) -> bool: ...
    def has_elementary_steps(self) -> int: ...
    def has_reactant(self, id: ID) -> Side: ...
    def has_reactants(self) -> typing.Tuple[int, int]: ...
    @staticmethod
    def make(lhs: typing.List[ID], rhs: typing.List[ID], collection: Collection, lhsTypes: typing.List[CompoundOrFlask] = [], rhsTypes: typing.List[CompoundOrFlask] = []) -> Reaction: ...
    def remove_elementary_step(self, id: ID) -> None: ...
    def remove_reactant(self, id: ID, side: Side) -> None: ...
    def set_elementary_steps(self, ids: typing.List[ID]) -> None: ...
    def set_reactants(self, ids: typing.List[ID], side: Side, types: typing.List[CompoundOrFlask] = []) -> None: ...
    @property
    def elementary_step_ids(self) -> typing.Optional[typing.List[ID]]:
        """
        Linked elementary step ids

        :type: typing.Optional[typing.List[ID]]
        """
    @elementary_step_ids.setter
    def elementary_step_ids(self, arg1: typing.Optional[typing.List[ID]]) -> None:
        """
        Linked elementary step ids
        """
    pass
class Results():
    """
          A data class representing database object ids resulting from a calculation

          ..note: This class owns its data and is not conceptually a database
                  pointer similar to the database objects.

          Three types of database objects are modeled to be calculation results:
          properties (``Property``), structures (``Structure``) and elementary steps
          (``ElementaryStep``). This type tracks the IDs of these objects.

          :example:
          >>> results = Results()
          >>> results.property_ids
          []
          >>> results.property_ids = [ID()]  # Note: not a DB operation
          >>> len(results.property_ids)
          1
        
    """
    def __add__(self, arg0: Results) -> Results: ...
    def __iadd__(self, arg0: Results) -> Results: ...
    def __init__(self) -> None: ...
    def add_elementary_step(self, arg0: ID) -> None: ...
    def add_property(self, arg0: ID) -> None: ...
    def add_structure(self, arg0: ID) -> None: ...
    def clear(self) -> None: ...
    def clear_elementary_steps(self) -> None: ...
    def clear_properties(self) -> None: ...
    def clear_structures(self) -> None: ...
    def get_elementary_step(self, arg0: int) -> ID: ...
    def get_elementary_steps(self) -> typing.List[ID]: ...
    def get_properties(self) -> typing.List[ID]: ...
    @typing.overload
    def get_property(self, arg0: int) -> ID: ...
    @typing.overload
    def get_property(self, arg0: str, arg1: Collection) -> ID: ...
    def get_structure(self, arg0: int) -> ID: ...
    def get_structures(self) -> typing.List[ID]: ...
    def remove_elementary_step(self, arg0: ID) -> None: ...
    def remove_property(self, arg0: ID) -> None: ...
    def remove_structure(self, arg0: ID) -> None: ...
    def set_elementary_steps(self, arg0: typing.List[ID]) -> None: ...
    def set_properties(self, arg0: typing.List[ID]) -> None: ...
    def set_structures(self, arg0: typing.List[ID]) -> None: ...
    @property
    def elementary_step_ids(self) -> typing.List[ID]:
        """
        Generated reaction path elementary step object ids

        :type: typing.List[ID]
        """
    @elementary_step_ids.setter
    def elementary_step_ids(self, arg0: typing.List[ID]) -> None:
        """
        Generated reaction path elementary step object ids
        """
    @property
    def property_ids(self) -> typing.List[ID]:
        """
        Generated property object ids

        :type: typing.List[ID]
        """
    @property_ids.setter
    def property_ids(self, arg0: typing.List[ID]) -> None:
        """
        Generated property object ids
        """
    @property
    def structure_ids(self) -> typing.List[ID]:
        """
        Generated structure object ids

        :type: typing.List[ID]
        """
    @structure_ids.setter
    def structure_ids(self, arg0: typing.List[ID]) -> None:
        """
        Generated structure object ids
        """
    pass
class Side():
    """
    Members:

      NONE

      LHS

      RHS

      BOTH
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BOTH: scine_database.Side # value = <Side.BOTH: 3>
    LHS: scine_database.Side # value = <Side.LHS: 1>
    NONE: scine_database.Side # value = <Side.NONE: 0>
    RHS: scine_database.Side # value = <Side.RHS: 2>
    __members__: dict # value = {'NONE': <Side.NONE: 0>, 'LHS': <Side.LHS: 1>, 'RHS': <Side.RHS: 2>, 'BOTH': <Side.BOTH: 3>}
    pass
class SparseMatrixProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: scipy.sparse.csc_matrix[numpy.float64]) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: scipy.sparse.csc_matrix[numpy.float64]) -> ID: ...
    def get_data(self) -> scipy.sparse.csc_matrix[numpy.float64]: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: scipy.sparse.csc_matrix[numpy.float64], collection: Collection) -> SparseMatrixProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: scipy.sparse.csc_matrix[numpy.float64], structure_id: ID, calculation_id: ID, collection: Collection) -> SparseMatrixProperty: ...
    def set_data(self, data: scipy.sparse.csc_matrix[numpy.float64]) -> None: ...
    @property
    def data(self) -> scipy.sparse.csc_matrix[numpy.float64]:
        """
        :type: scipy.sparse.csc_matrix[numpy.float64]
        """
    @data.setter
    def data(self, arg1: scipy.sparse.csc_matrix[numpy.float64]) -> None:
        pass
    pass
class Status():
    """
    Members:

      CONSTRUCTION : Calculation database representation is work in progress, is not ready to be run

      NEW : Calculation is scheduled to run

      PENDING : Calculation is running, awaiting results

      COMPLETE : Calculation is complete

      ANALYZED : The calculation has been post-processed

      HOLD : The calculation is being held ready for scheduling

      FAILED : The calculation failed to complete successfully
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ANALYZED: scine_database.Status # value = <Status.ANALYZED: 4>
    COMPLETE: scine_database.Status # value = <Status.COMPLETE: 3>
    CONSTRUCTION: scine_database.Status # value = <Status.CONSTRUCTION: 0>
    FAILED: scine_database.Status # value = <Status.FAILED: 99>
    HOLD: scine_database.Status # value = <Status.HOLD: 10>
    NEW: scine_database.Status # value = <Status.NEW: 1>
    PENDING: scine_database.Status # value = <Status.PENDING: 2>
    __members__: dict # value = {'CONSTRUCTION': <Status.CONSTRUCTION: 0>, 'NEW': <Status.NEW: 1>, 'PENDING': <Status.PENDING: 2>, 'COMPLETE': <Status.COMPLETE: 3>, 'ANALYZED': <Status.ANALYZED: 4>, 'HOLD': <Status.HOLD: 10>, 'FAILED': <Status.FAILED: 99>}
    pass
class StringProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: str) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: str) -> ID: ...
    def get_data(self) -> str: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: str, collection: Collection) -> StringProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: str, structure_id: ID, calculation_id: ID, collection: Collection) -> StringProperty: ...
    def set_data(self, data: str) -> None: ...
    @property
    def data(self) -> str:
        """
        :type: str
        """
    @data.setter
    def data(self, arg1: str) -> None:
        pass
    pass
class Structure(Object):
    """
        Class referencing a molecular three-dimensional structure database object

        A Structure has the following relationships with other database objects:
        - ``Aggregate``: An aggregate is a collection of one or more ``Structure``
          instances. Typically, structures are grouped by the criterion that they
          represent the same molecule or complex. They are grouped into
          ``Compounds`` (single molecules) or ``Flasks`` (complexes).
        - ``Calculation``: A calculation will usually require one or more
          ``Structure`` instances as input.
        - ``Property``: These classes are results of a ``Calculation`` that each
          represent a derived quantity describing a ``Structure``.

        A structure's data consists mainly of its three-dimensional structure, its
        charge, the spin multiplicity, and a label.

        :example:
        >>> collection = manager.get_collection("structures")
        >>> structure = Structure.make(atoms, charge=0, multiplicity=1, collection=collection)
        >>> structure.charge  # Note: Properties are database fetches, not cached data
        0
        >>> structure.multiplicity = 3
        >>> structure.label = Label.MINIMUM_GUESS

        What molecule a structure describes can be encoded by means of the
        graph-related methods. Graphs are stored as a free-form string-string map.
        The graph properties can be populated e.g. by SMILES or serializations of
        other molecular representations.

        :example:
        >>> collection = manager.get_collection("structures")
        >>> structure = Structure.make(atoms, charge=0, multiplicity=1, collection=collection)
        >>> structure.get_graphs()
        {}
        >>> structure.set_graph("smiles", "CO")
        >>> structure.get_graphs()
        {'smiles': 'CO'}

        A structure may be linked to a ``Compound``, which collects multiple
        structures, usually by the criterion that they are deemed to be describing
        the same molecule, though this is principally free-form.

        :example:
        >>> structures = manager.get_collection("structures")
        >>> compounds = manager.get_collection("compounds")
        >>> structure = Structure.make(atoms, charge=0, multiplicity=1, collection=structures)
        >>> structure.aggregate_id is None
        True
        >>> compound = Compound.make([structure.id()], compounds)
        >>> structure.aggregate_id is None
        True
        >>> structure.aggregate_id = compound.id()  # Only now are they fully connected
        >>> structure.aggregate_id is None
        False

        ``Properties`` derived from a structure are referenced directly in the
        database representation, and can be manipulated.

        :example:
        >>> structures = manager.get_collection("structures")
        >>> properties = manager.get_collection("properties")
        >>> structure = Structure.make(atoms, charge=0, multiplicity=1, collection=structures)
        >>> bigness = NumberProperty.make("bigness", structure.model, 2.5, properties)
        >>> structure.add_property("bigness", bigness.id())
        >>> structure.get_property("bigness") == bigness.id()
        True
      
    """
    @typing.overload
    def __init__(self) -> None: 
        """
            Empty-initialization

            Nearly all member functions called for an instance in this state will raise
            exceptions since no ID is present nor a collection linked. The only way to
            use this instance is by linking a collection and then creating a new
            structure in the database with the ``create`` family of instance methods.
            This pattern is disadvised though: Prefer using the ``make`` family of
            static methods to directly generate new database objects and receive object
            instances fully populated with ID and linked collection.

            :example:
            >>> s = Structure()  # no ID, no linked collection
            >>> s.comment
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            RuntimeError: Missing linked collection.
            >>> collection = manager.get_collection("structures")
            >>> s.link(collection)
            >>> s.comment  # s still doesn't refer to a database object
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            RuntimeError: The Object is missing an ID to be used in this context.
            >>> id = s.create(atoms, 0, 1)  # Generate a database instance
            >>> id == s.id()
            True
            >>> t = Structure.make(atoms, 0, 1, collection)  # Direct via static method
            >>> t.has_id() and t.has_link()
            True
            >>> t.id() == s.id()
            False
          


              Partial-initialization to existing database object

              A member function initialized by id, but without a collection refers
              to an existing database object, but does not fully specify which one,
              since ID uniqueness constraints are collection-level in the database.
              Nearly all member functions will raise for an instance in this state.
              The instance must be linked to a collection before it can be used.

              :example:
              >>> collection = manager.get_collection("structures")
              >>> obj = Structure.make(atoms, 0, 1, collection)  # Generate a db object
              >>> s = Structure(obj.id())  # Instance referring existing id
              >>> s.charge
              Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
              RuntimeError: Missing linked collection.
              >>> s.link(collection)
              >>> s.charge
              0
            


              Full initialization to existing database object

              :example:
              >>> collection = manager.get_collection("structures")
              >>> s = Structure.make(atoms, 0, 1, collection)  # Generate a db object
              >>> t = Structure(s.id(), collection)  # Full initialization
              >>> s.id() == t.id()  # Both instances refer to the same database object
              True
            
        """
    @typing.overload
    def __init__(self, id: ID) -> None: ...
    @typing.overload
    def __init__(self, id: ID, collection: Collection) -> None: ...
    def add_calculation(self, key: str, id: ID) -> None: ...
    def add_calculations(self, key: str, ids: typing.List[ID]) -> None: ...
    def add_property(self, key: str, id: ID) -> None: ...
    def clear_aggregate(self) -> None: ...
    def clear_all_calculations(self) -> None: ...
    def clear_all_properties(self) -> None: ...
    def clear_atoms(self) -> None: ...
    def clear_calculations(self, key: str) -> None: ...
    def clear_comment(self) -> None: ...
    def clear_compound(self) -> None: ...
    def clear_duplicate_id(self) -> None: ...
    def clear_graphs(self) -> None: ...
    def clear_original(self) -> None: ...
    def clear_properties(self, key: str) -> None: ...
    @typing.overload
    def create(self, atoms: scine_utilities.AtomCollection, charge: int, multiplicity: int) -> ID: ...
    @typing.overload
    def create(self, atoms: scine_utilities.AtomCollection, charge: int, multiplicity: int, model: Model, label: Label) -> ID: ...
    @typing.overload
    def create(self, xyz_file: str, charge: int, multiplicity: int) -> ID: ...
    @typing.overload
    def create(self, xyz_file: str, charge: int, multiplicity: int, model: Model, label: Label) -> ID: ...
    def get_aggregate(self, recursive: bool = True) -> ID: ...
    def get_all_calculations(self) -> typing.Dict[str, typing.List[ID]]: ...
    def get_all_properties(self) -> typing.Dict[str, typing.List[ID]]: ...
    def get_atoms(self) -> scine_utilities.AtomCollection: ...
    def get_calculation(self, key: str) -> ID: ...
    def get_calculations(self, key: str) -> typing.List[ID]: ...
    def get_charge(self) -> int: ...
    def get_comment(self) -> str: ...
    def get_compound(self) -> ID: ...
    def get_graph(self, key: str) -> str: ...
    def get_graphs(self) -> typing.Dict[str, str]: ...
    def get_label(self) -> Label: ...
    def get_model(self) -> Model: ...
    def get_multiplicity(self) -> int: ...
    def get_original(self) -> ID: ...
    def get_properties(self, key: str) -> typing.List[ID]: ...
    def get_property(self, key: str) -> ID: ...
    def has_aggregate(self, recursive: bool = True) -> bool: ...
    def has_atoms(self) -> int: ...
    @typing.overload
    def has_calculation(self, id: ID) -> bool: ...
    @typing.overload
    def has_calculation(self, key: str) -> bool: ...
    def has_calculations(self, key: str) -> int: ...
    def has_comment(self) -> bool: ...
    def has_compound(self) -> bool: ...
    def has_graph(self, key: str) -> bool: ...
    def has_graphs(self) -> int: ...
    def has_original(self) -> bool: ...
    def has_properties(self, key: str) -> int: ...
    @typing.overload
    def has_property(self, id: ID) -> bool: ...
    @typing.overload
    def has_property(self, key: str) -> bool: ...
    def is_duplicate_of(self) -> ID: ...
    @staticmethod
    @typing.overload
    def make(atoms: scine_utilities.AtomCollection, charge: int, multiplicity: int, collection: Collection) -> Structure: ...
    @staticmethod
    @typing.overload
    def make(atoms: scine_utilities.AtomCollection, charge: int, multiplicity: int, model: Model, label: Label, collection: Collection) -> Structure: ...
    @staticmethod
    @typing.overload
    def make(xyz_file: str, charge: int, multiplicity: int, collection: Collection) -> Structure: ...
    @staticmethod
    @typing.overload
    def make(xyz_file: str, charge: int, multiplicity: int, model: Model, label: Label, collection: Collection) -> Structure: ...
    def query_calculations(self, key: str, model: Model, collection: Collection) -> typing.List[ID]: ...
    def query_properties(self, key: str, model: Model, collection: Collection) -> typing.List[ID]: ...
    def remove_calculation(self, key: str, id: ID) -> None: ...
    def remove_graph(self, key: str) -> None: ...
    def remove_property(self, key: str, id: ID) -> None: ...
    def set_aggregate(self, aggregate: ID) -> None: ...
    def set_all_calculations(self, calculations: typing.Dict[str, typing.List[ID]]) -> None: ...
    def set_all_properties(self, properties: typing.Dict[str, typing.List[ID]]) -> None: ...
    def set_as_duplicate_of(self, id: ID) -> None: ...
    @typing.overload
    def set_atoms(self, atoms: scine_utilities.AtomCollection) -> None: 
        """
        Populate the atoms from an .xyz file
        """
    @typing.overload
    def set_atoms(self, xyz_file: str) -> None: ...
    def set_calculation(self, key: str, id: ID) -> None: ...
    def set_calculations(self, key: str, ids: typing.List[ID]) -> None: ...
    def set_charge(self, charge: int) -> None: ...
    def set_comment(self, comment: str) -> None: ...
    def set_compound(self, compound: ID) -> None: ...
    def set_graph(self, key: str, graph: str) -> None: ...
    def set_graphs(self, arg0: typing.Dict[str, str]) -> None: ...
    def set_label(self, label: Label) -> None: ...
    def set_model(self, model: Model) -> None: ...
    def set_multiplicity(self, multiplicity: int) -> None: ...
    def set_original(self, id: ID) -> None: ...
    def set_properties(self, key: str, ids: typing.List[ID]) -> None: ...
    def set_property(self, key: str, id: ID) -> None: ...
    @property
    def aggregate_id(self) -> typing.Optional[ID]:
        """
        Linked aggregate id

        :type: typing.Optional[ID]
        """
    @aggregate_id.setter
    def aggregate_id(self, arg1: typing.Optional[ID]) -> None:
        """
        Linked aggregate id
        """
    @property
    def charge(self) -> int:
        """
        Overall molecular charge

        :type: int
        """
    @charge.setter
    def charge(self, arg1: int) -> None:
        """
        Overall molecular charge
        """
    @property
    def comment(self) -> typing.Optional[str]:
        """
        Free-form comment on the structure

        :type: typing.Optional[str]
        """
    @comment.setter
    def comment(self, arg1: typing.Optional[str]) -> None:
        """
        Free-form comment on the structure
        """
    @property
    def compound_id(self) -> typing.Optional[ID]:
        """
        Linked compound id

        :type: typing.Optional[ID]
        """
    @compound_id.setter
    def compound_id(self, arg1: typing.Optional[ID]) -> None:
        """
        Linked compound id
        """
    @property
    def label(self) -> Label:
        """
        Label describing how the structure was generated

        :type: Label
        """
    @label.setter
    def label(self, arg1: Label) -> None:
        """
        Label describing how the structure was generated
        """
    @property
    def model(self) -> Model:
        """
        Model used to generate this structure

        :type: Model
        """
    @model.setter
    def model(self, arg1: Model) -> None:
        """
        Model used to generate this structure
        """
    @property
    def multiplicity(self) -> int:
        """
        Spin multiplicity

        :type: int
        """
    @multiplicity.setter
    def multiplicity(self, arg1: int) -> None:
        """
        Spin multiplicity
        """
    pass
class VectorProperty(Property, Object):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID) -> None: ...
    @typing.overload
    def __init__(self, arg0: ID, arg1: Collection) -> None: ...
    @typing.overload
    def create(self, model: Model, property_name: str, data: numpy.ndarray) -> ID: ...
    @typing.overload
    def create(self, model: Model, property_name: str, structure: ID, calculation: ID, data: numpy.ndarray) -> ID: ...
    def get_data(self) -> numpy.ndarray: ...
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: numpy.ndarray, collection: Collection) -> VectorProperty: 
        """
              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param collection: The collection to write the property into
            


              Create a new property in a collection

              :param name: The name of the property
              :param model: The model used to calculate the property
              :param data: The property data itself
              :param structure_id: The structure to which the property is related to
              :param calculation_id: The calculation the property was calculated in
              :param collection: The collection to write the property into
            
        """
    @staticmethod
    @typing.overload
    def make(name: str, model: Model, data: numpy.ndarray, structure_id: ID, calculation_id: ID, collection: Collection) -> VectorProperty: ...
    def set_data(self, data: numpy.ndarray) -> None: ...
    @property
    def data(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @data.setter
    def data(self, arg1: numpy.ndarray) -> None:
        pass
    pass
class database_version():
    @staticmethod
    def __repr__() -> str: ...
    major = 1
    minor = 1
    patch = 0
    pass
def levenshtein_distance(a: str, b: str, insert_cost: int = 1, delete_cost: int = 1, replace_cost: int = 1) -> int:
    pass
