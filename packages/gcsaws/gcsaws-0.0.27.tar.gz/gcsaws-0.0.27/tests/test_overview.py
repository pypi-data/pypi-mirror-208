import json
import unittest
from pathlib import Path

import jinja2

from gcsaws.nodes import *
from gcscore import CommandRenderer, ScriptTemplatesExtension
from gcscore.mod import Visitor, BaseContext, SearchableList, import_module
from gcsaws.visitor_save_scripts import VisitorStateSaveScripts, setup_visitor_save_script
from gcsaws.visitor_overview import VisitorStateOverview, setup_visitor_overview


class TestGCSAws(unittest.TestCase):
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
            {'messaging': messaging, 'pause_before_start': True, 'pause_before_end': False},
            targets
        )

        proc_module = import_module('__imported_proc__', 'data/proc01.py')
        proc = proc_module.main(context)

        cmd_renderer = CommandRenderer()
        ScriptTemplatesExtension.configure(cmd_renderer)
        j2env = jinja2.Environment(loader=jinja2.FileSystemLoader('data'), extensions=[ScriptTemplatesExtension])

        visitor_state = VisitorStateSaveScripts(Path('output/test_script_generation'), cmd_renderer, j2env)
        visitor = Visitor()
        setup_visitor_save_script(visitor)
        visitor.visit(proc, visitor_state)

        visitor_state = VisitorStateOverview('data', 'test_proc01')
        visitor = Visitor()
        setup_visitor_overview(visitor)
        visitor.visit(proc, visitor_state)
        result = visitor_state.export_html()
        Path('data/proc01.overview.html').write_text(result, encoding='utf-8')
