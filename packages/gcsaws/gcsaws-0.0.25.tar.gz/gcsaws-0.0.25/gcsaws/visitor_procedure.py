from dataclasses import dataclass, field
from functools import partial
from typing import Union

import jinja2

from gcscore import CommandRenderer
from gcscore.mod import Visitor, compact_script
from gcsaws.nodes import *

__all__ = ['VisitorStateProcedure', 'setup_procedure_visitor']


@dataclass
class VisitorStateProcedure:
    command_renderer: CommandRenderer
    j2env: jinja2.Environment
    root: list = field(default_factory=list)
    current: list = field(init=False)

    def __post_init__(self):
        self.current = self.root


def setup_procedure_visitor(visitor: Visitor):
    visitor.register('visit_wait', _visit_wait)
    visitor.register('visit_pause', _visit_pause)
    visitor.register('visit_script', _visit_script)
    visitor.register('visit_script_template', _visit_script_template)
    visitor.register('visit_step_function', _visit_step_function)
    visitor.register('visit_change_instance_state', _visit_change_instance_state)
    visitor.register('visit_run_in_order', partial(_visit_composed_node, node_type='ordered'))
    visitor.register('visit_run_in_parallel', partial(_visit_composed_node, node_type='async'))


ComposedNode = Union[NodeRunInOrder, NodeRunInParallel]


def _visit_composed_node(visitor: Visitor, node: ComposedNode, state: VisitorStateProcedure, node_type: str):
    result = {
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': node_type,
        'nodes': []
    }
    old_current = state.current
    state.current = result['nodes']
    [visitor.visit(child, state) for child in node.gcscore_children]
    state.current = old_current

    if len(result['nodes']) > 0:
        state.current.append(result)


def _visit_wait(_visitor: Visitor, node: NodeWait, state: VisitorStateProcedure):
    state.current.append({
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': 'wait',
        'duration': node.gcsaws_duration
    })


def _visit_pause(_visitor: Visitor, node: NodePause, state: VisitorStateProcedure):
    state.current.append({
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': 'pause',
        'identifier': node.gcsaws_identifier
    })


def _script_like(_visitor: Visitor, node: Union[NodeScript, NodeScriptTemplate], state: VisitorStateProcedure,
                 script: str):
    if node.gcsaws_compaction:
        script = compact_script(node.gcsaws_script_type, script)

    state.current.append({
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': node.gcsaws_script_type,
        'language': node.gcsaws_script_type,
        'commands': script.splitlines(),
        'targets': node.gcsaws_targets
    })


def _visit_script(visitor: Visitor, node: NodeScript, state: VisitorStateProcedure):
    if len(node.gcsaws_targets) == 0:
        return

    _script_like(visitor, node, state, node.gcsaws_command)


def _visit_script_template(visitor: Visitor, node: NodeScriptTemplate, state: VisitorStateProcedure):
    if len(node.gcsaws_targets) == 0:
        return

    script = state.command_renderer.render_command(node.gcsaws_command, state.j2env)
    _script_like(visitor, node, state, script)


def _visit_step_function(_visitor: Visitor, node: NodeStepFunction, state: VisitorStateProcedure):
    state.current.append({
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': 'stepfunction',
        'stepfunction': node.gcsaws_function_name,
        'payload': node.gcsaws_payload,
    })


def _visit_change_instance_state(_visitor: Visitor, node: NodeChangeInstanceState, state: VisitorStateProcedure):
    if len(node.gcsaws_targets) == 0:
        return

    state.current.append({
        'name': node.gcscore_name,
        'description': node.gcscore_description,
        'type': 'change-instance-state',
        'wanted_state': node.gcsaws_instance_state,
        'targets': node.gcsaws_targets,
    })
