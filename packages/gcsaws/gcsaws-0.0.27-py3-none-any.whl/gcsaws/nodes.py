from __future__ import annotations

import random
from typing import TypeVar, Optional

from gcscore.mod import *

T = TypeVar('T')

__all__ = ['HasIdentifier', 'HasCompaction', 'HasCommand', 'HasTargets', 'HasPayload', 'HasScriptType',
           'HasInstanceState', 'HasFunctionName', 'HasInstanceState', 'HasDurationSeconds', 'AcceptChildScript',
           'AcceptChildPause', 'AcceptChildWait', 'AcceptChildScriptTemplate', 'AcceptChildStepFunction',
           'AcceptChildRunInOrder', 'AcceptChildRunInParallel', 'NodeRunInOrder', 'NodeRunInParallel', 'NodeWait',
           'NodePause', 'NodeScript', 'NodeScriptTemplate', 'NodeStepFunction', 'NodeChangeInstanceState']


# <editor-fold desc="Trait attributes">

class HasDurationSeconds:
    gcsaws_duration: int = 5

    def duration(self: T, duration: int) -> T:
        """
        Sets the duration in seconds for the node.
        :param duration: the duration in seconds
        :return: self
        """
        self.gcsaws_duration = duration
        return self


class HasIdentifier:
    gcsaws_identifier: str = ''

    def identifier(self: T, identifier_: str) -> T:
        """
        Sets the identifier in order to make it clearly identified in the resume tool.
        :param identifier_: the identifier
        :return: self
        """
        self.gcsaws_identifier = identifier_
        return self


class HasScriptType:
    gcsaws_script_type: str = None

    def shell(self: T) -> T:
        """
        Makes the node run a shell script/command.
        :return: self
        """
        self.gcsaws_script_type = 'shell'
        return self

    def powershell(self: T) -> T:
        """
        Make the node run a powershell script/command.
        :return: self
        """
        self.gcsaws_script_type = 'powershell'
        return self


class HasCommand:
    gcsaws_command: Optional[str] = None
    gcsaws_command_source: Optional[str] = None

    def command(self: T, cmd: str) -> T:
        """
        Sets the node command or script.
        :param cmd:
        :return:
        """
        self.gcsaws_command = cmd
        self.gcsaws_command_source = cmd
        return self


class HasTargets:
    gcsaws_targets: list[dict]
    gcsaws_targets_initialized: bool

    def __gcs__init__(self, **_):
        self.gcsaws_targets = []
        self.gcsaws_targets_initialized = False

    def on_targets(self: T, targets: list[dict]) -> T:
        """
        Adds the targets to the node.
        :param targets: list of the targets
        :return: self
        """
        self.gcsaws_targets.extend(targets)
        self.gcsaws_targets_initialized = True
        return self


class HasCompaction:
    gcsaws_compaction: bool = False

    def compact(self: T, do_compact: bool = True) -> T:
        """
        Indicate that the content of the node (scripts...) should be compacted.
        :param do_compact: whether the compaction should be activated or not (default: True)
        :return: self
        """
        self.gcsaws_compaction = do_compact
        return self


class HasFunctionName:
    gcsaws_function_name: str = None

    def function_name(self: T, name: str) -> T:
        """
        Sets the name of the function called by the node.
        :param name: function's name
        :return: self
        """
        self.gcsaws_function_name = name
        return self


class HasPayload:
    gcsaws_payload: dict = None

    def payload(self: T, payload: dict) -> T:
        """
        Sets the payload of the node.
        :param payload: the payload dictionary
        :return: self
        """
        self.gcsaws_payload = payload
        return self


class HasInstanceState:
    gcsaws_instance_state: str = None

    def power_on(self: T) -> T:
        """
        Mark the wanted state as "running"
        :return: self
        """
        self.gcsaws_instance_state = 'running'
        return self

    def power_off(self: T) -> T:
        """
        Mark the wanted state as "stopped"
        :return: self
        """
        self.gcsaws_instance_state = 'stopped'
        return self


# </editor-fold>

# <editor-fold desc="Traits for children">

class AcceptChildWait:
    def wait(self: HasChildren, name: str) -> NodeWait:
        """
        Waits a certain amount of seconds before continuing the execution.
        :param name: node's name
        :return: the child node wait
        """
        return add_child(self, NodeWait, name=name)


