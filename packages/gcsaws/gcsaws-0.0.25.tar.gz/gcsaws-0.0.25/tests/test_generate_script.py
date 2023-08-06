import unittest
from pathlib import Path

import jinja2
from gcscore import CommandRenderer, ScriptTemplatesExtension
from gcscore.mod import Visitor, BaseContext, SearchableList

from gcsaws.nodes import *
from gcsaws.visitor_save_scripts import VisitorStateSaveScripts, setup_visitor_save_script


class TestScriptGeneration(unittest.TestCase):
    def test_script_template(self):
        context = BaseContext({}, SearchableList([{'name': 'vm01'}]))

        targets = context.targets.select_by_name('vm01')
        root = NodeRunInOrder(name='root')
        root.run_script('test1').shell().command('echo "Hello world!"').on_targets(targets)
        root.run_script_template('test2').command('script01.sh Robin').shell().on_targets(targets)
        root.run_script_template('test3').command('script01.sh Robin').shell().on_targets([])

        cmd_renderer = CommandRenderer()
        ScriptTemplatesExtension.configure(cmd_renderer)
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader('data'), extensions=[ScriptTemplatesExtension])
        visitor_state = VisitorStateSaveScripts(Path('output/test_script_generation'), cmd_renderer, j2env)
        visitor = Visitor()
        setup_visitor_save_script(visitor)
        visitor.visit(root, visitor_state)

        self.assertEqual(0, len(cmd_renderer.errors_history))
        pass
