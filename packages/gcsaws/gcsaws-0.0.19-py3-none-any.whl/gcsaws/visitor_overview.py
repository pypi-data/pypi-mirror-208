from os import PathLike
from pathlib import Path
from typing import Union, Optional

from gcscore.mod import Visitor, HasName, HasDescription
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.tree import Tree

from gcsaws import *

STYLE_RUN_IN_ORDER = Style(bold=True, color='black')
STYLE_RUN_IN_PARALLEL = Style(bold=True, color='bright_magenta')
STYLE_BOLD = Style(bold=True)
STYLE_HIGHLIGHT_1 = Style(bold=True, color='purple')


def _assemble_lines(*lines: Text, empty_line_ending=False) -> Text:
    result = Text()
    for line in lines:
        if line is None:
            continue
        result += line
        result.append('\n')
    if empty_line_ending:
        result.append('\n ')
    return result


def _make_description(node: HasDescription) -> Optional[Text]:
    if len(node.gcscore_description) == 0:
        return None
    return Text(node.gcscore_description)


def _make_name(node: HasName, icon: Union[str, Text] = None) -> Text:
    result = Text()
    if isinstance(icon, Text):
        result += icon
    else:
        result += Text(f'{icon} ') if icon is not None else Text('')
    result.append(f'[{node.gcscore_name}] ', STYLE_BOLD)
    return result


def _make_targets(node: HasTargets, prefix=' ') -> Text:
    target_pretty_list = ', '.join(map(lambda t: t['name'], node.gcsaws_targets))

    result = Text(prefix)
    result.append(target_pretty_list, STYLE_HIGHLIGHT_1)
    return result


class VisitorStateOverview:
    def __init__(self,
                 main_name: str,
                 width: int = 200):
        self.current_tree = self.root = Tree(f'📑 {main_name}', guide_style='bold')
        self.width = width

    def _capture(self) -> Console:
        root = self.root.children[0]
        console = Console(record=True, width=self.width)
        console.begin_capture()
        console.print(root)
        console.end_capture()
        return console

    def export_html(self) -> str:
        return self._capture().export_html()


def setup_visitor_overview(visitor: Visitor):
    visitor.register('visit_wait', _visit_wait)
    visitor.register('visit_pause', _visit_pause)
    visitor.register('visit_script', _visit_script)
    visitor.register('visit_script_template', _visit_script_template)
    visitor.register('visit_step_function', _visit_step_function)
    visitor.register('visit_change_instance_state', _visit_change_instance_state)
    visitor.register('visit_run_in_order', _visit_run_in_order)
    visitor.register('visit_run_in_parallel', _visit_run_in_parallel)


ComposedNode = Union[NodeRunInOrder, NodeRunInParallel]


def _visit_composed_node(visitor: Visitor,
                         node: ComposedNode,
                         state: VisitorStateOverview,
                         icon: Union[str, Text],
                         title_ext: Text,
                         guide_style: Style):
    title = _make_name(node, icon)
    title += title_ext

    old_current = state.current_tree
    current = state.current_tree.add(_assemble_lines(title, _make_description(node)), guide_style=guide_style)
    for child in node.gcscore_children:
        state.current_tree = current
        visitor.visit(child, state)
    state.current_tree = old_current


def _visit_run_in_order(visitor: Visitor, node: NodeRunInParallel, state: VisitorStateOverview):
    title_ext = Text('run in ')
    title_ext.append('order', STYLE_HIGHLIGHT_1)

    _visit_composed_node(visitor, node, state, '🪜', title_ext, STYLE_RUN_IN_ORDER)


def _visit_run_in_parallel(visitor: Visitor, node: NodeRunInParallel, state: VisitorStateOverview):
    title_ext = Text('run in ')
    title_ext.append('parallel', STYLE_HIGHLIGHT_1)

    _visit_composed_node(visitor, node, state, Text('// ', STYLE_BOLD), title_ext, STYLE_RUN_IN_PARALLEL)


def _visit_wait(_visitor: Visitor, node: NodeWait, state: VisitorStateOverview):
    title = _make_name(node, '⏳')
    title.append('wait ')
    title.append(str(node.gcsaws_duration), STYLE_HIGHLIGHT_1)
    title.append(' seconds')
    state.current_tree.add(_assemble_lines(title, _make_description(node)))


def _visit_pause(_visitor: Visitor, node: NodePause, state: VisitorStateOverview):
    title = _make_name(node, icon='⏸')
    title.append('pause')
    title.append(f'\n> {node.gcsaws_identifier}', 'blue')
    state.current_tree.add(_assemble_lines(title, _make_description(node)))


def _visit_script(visitor: Visitor, node: NodeScript, state: VisitorStateOverview):
    title = _make_name(node)
    title.append('run command on')
    title += _make_targets(node)
    title.append(f'\n$> {node.gcsaws_command_source}', 'blue')
    state.current_tree.add(_assemble_lines(title, _make_description(node)))


def _visit_script_template(visitor: Visitor, node: NodeScriptTemplate, state: VisitorStateOverview):
    title = _make_name(node, Text('</> ', STYLE_BOLD))
    title.append('generate and run the script on')
    title += _make_targets(node)
    title.append(f'\n> {node.gcsaws_command_source}', 'blue')

    state.current_tree.add(_assemble_lines(title, _make_description(node)))


def _visit_step_function(visitor: Visitor, node: NodeStepFunction, state: VisitorStateOverview):
    title = _make_name(node, '📜')
    title.append('call the step function ')
    title.append(node.gcsaws_function_name, STYLE_HIGHLIGHT_1)
    state.current_tree.add(_assemble_lines(title, _make_description(node)))


def _visit_change_instance_state(visitor: Visitor, node: NodeChangeInstanceState, state: VisitorStateOverview):
    if node.gcsaws_instance_state == 'running':
        icon = '🟢'
        action = 'on'
    else:
        icon = '🔴'
        action = 'off'
    title = _make_name(node, icon)
    title.append(f'power {action}')
    title += _make_targets(node)
    state.current_tree.add(_assemble_lines(title, _make_description(node)))
