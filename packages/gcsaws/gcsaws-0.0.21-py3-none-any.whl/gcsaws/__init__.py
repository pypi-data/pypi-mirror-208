from .nodes import *
from .helpers import * # NOQA

Procedure = NodeRunInOrder


def new_procedure(name: str) -> Procedure:
    return Procedure(name=name)
