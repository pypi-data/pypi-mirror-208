"""Meta-information on the mongodb layout of the database"""
import scine_database.layout
import typing
from typing import Union
import scine_database

__all__ = [
    "calculation_status",
    "default_collection",
    "elementary_step_type",
    "structure_label"
]


def calculation_status(status: scine_database.Status) -> str:
    """
          Returns the database layout of a calculation status

          >>> import scine_database as db
          >>> calculation_status(db.Status.NEW)
          "new"
        
    """
def default_collection(db_type: object) -> str:
    """
          Returns the default database collection name for a database object

          >>> import scine_database as db
          >>> default_collection(db.Structure)
          "structures"
          >>> default_collection(db.NumberProperty)
          "properties"
          >>> default_collection(db.Manager)
          Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
          RuntimeError: The type 'Manager' does not have a default collection
        
    """
def elementary_step_type(type: scine_database.ElementaryStepType) -> str:
    """
          Returns the database layout of a elementary step type

          >>> import scine_database as db
          >>> elementary_step_type(db.ElementaryStepType.REGULAR)
          "regular"
        
    """
def structure_label(label: scine_database.Label) -> str:
    """
          Returns the database layout of a structure label

          >>> import scine_database as db
          >>> structure_label(db.Label.MINIMUM_OPTIMIZED)
          "minimum_optimized"
        
    """
