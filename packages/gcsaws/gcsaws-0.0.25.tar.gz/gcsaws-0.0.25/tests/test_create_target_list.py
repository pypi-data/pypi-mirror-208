import json
import unittest
from pathlib import Path

from gcsaws.helpers import create_target_list, TargetFieldQuery


class TestCreateTargetList(unittest.TestCase):
    def test_01(self):
        data = json.loads(Path('data/targets.json').read_text())
        mapping = [
            TargetFieldQuery('id', '$.InstanceId'),
            TargetFieldQuery('name', '$.Tags[?(@.Key=="Name")].Value'),
            TargetFieldQuery('root_volume', '$.BlockDeviceMappings[?(@.DeviceName=="/dev/sda1")].Ebs.VolumeId')
        ]

        targets = create_target_list(data, mapping)
        expected = [
            {'id': '64523163', 'name': 'vm01', 'root_volume': None},
            {'id': '65134653', 'name': None, 'root_volume': 'string'}
        ]
        self.assertEqual(expected, targets)
