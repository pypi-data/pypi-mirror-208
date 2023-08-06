import unittest
from gcsaws import *

from gcscore.mod import Visitor
from gcsaws.visitor_validation import VisitorStateValidation, setup_validation_visitor


class TestErrorLogging(unittest.TestCase):
    def test_valid_proc(self):
        proc = new_procedure('test')
        proc.wait('test_wait')

        rip = proc.run_in_parallel('X')
        rip.pause('A').identifier('ABC')

        # Validation
        visitor = Visitor()
        visitor_state = VisitorStateValidation()
        setup_validation_visitor(visitor)
        visitor.visit(proc, visitor_state)  # Should not raise any error

    def test_invalid_proc(self):
        proc = new_procedure('invalid_proc')
        proc.wait('invalid_wait').duration(-5)
        proc.pause('4651d=)àç')
        proc.run_step_function('my_sf')

        rip = proc.run_in_parallel('blah')
        rip.run_script('booya')
        rip.change_instance_state('madara!!!')

        # Validation
        visitor = Visitor()
        visitor_state = VisitorStateValidation(only_log_errors=True)
        setup_validation_visitor(visitor)
        visitor.visit(proc, visitor_state)
