import json
import unittest
from pathlib import Path

import jinja2

from gcsaws.nodes import *
from gcsaws.visitor_procedure import VisitorStateProcedure, setup_procedure_visitor
from gcscore import CommandRenderer, ScriptTemplatesExtension
from gcscore.mod import Visitor, BaseContext, SearchableList, import_module


class TestGCSAws(unittest.TestCase):
    def test_simple(self):
        # Build procedure
        root = NodeRunInOrder(name='root').description('Root procedure')
        root.wait('wait_something').description('Wait for something to happen').duration(15)

        sub_proc = root.run_in_parallel('do_async_things').description('Do somethings in parallel.')
        sub_proc.pause('do_pause').identifier('pauseX')
        sub_proc.wait('hello').duration(15)

        sub_proc2 = NodeRunInOrder(name='sub2')
        sub_proc2.wait('XOXO').duration(5)
        root.child(sub_proc2)

        # Visit
        visitor_state = VisitorStateProcedure(None, None)  # NOQA
        visitor = Visitor()
        setup_procedure_visitor(visitor)
        visitor.visit(root, visitor_state)
        final = visitor_state.root[0]
        pass

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
        visitor_state = VisitorStateProcedure(cmd_renderer, j2env)
        visitor = Visitor()
        setup_procedure_visitor(visitor)
        visitor.visit(root, visitor_state)
        final = visitor_state.root[0]

        self.assertEqual(0, len(cmd_renderer.errors_history))
        pass

    def test_proc_file(self):
        targets = SearchableList([{'name': 'vm01'}, {'name': 'vm02'}, {'name': 'vm03'}])
        messaging = {
            'to': ['me@me.com'],
            'from': 'no-reply@me.com',
            'context': {
                'client': 'ME',
                'environment': 'sbx'
            }
        }
        context = BaseContext(
            {'messaging': messaging, 'pause_before_start': False, 'pause_before_end': False},
            targets
        )

        proc_module = import_module('__imported_proc__', 'data/proc01.py')
        proc = proc_module.main(context)

        cmd_renderer = CommandRenderer()
        ScriptTemplatesExtension.configure(cmd_renderer)
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader('data'), extensions=[ScriptTemplatesExtension])
        visitor_state = VisitorStateProcedure(cmd_renderer, j2env)
        visitor = Visitor()
        setup_procedure_visitor(visitor)
        visitor.visit(proc, visitor_state)
        cmd_renderer.errors_history.render()
        final = visitor_state.root[0]
        Path('data/proc01.json').write_text(json.dumps(final, indent=4))
        pass

    def test_ultra_simple(self):
        node = NodeWait(name='test')
