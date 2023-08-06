import re
import shlex
from typing import Union

import jinja2
from gcscore.mod import Visitor
from gcscore.mod.validation import VisitorStateValidation, validation_error_value, validate_string, validation_error

from gcsaws.nodes import *

__all__ = ['setup_validation_visitor', 'VisitorStateValidation']


def setup_validation_visitor(visitor: Visitor):
    visitor.register('visit_wait', _visit_wait)
    visitor.register('visit_pause', _visit_pause)
    visitor.register('visit_script', _visit_script)
    visitor.register('visit_script_template', _visit_script)
    visitor.register('visit_step_function', _visit_step_function)
    visitor.register('visit_change_instance_state', _visit_change_instance_state)
    visitor.register('visit_run_in_order', _visit_composed_node)
    visitor.register('visit_run_in_parallel', _visit_composed_node)


PATTERN_NAME = re.compile(r'^[a-zA-Z0-9_\-]+$')


def _validate_targets(state: VisitorStateValidation, node: HasTargets):
    if not node.gcsaws_targets_initialized:
        validation_error_value(state, 'targets', None, 'on_targets(...) must be called')
    if len(node.gcsaws_targets) == 0:
        print(f'{state.formatted_traceback()} will be ignore due to missing target(s).')


def _validate_template(state: VisitorStateValidation, node: HasCommand):
    try:
        command = shlex.split(node.gcsaws_command, comments=True, posix=True)
    except Exception as ex:  # NOQA
        validation_error_value(state, 'command', node.gcsaws_command, 'Must be a valid posix command.')
        return

    if len(command) == 0:
        validation_error_value(state, 'command', node.gcsaws_command, 'The parsed must not be empty.')
        return

    if 'j2env' not in state.others:
        validation_error(state, 'No jinja2.Environment set in state.others["j2env"]. Cannot check the template.')
        return

    template_name = command[0]
    try:
        state.others['j2env'].get_template(template_name)
    except jinja2.TemplateNotFound:
        validation_error_value(state, 'template_name', node.gcsaws_command, 'Template not found.')
    except Exception as ex:  # NOQA
        validation_error_value(state, 'template', node.gcsaws_command, 'Error with the template.')


ComposedNode = Union[NodeRunInOrder, NodeRunInParallel]


def _visit_composed_node(visitor: Visitor, node: ComposedNode, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)
    for child in node.gcscore_children:
        visitor.visit(child, state)


def _visit_wait(_visitor: Visitor, node: NodeWait, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)
    if node.gcsaws_duration <= 0:
        validation_error_value(state, 'duration', node.gcsaws_duration, 'Must be greater than 0')


def _visit_pause(_visitor: Visitor, node: NodePause, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)


def _visit_script(_visitor: Visitor, node: NodeScript, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)
    _validate_targets(state, node)
    if node.gcsaws_script_type is None:
        validation_error_value(state, 'script_type', None, 'shell() or powershell() must be called')
        return
    if node.gcsaws_command is None:
        validation_error_value(state, 'command', None, 'command("your command") must be called')
        return
    _validate_template(state, node)


def _visit_step_function(_visitor: Visitor, node: NodeStepFunction, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)
    if node.gcsaws_function_name is None:
        validation_error_value(state, 'stepfuntion', None, 'stepfunction("sf-name") must be called')
    if node.gcsaws_payload is None:
        validation_error_value(state, 'payload', None, 'payload({"key": "value") must be called')


def _visit_change_instance_state(_visitor: Visitor, node: NodeChangeInstanceState, state: VisitorStateValidation):
    state = state.concat(node.gcscore_name)
    validate_string(state, 'name', node.gcscore_name, PATTERN_NAME)
    _validate_targets(state, node)
    if node.gcsaws_instance_state is None:
        validation_error_value(state, 'instance_state', node.gcsaws_instance_state,
                               'power_on() or power_off() must be called')
