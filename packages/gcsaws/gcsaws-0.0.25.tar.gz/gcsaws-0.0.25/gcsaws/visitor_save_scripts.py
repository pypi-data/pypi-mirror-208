from dataclasses import dataclass
from pathlib import Path
import shlex

from gcscore.mod import Visitor, HasChildren
from gcscore import CommandRenderer
import jinja2
from .nodes import *

__all__ = ['VisitorStateSaveScripts', 'setup_visitor_save_script']

@dataclass
class VisitorStateSaveScripts:
    output_directory: Path
    command_renderer: CommandRenderer
    j2env: jinja2.Environment


def setup_visitor_save_script(visitor: Visitor):
    for meth in ['visit_wait', 'visit_pause', 'visit_script', 'visit_step_function', 'visit_change_instance_state']:
        visitor.register(meth, _visit_other)

    visitor.register('visit_script_template', _visit_script_template)
    visitor.register('visit_run_in_order', _visit_composed_node)
    visitor.register('visit_run_in_parallel', _visit_composed_node)


def _visit_composed_node(visitor: Visitor, node: HasChildren, state: VisitorStateSaveScripts):
    for child in node.gcscore_children:
        visitor.visit(child, state)


def _visit_other(*_):
    pass


def _visit_script_template(_: Visitor, node: NodeScriptTemplate, state: VisitorStateSaveScripts):
    script = state.command_renderer.render_command(node.gcsaws_command, state.j2env)
    path = state.output_directory / node.gcscore_name / shlex.split(node.gcsaws_command_source, comments=True, posix=True)[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding='utf8')