class AcceptChildPause:
    def pause(self: HasChildren, name: str) -> NodePause:
        """
        Waits for the user to resume the automation.
        :param name: node's name
        :return: the child node pause
        """
        return add_child(self, NodePause, name=name)


class AcceptChildRunInOrder:
    def run_in_order(self: HasChildren, name: str) -> NodeRunInOrder:
        """
        Starts a new in order procedure part.
        :param name: node's name
        :return: the child node
        """
        return add_child(self, NodeRunInOrder, name=name)


class AcceptChildRunInParallel:
    def run_in_parallel(self: HasChildren, name: str) -> NodeRunInParallel:
        """
        Starts a new parallelized nodes procedure part.
        :param name: node's name
        :return: the child node
        """
        return add_child(self, NodeRunInParallel, name=name)


class AcceptChildScript:
    def run_script(self: HasChildren, name: str) -> NodeScript:
        """
        Runs a script on the given servers.
        :param name: node's name
        :return: the child node
        """
        return add_child(self, NodeScript, name=name)


class AcceptChildScriptTemplate:
    def run_script_template(self: HasChildren, name: str) -> NodeScriptTemplate:
        """
        Renders the script command and runs it on the servers.
        :param name: node's name
        :return: the child node
        """
        return add_child(self, NodeScriptTemplate, name=name)


class AcceptChildStepFunction:
    def run_step_function(self: HasChildren, name: str) -> NodeStepFunction:
        """
        Run a step function.
        :param name: node's name
        :return: the child node
        """
        return add_child(self, NodeStepFunction, name=name)


class AcceptChildChangeInstanceState:
    def change_instance_state(self: HasChildren, name: str) -> NodeChangeInstanceState:
        """
        Power on or off the targets.
        :param name: node(s name
        :return: the child node
        """
        return add_child(self, NodeChangeInstanceState, name=name)


class AcceptChildProcedure:
    def child_procedure(self: AcceptAnonymousChild, procedure_file: str, context: BaseContext):
        """
        Include the procedure in the parent procedure.
        :param procedure_file: the procedure generator
        :param context: the generation context
        """
        name = str(random.randint(0, 1_000_000_000))
        proc = import_module(name, procedure_file).main(context)
        self.child(proc)


# </editor-fold>

# <editor-fold desc="Nodes">
class _ComposedNode(
    BaseNode,
    HasName,
    HasDescription,
    HasChildren,
    AcceptAnonymousChild,
    AcceptMerge,
    AcceptChildWait,
    AcceptChildPause,
    AcceptChildRunInOrder,
    AcceptChildRunInParallel,
    AcceptChildScript,
    AcceptChildScriptTemplate,
    AcceptChildStepFunction,
    AcceptChildChangeInstanceState,
    AcceptChildProcedure
):
    pass


class NodeRunInParallel(_ComposedNode):
    __visitor_method__ = 'visit_run_in_parallel'


class NodeRunInOrder(_ComposedNode):
    __visitor_method__ = 'visit_run_in_order'


class NodeWait(
    BaseNode,
    HasName,
    HasDescription,
    HasDurationSeconds
):
    __visitor_method__ = 'visit_wait'


class NodePause(
    BaseNode,
    HasName,
    HasDescription,
    HasIdentifier
):
    __visitor_method__ = 'visit_pause'


class NodeScript(
    BaseNode,
    HasName,
    HasDescription,
    HasScriptType,
    HasCommand,
    HasTargets,
    HasCompaction
):
    __visitor_method__ = 'visit_script'


class NodeScriptTemplate(
    BaseNode,
    HasName,
    HasDescription,
    HasScriptType,
    HasCommand,
    HasTargets,
    HasCompaction
):
    __visitor_method__ = 'visit_script_template'


class NodeStepFunction(
    BaseNode,
    HasName,
    HasDescription,
    HasFunctionName,
    HasPayload
):
    __visitor_method__ = 'visit_step_function'


class NodeChangeInstanceState(
    BaseNode,
    HasName,
    HasDescription,
    HasTargets,
    HasInstanceState
):
    __visitor_method__ = 'visit_change_instance_state'

# </editor-fold>
