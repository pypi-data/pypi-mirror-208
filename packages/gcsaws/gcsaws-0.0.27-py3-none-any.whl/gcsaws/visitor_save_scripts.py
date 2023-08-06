from dataclasses import dataclass, field
from pathlib import Path
import shlex

from gcscore.mod import Visitor, HasChildren
from gcscore import CommandRenderer
import jinja2
from .nodes import *

__all__ = ['VisitorStateSaveScripts', 'Visitor', 'setup_visitor_save_script', 'visit_other', 'visit_script_template',
           'visit_composed_node']


@dataclass
class VisitorStateSaveScripts:
    command_renderer: CommandRenderer
    j2env: jinja2.Environment
    output: dict[Path, str] = field(default_factory=dict)


def setup_visitor_save_script(visitor: Visitor):
    for meth in ['visit_wait', 'visit_pause', 'visit_script', 'visit_step_function', 'visit_change_instance_state']:
        visitor.register(meth, visit_other)

    visitor.register('visit_script_template', visit_script_template)
    visitor.register('visit_run_in_order', visit_composed_node)
    visitor.register('visit_run_in_parallel', visit_composed_node)


def visit_other(*_):
    pass


def visit_composed_node(visitor: Visitor, node: HasChildren, state: VisitorStateSaveScripts):
    for child in node.gcscore_children:
        visitor.visit(child, state)


def visit_script_template(_: Visitor, node: NodeScriptTemplate, state: VisitorStateSaveScripts):
    script = state.command_renderer.render_command(node.gcsaws_command, state.j2env)
    path = Path(node.gcscore_name) / shlex.split(node.gcsaws_command_source, comments=True, posix=True)[0]
    state.output[path] = script
